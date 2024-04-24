

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
  log_message(event);
  update_table(event);
};

function log_message(event){
  var data = JSON.parse(event.data);
  var table = document.getElementById("logtable");
  let row = table.insertRow(-1);

  let c1 = row.insertCell(0);
  let c2 = row.insertCell(1);
  let c3 = row.insertCell(2);
  let c4 = row.insertCell(3);
  
  console.log(data.data)
  if(data.data.bought != null){
    c2.innerText = data.data.bought.amount + 'x ' +data.data.bought.item.name;
  }else{
    c2.innerText = "";
  };
  c1.innerText = data.data.player.name;
  c3.innerText = items_to_string(data.data.costs);
  c4.innerText= data.data.log;

};

function update_table(event){
  var data = JSON.parse(event.data)
  if(data.data.bought == null){
    var td_amount = document.getElementById(data.data.player.team + '_' + Object.values(data.data.costs)[0].currency);
    cur_amount = parseInt(td_amount.innerText);
    cur_amount += Object.values(data.data.costs)[0].amount;
    td_amount.innerText = cur_amount;
  }
};

// TODO: update chart data on message_received
function update_chart(event){
  

  // c.data.datasets[0].data = player_item_data
  c.update()

}


function items_to_string(items, newline=true){
  let retstr = "";
  for(item in items){
    retstr += items[item].amount + " " + items[item].name;
    if(newline){
      retstr += '\n';
    }
  }
  return retstr
}

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
        beginAtZero: true,
        stacked: true
      }
    }
  }
});

var player_item_data = {}


set_teams();
