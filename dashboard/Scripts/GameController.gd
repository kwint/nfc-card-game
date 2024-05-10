extends Node

@onready var mines = [
  $"../MinersLeft",
  $"../MinersRight",
];

@onready var levels = [
  $"../Viewport/BalanceGaugeLeft",
  $"../Viewport/BalanceGaugeRight",
];


func _ready():
	# Spawn random set of miners on start in debug builds
	if OS.has_feature("debug"):
		for i in range(1 + randi() % 4):
			self.add_miner.call_deferred(true, Global.MinerType.MINER1);
		for i in range(1 + randi() % 4):
			self.add_miner.call_deferred(false, Global.MinerType.MINER1);


func add_miner(left: bool, miner_type: Global.MinerType):
	var i = 0 if left else 1;
	self.mines[i].add(miner_type);
	self.levels[i].add(miner_type);
