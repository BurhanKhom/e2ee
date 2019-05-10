var socket = io.connect('http://' + document.domain + ':' + location.port);
socket.on('connect', function() {
    socket.emit('my event', {data: 'I\'m connected!'});
});
socket.on('connect', function(){
  $.getJSON("https://jsonip.com?callback=?", function(data) {
    $("#linfo").append("<p>IP: "+data.ip+" Connected!</p>")
  });
});

socket.on('message', function(msg){

  $.getJSON("https://jsonip.com?callback=?", function(data) {
    var m = '<div class = "bubble"><div style="font-size:10px">'+data.ip+'</div>'+msg+'</div><br>'
    $("#message").append(m)
    var element = document.getElementById("message");
    element.scrollTop = element.scrollHeight;
  });
});

socket.on('join', function(){
  console.log("User connected")
});

$('#msgInput').keypress(function(e){
  var key = e.which
  if(key == 13)
  {
    socket.send($("#msgInput").val())
    console.log($("#msgInput").val())
    $("#msgInput").val('')
  }

});
