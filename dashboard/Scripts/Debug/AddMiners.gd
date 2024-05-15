extends GridContainer

@export var game_controller: Node;
@export var team: Settings.TeamId = Settings.TeamId.TEAM1;

# Called when the node enters the scene tree for the first time.
func _ready():
	$Button1.connect("pressed", add1);
	$Button2.connect("pressed", add2);
	$Button3.connect("pressed", add3);


func add1():
	var amount = $SpinBox1.value;
	game_controller.add_miners(self.team, Settings.MinerType.MINER1, amount, amount, "Mijnwerker");


func add2():
	var amount = $SpinBox2.value;
	game_controller.add_miners(self.team, Settings.MinerType.MINER2, amount, 3 * amount, "Drilboor");


func add3():
	var amount = $SpinBox3.value;
	game_controller.add_miners(self.team, Settings.MinerType.MINER3, amount, 10 * amount, "Bulldozer");
