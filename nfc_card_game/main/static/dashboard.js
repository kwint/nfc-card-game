const ctx = document.getElementById('myChart')

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
  update_chart(event);
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
    var td_amount = document.getElementById(data.data.player.team +  '_' + Object.values(data.data.costs)[0].currency);
    cur_amount = parseInt(td_amount.innerText);
    cur_amount += Object.values(data.data.costs)[0].amount;
    td_amount.innerText = cur_amount;
  }
};


function update_chart(event){
  var data = JSON.parse(event.data)
  
  if(data.data.bought == null){
    var datasetIndex = c.data.datasets.findIndex(dataset => dataset.label === Object.values(data.data.costs)[0].post_name)
    console.log(datasetIndex)
    if (datasetIndex !== -1){
      c.data.datasets[datasetIndex].data[0] += Object.values(data.data.costs)[0].amount
      c.update()
    }
  }
};


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
      data: [],
      borderWidth: 1
    }]
  },
  options: {
    scales: {
      x: {
        stacked: false, 
      },
      y: {
        beginAtZero: true,
        stacked: false
      }
    }
  }
});

var player_item_data = {}

function get_color_from_currency(currency) {
  if (currency === 'BLUE') return "rgba(54, 162, 235, 0.5)";
  if (currency === 'RED') return "rgba(255, 99, 132, 0.5)";
  if (currency === 'GREEN') return "rgba(130, 255, 54, 0.5)";
}

function init(){

  var uniqueLabels = new Set();
  var chartData = {
    labels: [],
    datasets: []
  }

  team_info.forEach(team => {
    if(!uniqueLabels.has(team.team)){
      uniqueLabels.add(team.team);
      chartData.labels.push(team.team);
    }
    chartData.datasets.push({
      label: team.mine,
      data: [parseInt(team.mine_amount)],
      backgroundColor: get_color_from_currency(team.currency),
    });
  });
  c.data = chartData;
  c.update()
};

init();
