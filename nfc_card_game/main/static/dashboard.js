

const ctx = document.getElementById('myChart')

// var base_url = "ws://localhost:8000/ws";
var base_url = "ws://"+ window.location.host + "/ws/"
const websocket = new WebSocket(base_url);

websocket.onopen = function(e){
  console.log("COnnected!");
}

websocket.onmessage = function(event){
    var data = JSON.parse(event.data);
    console.log(data);
    if(data.weather_station == current_station){
      for(var i = 0; i < knobs.length; i++){
        var knob = knobs[i];
        knob.setValue(data.data[knob.getProperty("label")])
      }
      callREST();
    }
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
