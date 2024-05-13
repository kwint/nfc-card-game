extends GridContainer

@export var game_controller: Node;

# Called when the node enters the scene tree for the first time.
func _ready():
	$Button1.connect("pressed", add1);
	$Button2.connect("pressed", add2);
	$Button3.connect("pressed", add3);


func add1():
	game_controller.add_miners(Global.TeamId.TEAM1, Global.MinerType.MINER1, $SpinBox1.value, "+1");


func add2():
	game_controller.add_miners(Global.TeamId.TEAM1, Global.MinerType.MINER2, $SpinBox2.value, "+1");


func add3():
	game_controller.add_miners(Global.TeamId.TEAM1, Global.MinerType.MINER3, $SpinBox3.value, "+1");
