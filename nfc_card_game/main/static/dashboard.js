

const ctx = document.getElementById('myChart')

// var base_url = "ws://localhost:8000/ws";
var base_url = "ws://"+ window.location.host + "/ws/"
const websocket = new WebSocket('ws://localhost:8000/ws/');

websocket.onopen = function(e){
  console.log("COnnected!");
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
    console.log(data.data);
    var team_table = document.getElementById("team_table");
    let row = table.insertRow(0);


    var table = document.getElementById("logtable");
    let row = table.insertRow(-1);

    let c1 = row.insertCell(0);
    let c2 = row.insertCell(1);
    let c3 = row.insertCell(2);
    let c4 = row.insertCell(3);
    
    c1.innerText = data.data.player.name;
    c2.innerText = items_to_string(data.data.bought);

  
    c3.innerText = items_to_string(data.data.costs);
    c4.innerText= data.data.log;
}

function items_to_string(items, newline=true){
  // console.log("IMTES");
  // console.log( items);
  let retstr = "";
  for(item in items){
    retstr += items[item] + " " + item;
    if(newline){
      retstr += "\n";
    }
  }
  return retstr;
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
