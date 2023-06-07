layui.use(['table', 'layer'], function () {
    let $ = layui.jquery;

    function get_box_size() {
        let init_width = 9;
        let init_height = 18;
        let windows_width = $('#terminal').width();
        let windows_height = $(window).height();
        return {
            cols: Math.floor(windows_width / init_width), rows: Math.floor(windows_height / init_height),
        }
    }

    let cols = get_box_size().cols;
    let rows = get_box_size().rows;
    let term = new Terminal({
        cursorBlink: true, rows: rows, cols: cols, useStyle: true,
    });
    term.open(document.getElementById('terminal'));
    // let server_id = '{{ connect.id }}';
    let server_id = $("#instance").val();
    let ws = new WebSocket('ws://' + window.location.host + '/webssh/terminal/?id=' + server_id);
    ws.onopen = function () {
        term.on('data', function (data) {
            let send_data = JSON.stringify({
                'flag': 'entered_key', 'entered_key': data, 'cols': null, 'rows': null
            });
            ws.send(send_data);
        });
        ws.onerror = function (event) {
            console.log('error: ' + event);
        };
        ws.onmessage = function (event) {
            term.write(event.data);
        };
        ws.onclose = function (event) {
            console.log('close: ' + event)
            term.write('\n\r\x1B[1;3;31m连接关闭！\x1B[0m');
        };
    };
    $(window).resize(function () {
        let cols = get_box_size().cols;
        let rows = get_box_size().rows;
        let send_data = JSON.stringify({'flag': 'resize', 'cols': cols, 'rows': rows});
        ws.send(send_data);
        term.resize(cols, rows)
    })
});