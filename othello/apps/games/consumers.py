from typing import Any, Dict, Optional

from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer

from django.utils import timezone

from ...moderator.constants import Player
from .models import Game, GameLog, Submission
from .tasks import run_game
from .utils import serialize_game_error, serialize_game_info, serialize_game_log


class GameConsumer(JsonWebsocketConsumer):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.game: Optional[Game] = None
        self.connected: bool = False

    def connect(self) -> None:
        try:
            self.game = Game.objects.get(id=self.scope["url_route"]["kwargs"]["game_id"])
        except Game.DoesNotExist:
            self.close()
            return

        yourself: Submission = Submission.objects.get(user__username="Yourself")

        if not self.game.playing:
            self.close()
            return

        self.is_black_yourself: bool = self.game.black.id == yourself.id
        self.is_white_yourself: bool = self.game.white.id == yourself.id

        self.connected = True
        self.accept()

        async_to_sync(self.channel_layer.group_add)(self.game.channels_group_name, self.channel_name)

    def disconnect(self, code: int) -> None:
        self.connected = False

    def game_update(self, event: Dict[str, Any]) -> None:
        self.update_game()

    def game_log(self, event: Dict[str, Any]) -> None:
        self.send_log(event["object_id"])

    def game_error(self, event: Dict[str, Any]) -> None:
        self.send_error(event["object_id"])

    def update_game(self) -> None:
        if self.connected:
            self.game.refresh_from_db()
            game = serialize_game_info(self.game)
            self.send_json(game)
            if game["game_over"]:
                self.close()

    def send_log(self, object_id: int) -> None:
        if self.connected:
            self.game.refresh_from_db()
            log: GameLog = self.game.logs.get(id=object_id)
            has_access: bool = log.game.black.user == self.scope["user"] if log.player == Player.BLACK.value else log.game.white.user == self.scope["user"]
            if has_access or (log.player == Player.BLACK.value and self.is_black_yourself) or (log.player == Player.WHITE.value and self.is_white_yourself):
                self.send_json(serialize_game_log(log))

    def send_error(self, object_id: int) -> None:
        if self.connected:
            self.send_json(serialize_game_error(self.game.errors.get(id=object_id)))


class GamePlayingConsumer(GameConsumer):
    def connect(self) -> None:
        super(GamePlayingConsumer, self).connect()
        run_game.delay(self.game.id)

    def disconnect(self, code: int) -> None:
        self.game.playing = False
        self.game.save(update_fields=["playing"])
        super().disconnect(code)

    def receive_json(self, content: Dict[str, Any], **kwargs: Any) -> None:
        self.game.last_heartbeat = timezone.now()
        self.game.save()

        player: str = content.get("player", None)
        try:
            move: int = int(content.get("move", None))
        except (ValueError, TypeError):
            move = None

        if move is not None and player is not None:
            if player == Player.WHITE.value and self.is_white_yourself:
                self.game.moves.create(player=player, move=move)
            elif player == Player.BLACK.value and self.is_black_yourself:
                self.game.moves.create(player=player, move=move)
