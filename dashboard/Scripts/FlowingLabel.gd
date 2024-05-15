extends Control

@export var text: String = "+1";
@export var text_scale: float = 1.0;
@export var color: Color = Color.WHITE;
@export var direction: Vector2 = Vector2.UP;
@onready var shifter = $Shifter;
@onready var label = $Shifter/Center/Label;

const DURATION: float = 2.0;
const DRIFT_LENGTH: float = 75.0;
const DRIFT_ROTATION_RANGE: float = PI / 8.0;
const DRIFT_SCALE: float = 0.6;

func _ready():
	self.label.text = text;
	if self.text_scale != 1.0:
		self.label.add_theme_font_size_override("font_size", self.label.get_theme_font_size("font_size") * self.text_scale);
	self.modulate = self.color;
	
	# Update label size to fit text
	self.label.reset_size()
	
	# Determine shift amount and add randomized rotation
	var shift = DRIFT_LENGTH * self.direction.normalized();
	var shift_rotation = randf_range(-DRIFT_ROTATION_RANGE, DRIFT_ROTATION_RANGE);
	shift = shift.rotated(shift_rotation);
	
	# Shift label to account for own size
	var offset = self.label.get_size() / 2.0 * self.direction.normalized();
	self.shifter.position += offset;
	
	# Calcualte target value for some tweeners
	var color_hidden = self.color;
	color_hidden.a = 0;
	
	# Animate
	var tween = self.create_tween();
	tween.tween_property(self, "modulate", color_hidden, DURATION);
	tween.parallel().tween_property(self.shifter, "position", self.shifter.position + shift, DURATION);
	tween.parallel().tween_property(self.shifter, "scale", self.shifter.scale * DRIFT_SCALE, DURATION);
	tween.tween_callback(self.queue_free);
