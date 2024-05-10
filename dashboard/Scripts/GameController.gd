extends Node

@onready var mines = [
  $"../MinersLeft",
  $"../MinersRight",
];

@onready var levels = [
  $"../Viewport/LevelsLeft",
  $"../Viewport/LevelsRight",
];

# Called when the node enters the scene tree for the first time.
func _ready():
	pass # Replace with function body.


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	if randi() % 40 == 0:
		var i = randi() % 2;
		
		var miner_type;
		match randi() % 3:
			0:
				miner_type = Global.MinerType.MINER1;
				self.levels[i].update_value1(self.mines[i].count() + 1);
			1:
				miner_type = Global.MinerType.MINER2;
				self.levels[i].update_value2(self.mines[i].count() + 1);
			_:
				miner_type = Global.MinerType.MINER3;
				self.levels[i].update_value3(self.mines[i].count() + 1);
		
		self.mines[i].add_miner(miner_type);
