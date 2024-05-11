extends HBoxContainer

const ORIGIN: float = 0.5;

@export var values = {
	Global.MinerType.MINER1: 0,
	Global.MinerType.MINER2: 0,
	Global.MinerType.MINER3: 0,
};
@onready var levels = {
	Global.MinerType.MINER1: $Gauge1,
	Global.MinerType.MINER2: $Gauge2,
	Global.MinerType.MINER3: $Gauge3,
};


func _ready():
	pass


func update_levels():
	var miner_types = self.levels.keys();
	var avg = self.values.values().map(func(n): return float(n)).reduce(func(a, b): return a + b) / 3.0;
	
	# Calculate deltas to determine proportions
	var deltas = {}
	for miner_type in miner_types:
		deltas[miner_type] = float(self.values[miner_type]) - avg;
	var delta_max = deltas.values().max();
	var delta_scale = delta_max / avg;
	
	# Determine offsets between [-1, 1], scale them to gauge range
	var offsets = {
		Global.MinerType.MINER1: 0.0,
		Global.MinerType.MINER2: 0.0,
		Global.MinerType.MINER3: 0.0,
	};
	if delta_max > 0.0:
		for miner_type in miner_types:
			offsets[miner_type] = deltas[miner_type] / delta_max * delta_scale;
	
	# Update gauges
	for miner_type in miner_types:
		self.levels[miner_type].value = ORIGIN + offsets[miner_type] / 2.0;


func add(type: Global.MinerType):
	self.values[type] += 1;
	self.update_levels();


func set_level(type: Global.MinerType, amount: int):
	self.values[type] = amount;
	self.update_levels();
