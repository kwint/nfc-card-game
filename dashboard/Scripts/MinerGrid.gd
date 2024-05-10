extends Node2D

const MINER_PREFAB = preload("res://Scenes/Miner.tscn");

@export var flipped: bool;
@export var color: Color = Color.WHITE;
@export var reference_grid: Control;

var miners = [];
var noise = FastNoiseLite.new()


func _ready():
	get_viewport().connect("size_changed", reposition_miners, CONNECT_DEFERRED);


func _process(_delta):
	pass
	

func add(type: Global.MinerType = Global.MinerType.MINER1):
	var miner = MINER_PREFAB.instantiate();
	miner.position = self.get_miner_position(self.miners.size());
	
	if self.flipped:
		miner.scale.x *= -1;
		
	if self.color != null:
		miner.modulate = self.color;
	
	self.miners.append(miner);
	
	miner.type = type;
	
	self.add_child(miner);
	
	
func count() -> int:
	return self.miners.size();
	
	
func reposition_miners():
	for i in range(self.miners.size()):
		var miner = self.miners[i];
		miner.position = self.get_miner_position(i);


func get_miner_position(index: int) -> Vector2:
	if self.reference_grid == null:
		return Vector2.ZERO;
	
	var rect = self.reference_grid.get_global_rect();
	
	var diagnal_position_factor = self.noise.get_noise_1d(float(index) * 100.0);
	diagnal_position_factor = scale_float(diagnal_position_factor, -1.0, 1.0, 0.0, 1.0);
	
	var offset = rect.size * diagnal_position_factor;
	# TODO: invert x, do this in a different way?
	if !self.flipped:
		offset.x = abs(offset.x - rect.size.x);
	
	var horizontal_shift = self.noise.get_noise_1d(float(index) * 38.123);
	horizontal_shift = scale_float(horizontal_shift, -1.0, 1.0, -0.5, 0.5);
	offset.x += rect.size.x * horizontal_shift;
	
	return rect.position + offset;


func scale_float(value: float, from_min: float, from_max: float, to_min: float, to_max: float) -> float:
	value = clampf(value, from_min, from_max);
	
	var from_diff = from_max - from_min;
	var to_diff = to_max - to_min;
	var factor = (value - from_min) / from_diff;
	
	return to_min + to_diff * factor;
