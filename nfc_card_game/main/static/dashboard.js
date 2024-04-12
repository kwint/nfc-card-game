

const ctx = document.getElementById('myChart')

// var base_url = "ws://localhost:8000/ws";
var base_url = "ws://"+ window.location.host + "/ws/"
const websocket = new WebSocket('ws://localhost:8000/ws/');

websocket.onopen = function(e){
  console.log("COnnected!");
  websocket.send(JSON.stringify({message: "Hello, server!"}));
};

websocket.onclose = function(event) {
  if (event.wasClean){
    console.log(`Connection closed cleanly, code=${event.code}`)
  }else{
    console.log('Connection died!')
  }
}


websocket.onerror = function(error){
  console.log(`[WebSocket Error] ${error}`);
  console.log(error);
};

websocket.onmessage = function(event){
    var data = JSON.parse(event.data);
    console.log(data)
}

console.log(player_items)
c = new Chart(ctx, {
  type: 'bar',
  data: {
    datasets: [{
      data: player_items[0].fields,
      borderWidth: 1
    }]
  },
  options: {
    scales: {
      y: {
        beginAtZero: true
      }
    }
  }
});

var player_item_data = {}


for(let i = 0; i < player_items.length; i++){
  console.log(player_items[i].fields)
  console.log(Object.keys(player_items[i].fields[0]))
  for(let j = 0; j < player_items[i].fields.length; j++){
    player_item_data[Object.keys(player_items[i].fields[j])] = player_items[i].fields[j]

  }
}

console.log(player_item_data)
c.data.datasets[0].data = player_item_data
c.update()
console.log(c.data)
