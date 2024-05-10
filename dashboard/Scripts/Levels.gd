extends HBoxContainer

const ORIGIN: float = 0.5;

@export var value1: float = 0.0;
@export var value2: float = 0.0;
@export var value3: float = 0.0;

@onready var levels = [
	$Level1,
	$Level2,
	$Level3,
];


func _ready():
	pass


func update_levels():
	var values = [
		self.value1,
		self.value2,
		self.value3,
	];
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


func update_value1(value):
	self.value1 = value;
	self.update_levels();


func update_value2(value):
	self.value2 = value;
	self.update_levels();


func update_value3(value):
	self.value3 = value;
	self.update_levels();
