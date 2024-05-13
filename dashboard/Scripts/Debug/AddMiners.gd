extends GridContainer

@export var game_controller: Node;

# Called when the node enters the scene tree for the first time.
func _ready():
	$Button1.connect("pressed", add1);
	$Button2.connect("pressed", add2);
	$Button3.connect("pressed", add3);


func add1():
	var amount = $SpinBox1.value;
	game_controller.add_miners(Global.TeamId.TEAM1, Global.MinerType.MINER1, amount, amount, "+1");


func add2():
	var amount = $SpinBox1.value;
	game_controller.add_miners(Global.TeamId.TEAM1, Global.MinerType.MINER2, amount, 3 * amount, "+1");


func add3():
	var amount = $SpinBox1.value;
	game_controller.add_miners(Global.TeamId.TEAM1, Global.MinerType.MINER3, amount, 10 * amount, "+1");
