extends Node2D

const MINER_PREFAB = preload("res://Prefabs/Miner.tscn");
const FLOWING_LABEL_PREFAB = preload("res://Prefabs/FlowingLabel.tscn");
const FLOWING_LABEL_TEXT_SCALE: float = 0.7;
# Maximum number of miner instances per type
const MAX_RENDERED_MINERS: int = 5_000;
const MINER_HIGHEST_POSITION: float = 0.05;
const MINER_LOWEST_POSITION: float = 0.92;

@export var flipped: bool;
@export var color: Color = Color.WHITE;
@export var animate_color: Color = Color.GREEN;
@export var reference_grid: Control;

# A dict per miner type, containing a list of miner instances.
var miners = {};
# A dict of the number of hidden miners per type.
var miners_hidden = {};

# Random source for miner placement
var random = RandomNumberGenerator.new();
var random_base: int = 0;


func _ready():
	# Pick a random base number for random miner spread
	self.random.randomize();
	self.random_base = self.random.randi() % 999999;
	
	get_viewport().connect("size_changed", reposition_miners, CONNECT_DEFERRED);


# Add the given amount of miners
# The amount rendered on screen may be limited for performance reasons
func add_miners(type: Settings.MinerType = Settings.MinerType.MINER1, amount: int = 1, animate_text = null):
	# Determine how many visible and hidden miners to add
	var add_visible = min(amount, MAX_RENDERED_MINERS);
	var add_hidden = max(amount - add_visible, 0);
	
	# Update the hidden count and add each visible miner
	self._add_hidden_miners(type, add_hidden);
	for _i in range(add_visible):
		self._add_miner(type, animate_text);


# Add a single visible miner instance
func _add_miner(type: Settings.MinerType = Settings.MinerType.MINER1, animate_text = null):
	var miner = MINER_PREFAB.instantiate();
	var miner_position = self.get_miner_position(type, self.count_miners(type));
	
	if self.flipped:
		miner.scale.x *= -1;
	if self.color != null:
		miner.color = self.color;
	
	miner.animate = animate_text != null;
	miner.position = miner_position;
	miner.type = type;
	
	self._add_miner_to_list(type, miner);
	self.add_child(miner);
	
	if animate_text != null:
		var flowing_label = FLOWING_LABEL_PREFAB.instantiate();
		flowing_label.text = animate_text;
		flowing_label.color = self.animate_color;
		flowing_label.text_scale = FLOWING_LABEL_TEXT_SCALE;
		self.add_child(flowing_label);
		flowing_label.position = miner_position;
	

func _add_miner_to_list(type: Settings.MinerType, miner):
	if !self.miners.has(type):
		self.miners[type] = [];
	var miners = self.miners[type];
	
	# List new miner
	miners.append(miner);
	
	# Remove old miners when reaching miner limit
	var overflow = max(miners.size() - MAX_RENDERED_MINERS, 0);
	if overflow > 0:
		for i in range(overflow):
			miners[i].destroy();
		self.miners[type] = miners.slice(overflow, miners.size());
		self._add_hidden_miners(type, overflow);
	

# Add the given number of hidden miners.
func _add_hidden_miners(type: Settings.MinerType = Settings.MinerType.MINER1, amount: int = 1):
	if !self.miners_hidden.has(type):
		self.miners_hidden[type] = 0;
	self.miners_hidden[type] += amount;
	

# Get the number of hidden miners.
func _get_hidden_miners(type: Settings.MinerType = Settings.MinerType.MINER1) -> int:
	return self.miners_hidden.get(type, 0);


# Remove the given number of miners.
func remove_miners(type: Settings.MinerType = Settings.MinerType.MINER1, amount: int = 1):
	# First remove hidden miners, it is more efficient
	var remove_hidden = min(amount, self._get_hidden_miners(type));
	self._add_hidden_miners(type, -remove_hidden);
	amount -= remove_hidden;
	
	# Remove visible miner instances
	var miners = self.miners[type];
	for _i in range(amount):
		var miner = miners.pop_back();
		if miner == null:
			break;
		miner.destroy();
	
	# Reposition miners if we have removed hidden ones
	if remove_hidden > 0:
		self.reposition_miners();


# Set the given number of miners, automatically adding or removing them as needed.
func set_miners(type: Settings.MinerType, amount: int, animate_text = null):
	var delta = amount - self.count_miners(type);
	if delta > 0:
		self.add_miners(type, delta, animate_text);
	if delta < 0:
		self.remove_miners(type, delta * -1);


# Count the miners of a type
# Returns the true count, including both visible and invisible miners.
func count_miners(type: Settings.MinerType) -> int:
	return self.miners.get(type, []).size() + self.miners_hidden.get(type, 0);


# Reposition all visible miners based on our positioning logic.
func reposition_miners():
	for type in self.miners:
		var miners = self.miners[type];
		var index_offset = self.miners_hidden.get(type, 0);
		for i in range(miners.size()):
			miners[i].position = self.get_miner_position(type, i, index_offset);


func get_miner_position(type: Settings.MinerType, index: int, hidden_amount = null) -> Vector2:
	if self.reference_grid == null:
		return Vector2.ZERO;
	
	# Pick a base seed based on the miner type
	# This prevents overlapping of different miner types
	var base_seed = MAX_RENDERED_MINERS * type + self.random_base;
	self.random.set_seed(base_seed + index);

	# Offset index to prevent position jumps when removing old miners
	if hidden_amount == null:
		hidden_amount = self.miners_hidden.get(type, 0);
	index += hidden_amount;
	
	# Height factor in rectangle [0, 1], slowly spread from center
	var height_factor = self.random.randf_range(MINER_HIGHEST_POSITION, MINER_LOWEST_POSITION);
	if index < 45:
		height_factor = scale_float(height_factor, 0.0, 1.0, max(0.45 - index * 0.01, 0.0), min(0.55 + index * 0.01, 1.0));
	
	# Width factor in rectangle [0, 1], slowly spread from center
	var width_factor = self.random.randf_range(0.0, 1.0);
	if index < 45:
		width_factor = scale_float(width_factor, 0.0, 1.0, max(0.45 - index * 0.01, 0.0), min(0.55 + index * 0.01, 1.0));
	
	# Keep width within rectangle of mountain
	var width_factor_left = 1.0 - height_factor if !self.flipped else 0.0;
	var width_factor_right = 1.0 if !self.flipped else height_factor;
	width_factor = scale_float(width_factor, 0.0, 1.0, width_factor_left, width_factor_right);
	
	# Scale width and height factor to the reference rectangle
	var rect = self.reference_grid.get_global_rect();
	var offset = rect.size * Vector2(width_factor, height_factor);
	return rect.position + offset;


func scale_float(value: float, from_min: float, from_max: float, to_min: float, to_max: float) -> float:
	value = clampf(value, from_min, from_max);
	
	var from_diff = from_max - from_min;
	var to_diff = to_max - to_min;
	var factor = (value - from_min) / from_diff;
	
	return to_min + to_diff * factor;
