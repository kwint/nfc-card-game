extends MarginContainer

const FLOWING_LABEL_PREFAB = preload("res://Scenes/FlowingLabel.tscn");
const FLOWING_LABEL_MARGIN = 30.0;
const MONEY_PREFIX: String = "$";

@export var right = false;
@onready var label = $Label;
@onready var parent = self.get_parent();

var money: int = 0;


func _ready():
	self.set_money(0);


func set_money(money: int, flowing_label: bool = true) -> void:
	var diff = money - self.money;
	var positive = diff > 0;
	
	self.money = money;
	self.label.text = MONEY_PREFIX + str(money);

	# Spawn flow label
	if flowing_label && diff != 0:
		var label_direction = Vector2.RIGHT if !self.right else Vector2.LEFT;
		var rect = self.label.get_global_rect();
		var label_position = rect.position + (rect.size * Vector2(0, 0.5));
		if !self.right:
			label_position += rect.size * Vector2(1, 0);
		label_position += label_direction * FLOWING_LABEL_MARGIN;
		
		self.spawn_flowing_label(
			str("+ ", MONEY_PREFIX, diff) if positive else str("- ", MONEY_PREFIX, abs(diff)),
			Color.GREEN if positive else Color.RED,
			label_position,
			label_direction,
		);

func spawn_flowing_label(text: String, color: Color, label_position: Vector2, label_direction: Vector2):
	var flowing_label = FLOWING_LABEL_PREFAB.instantiate();
	flowing_label.text = text;
	flowing_label.color = color;
	flowing_label.direction = label_direction;
	
	self.parent.add_child(flowing_label);
	flowing_label.global_position = label_position;
