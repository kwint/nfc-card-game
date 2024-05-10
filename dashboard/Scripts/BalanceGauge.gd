extends HBoxContainer

const ORIGIN: float = 0.5;

@export var values = [
	0,
	0,
	0,
];

@onready var levels = [
	$Gauge1,
	$Gauge2,
	$Gauge3,
];


func _ready():
	pass


func update_levels():
	var values = self.values.map(func(n): return float(n));
	var avg = values.reduce(func(a, b): return a + b) / 3.0;
	var deltas = values.map(func(n): return n - avg);
	var delta_max = deltas.max();
	var delta_scale = delta_max / avg;
	
	# Determine offsets between [-1, 1], scale them
	var offsets = [0.0, 0.0, 0.0];
	if delta_max > 0.0:
		offsets = deltas.map(func(n): return n / delta_max * delta_scale);
	
	for i in range(self.levels.size()):
		self.levels[i].value = ORIGIN + offsets[i] / 2.0;


func add(type: Global.MinerType):
	var i = Global.miner_type_index(type);
	self.values[i] += 1;
	self.update_levels();
