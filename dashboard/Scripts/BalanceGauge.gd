extends Container

const ORIGIN: float = 0.5;
const GAUGE_BASE_COLOR: Color = Color.WHITE;
const GAUGE_GOOD_COLOR: Color = Color.GREEN;
const GAUGE_BAD_COLOR: Color = Color.RED;
const GAUGE_GOOD_DELTA_MAX: float = 0.1;
const GAUGE_BAD_LOWEST: float = 0.1;
const GAUGE_BAD_HIGHEST: float = 0.35;

@export var values = {
	Settings.MinerType.MINER1: 0,
	Settings.MinerType.MINER2: 0,
	Settings.MinerType.MINER3: 0,
};
@onready var containers = {
	Settings.MinerType.MINER1: $Gauge1,
	Settings.MinerType.MINER2: $Gauge2,
	Settings.MinerType.MINER3: $Gauge3,
};
@onready var levels = {
	Settings.MinerType.MINER1: $Gauge1/Gauge,
	Settings.MinerType.MINER2: $Gauge2/Gauge,
	Settings.MinerType.MINER3: $Gauge3/Gauge,
};


func _ready():
	pass


func update_levels():
	var miner_types = self.levels.keys();
	var sum = self.values.values().map(func(n): return float(n)).reduce(func(a, b): return a + b);
	var avg = sum / 3.0;
	
	# Calculate deltas to determine proportions
	var deltas = {}
	for miner_type in miner_types:
		deltas[miner_type] = float(self.values[miner_type]) - avg;
	var delta_max = deltas.values().max();
	var delta_scale = delta_max / avg;
	if is_nan(delta_scale):
		delta_scale = 0.0;
	
	# Determine offsets between [-1, 1], scale them to gauge range
	var offsets = {
		Settings.MinerType.MINER1: 0.0,
		Settings.MinerType.MINER2: 0.0,
		Settings.MinerType.MINER3: 0.0,
	};
	if delta_max > 0.0:
		for miner_type in miner_types:
			offsets[miner_type] = deltas[miner_type] / delta_max * delta_scale;
	
	# Update gauges
	for miner_type in miner_types:
		var value = ORIGIN + offsets[miner_type] / 2.0;
		self.levels[miner_type].value = value;
		
		# Color gauges to hint good/bad state
		# - Turn red in the range [0.1, 0.35]
		# - Turn green when maximum delta is within 10%
		var color = GAUGE_BASE_COLOR;
		if sum > 0:
			if value < GAUGE_BAD_HIGHEST:
				color = GAUGE_BAD_COLOR.lerp(GAUGE_BASE_COLOR, Helpers.scale_float(value, GAUGE_BAD_LOWEST, GAUGE_BAD_HIGHEST, 0.0, 1.0));
			elif delta_scale < GAUGE_GOOD_DELTA_MAX:
				color = GAUGE_GOOD_COLOR.lerp(GAUGE_BASE_COLOR, Helpers.scale_float(delta_scale, 0.0, GAUGE_GOOD_DELTA_MAX, 0.0, 1.0));
		self.containers[miner_type].modulate = color;


func add_levels(type: Settings.MinerType, amount: int = 1):
	self.values[type] += amount;
	self.update_levels();


func set_level(type: Settings.MinerType, amount: int):
	self.values[type] = amount;
	self.update_levels();
