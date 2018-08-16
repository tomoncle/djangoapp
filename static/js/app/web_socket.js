/**
 *
 //申请一个WebSocket对象，参数是需要连接的服务器端的地址，同http协议使用http://开头一样，
 // WebSocket协议的URL使用ws://开头，另外安全的WebSocket协议使用wss://开头。
 var ws = new WebSocket('ws://0.0.0.0:10005');

 //当websocket创建成功时，即会触发onopen事件
 ws.onopen = function () {
        console.log('open');
        //用于叫消息发送到服务端
        ws.send('hello');
 };
 //当客户端收到服务端发来的消息时，会触发onmessage事件，参数evt.data中包含server传输过来的数据
 ws.onmessage = function (evt) {
        console.log(evt.data)
        $("#ll").text(evt.data)
 };
 //当客户端收到服务端发送的关闭连接的请求时，触发onclose事件
 ws.onclose = function (evt) {
        console.log('WebSocketClosed!');
 };
 //如果出现连接，处理，接收，发送数据失败的时候就会触发onerror事件
 ws.onerror = function (evt) {
        console.log('WebSocketError!');
 };

 */

/**
 * Created by liyuanjun on 16-9-7.
 *
 * py :
 *  c=Client(message={'security_group%s'%(str(obj.id)),'运行中'})
 *  c.start()
 *
 * page: <td id="rule{{ rule.id }}">创建中</td>
 *
 */
var addr='ws://0.0.0.0:30001';
var WebSocketClient = {
    init: function () {
        var ws = new WebSocket(addr);
        ws.onmessage = function (evt) {
            var data;
            try {
                data=eval('(' + evt.data + ')');
            }catch (e){
                console.log('error:只监听json格式数据,详细信息:'+e);
                return;
            }
            for (var key in data){
                $("#"+key).text(data[key]);
            }
        }
    }
};
WebSocketClient.init();