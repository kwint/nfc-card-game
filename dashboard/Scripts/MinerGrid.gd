extends Node2D

const MINER_PREFAB = preload("res://Prefabs/Miner.tscn");
const FLOWING_LABEL_PREFAB = preload("res://Prefabs/FlowingLabel.tscn");

@export var flipped: bool;
@export var color: Color = Color.WHITE;
@export var reference_grid: Control;

var miners = {};
var noise = FastNoiseLite.new()


func _ready():
	get_viewport().connect("size_changed", reposition_miners, CONNECT_DEFERRED);


func _process(_delta):
	pass
	

func add_miner(type: Global.MinerType = Global.MinerType.MINER1, animate: bool = true):
	var miner = MINER_PREFAB.instantiate();
	var miner_position = self.get_miner_position(type, self.count_miners(type));
	
	if self.flipped:
		miner.scale.x *= -1;
	if self.color != null:
		miner.color = self.color;
	
	miner.animate = animate;
	miner.position = miner_position;
	miner.type = type;
	
	self._add_miner_to_list(type, miner);
	self.add_child(miner);
	
	if animate:
		var flowing_label = FLOWING_LABEL_PREFAB.instantiate();
		self.add_child(flowing_label);
		flowing_label.position = miner_position;


func remove_miner(type: Global.MinerType = Global.MinerType.MINER1):
	var miner = self.miners[type].pop_back();
	if miner == null:
		return;
	miner.destroy();
	

func _add_miner_to_list(type: Global.MinerType, miner):
	if !self.miners.has(type):
		self.miners[type] = [];
	self.miners[type].append(miner);


func set_miners(type: Global.MinerType, amount: int, animation: bool = false):
	# TODO: do this in batches
	
	var delta = amount - self.count_miners(type);
	
	# Add new miners
	if delta > 0:
		for _i in range(delta):
			self.add_miner(type, animation);
			
	# Remove excess miners
	if delta < 0:
		delta *= -1;
		for _i in range(delta):
			self.remove_miner(type);
	
	
func count_miners(type: Global.MinerType) -> int:
	if !self.miners.has(type):
		return 0;
	return self.miners[type].size();
	
	
func reposition_miners():
	for type in self.miners:
		var miners = self.miners[type];
		for i in range(miners.size()):
			miners[i].position = self.get_miner_position(type, i);


func get_miner_position(type: Global.MinerType, index: int) -> Vector2:
	if self.reference_grid == null:
		return Vector2.ZERO;
	
	var rect = self.reference_grid.get_global_rect();
	
	var diagnal_position_factor = self.noise.get_noise_1d((type * 100000.3) + float(index) * 100.0);
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
