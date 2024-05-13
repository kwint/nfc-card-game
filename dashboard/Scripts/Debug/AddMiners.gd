extends GridContainer

@export var game_controller: Node;

# Called when the node enters the scene tree for the first time.
func _ready():
	$Button1.connect("pressed", add1);
	$Button2.connect("pressed", add2);
	$Button3.connect("pressed", add3);


func add1():
	for i in range($SpinBox1.value):
		game_controller.add_miner(Global.TeamId.TEAM1, Global.MinerType.MINER1, "+1");


func add2():
	for i in range($SpinBox2.value):
		game_controller.add_miner(Global.TeamId.TEAM1, Global.MinerType.MINER2, "+1");


func add3():
	for i in range($SpinBox3.value):
		game_controller.add_miner(Global.TeamId.TEAM1, Global.MinerType.MINER3, "+1");
