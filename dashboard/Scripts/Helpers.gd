class_name Helpers


static func scale_float(value: float, from_min: float, from_max: float, to_min: float, to_max: float) -> float:
	value = clampf(value, from_min, from_max);
	
	var from_diff = from_max - from_min;
	var to_diff = to_max - to_min;
	var factor = (value - from_min) / from_diff;
	
	return to_min + to_diff * factor;
