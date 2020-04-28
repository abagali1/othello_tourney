const PROTOCOL = window.location.protocol === "https:" ? "wss" : "ws";
const PATH = `${PROTOCOL}://${window.location.host}`;


function add_listeners(socket){
    let rCanvas = init(game.black, game.white, 0,0);

    $(window).on('resize', function () {
        rCanvas.resize();
    });

    function mouseOver(event){
        highlight_tile(rCanvas, event);
    }

    function clickHandler(event){
        rCanvas.lastClicked = -1;
        place_stone(rCanvas, event);
    }

    $(document).on('mousemove', mouseOver);

    $("#downloadModal")
        .on('show.bs.modal', function () {
            $("#prettyHistory").text(generate_pretty_history());
            $("#parseableHistory").text(generate_parseable_history());
            $(document).off('mousemove');
            $(document).off('click');
        })
        .on('hide.bs.modal', function () {
            $(document).on('mousemove', mouseOver);
            $(document).on('click', clickHandler);
            $("#downloadHistoryButton").click(function () {
                $("#downloadModal").modal('show');
            });
        });

    $("#pretty_download")
        .click(function () {
            download(`${rCanvas.black_name}_${rCanvas.white_name}.txt`, $("#prettyHistory").text());
        });

    $("#parseable_download")
        .click(function () {
            download(`${rCanvas.black_name}_${rCanvas.white_name}_formatted.txt`, $("#parseableHistory").text());
        });

    socket.onopen = () => {
        console.log("socket is connected");
        $(document).on('click', clickHandler);
    };

    socket.onclose = function () {
        console.log("disconnected from socket");
0    };

    socket.onmessage = function (message) {
        let data = JSON.parse(message.data);
        switch(data.type){
            case 'game.log':
                console.log(`LOG: ${data.message}`);
                break;
            case 'game.update':
                if(data.moves[0].tile === -10){
                    console.log("starting game");
                    rCanvas.black_name = data.black;
                    rCanvas.white_name = data.white;
                    console.log(JSON.stringify(data))
                    drawBoard(rCanvas, data.moves[0].board, data.moves[0].possible, BLACK_NM, rCanvas.animArray);
                }else{
                    console.log(data.moves[0])
                }
                HISTORY = data.moves;
                break
            default:
                console.error(`Invalid message type: ${data.type}`);
                return;
        }
    }
}


window.onload = function () {
    on_load();
    let socket;
    socket = is_watching ? new WebSocket(`${PATH}/watch/${game.id}`) : new WebSocket(`${PATH}/play/${game.id}`);
    add_listeners(socket);
};