extends Control

@export var text: String = "+1";
@export var color: Color = Color.GREEN;
@export var direction: Vector2 = Vector2.UP;
@onready var label = $Center/Wrapper/Label;

const DURATION: float = 2.0;
const DRIFT_LENGTH: float = 75.0;
const DRIFT_ROTATION_RANGE: float = PI / 8.0;

func _ready():
	self.label.text = text;
	self.modulate = self.color;
	
	# Determine shift amount and add randomized rotation
	var shift = DRIFT_LENGTH * self.direction;
	var shift_rotation = randf_range(-DRIFT_ROTATION_RANGE, DRIFT_ROTATION_RANGE);
	shift = shift.rotated(shift_rotation);
	
	# Calculate new label position and hidden color
	var new_pos = label.position + shift;
	var color_hidden = self.color;
	color_hidden.a = 0;
	
	# Actually animate
	var tween = get_tree().create_tween();
	tween.tween_property(self, "modulate", color_hidden, DURATION);
	tween.parallel().tween_property(label, "position", new_pos, DURATION);
	tween.tween_callback(self.queue_free)
