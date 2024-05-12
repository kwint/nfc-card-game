extends MarginContainer

const FLOWING_LABEL_PREFAB = preload("res://Scenes/FlowingLabel.tscn");
const FLOWING_LABEL_MARGIN = 30.0;
const MONEY_PREFIX: String = "$";
const FLASH_ANIMATION_LENGTH: float = 0.4;
const COLOR_POSITIVE: Color = Color.GREEN;
const COLOR_NEGATIVE: Color = Color.RED;

@export var right: bool = false;
@onready var label = $Label;
@onready var parent = self.get_parent();
@onready var default_modulate: Color = self.modulate;
@onready var flash_tween: Tween;

var money: int = 0;


func _ready():
	self.set_money(0);


func set_money(money: int, animate: bool = true) -> void:
	var diff = money - self.money;
	var positive = diff > 0;
	
	# Update label
	self.money = money;
	self.label.text = MONEY_PREFIX + str(money);

	# Animations
	if animate && diff != 0:
		self.animate_flash(positive);
		self.animate_flowing_label(diff);


func animate_flash(positive: bool):
	self.modulate = COLOR_POSITIVE if positive else COLOR_NEGATIVE;
	if self.flash_tween != null && self.flash_tween.is_valid():
		self.flash_tween.kill();
	self.flash_tween = self.create_tween();
	self.flash_tween.tween_property(self, "modulate", self.default_modulate, FLASH_ANIMATION_LENGTH);


func animate_flowing_label(diff: int):
	# Detemrine label parameters
	var positive = diff > 0;
	var text = str("+ ", MONEY_PREFIX, diff) if positive else str("- ", MONEY_PREFIX, abs(diff));
	var color = COLOR_POSITIVE if positive else COLOR_NEGATIVE;
	var label_direction = Vector2.RIGHT if !self.right else Vector2.LEFT;
	var rect = self.label.get_global_rect();
	var label_position = rect.position + (rect.size * Vector2(0, 0.5));
	if !self.right:
		label_position += rect.size * Vector2(1, 0);
	label_position += label_direction * FLOWING_LABEL_MARGIN;
	
	# Instantiate label
	var flowing_label = FLOWING_LABEL_PREFAB.instantiate();
	flowing_label.text = text;
	flowing_label.color = color;
	flowing_label.direction = label_direction;
	self.parent.add_child(flowing_label);
	flowing_label.global_position = label_position;
