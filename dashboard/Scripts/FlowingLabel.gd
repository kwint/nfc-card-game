extends Control

@onready var label = $Wrapper/Label;

const DURATION: float = 2.0;
const DRIFT_LENGTH: float = 75.0;
const DRIFT_DIRECTION: Vector2 = Vector2.UP;
const DRIFT_ROTATION_RANGE: float = PI / 8.0;

func _ready():
	# Determine shift amount and add randomized rotation
	var shift = DRIFT_DIRECTION * DRIFT_LENGTH;
	var shift_rotation = randf_range(-DRIFT_ROTATION_RANGE, DRIFT_ROTATION_RANGE);
	shift = shift.rotated(shift_rotation);
	
	# Calculate new label position and hidden color
	var new_pos = label.position + shift;
	var hidden = self.modulate;
	hidden.a = 0;
	
	# Actually animate
	var tween = get_tree().create_tween();
	tween.tween_property(self, "modulate", hidden, DURATION);
	tween.parallel().tween_property(label, "position", new_pos, DURATION);
	tween.tween_callback(self.queue_free)
