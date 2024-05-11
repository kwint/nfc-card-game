extends MarginContainer

const MONEY_PREFIX: String = "$ ";

@onready var label = $Label;


func _ready():
	self.set_money(0);


func set_money(money: int) -> void:
	self.label.text = MONEY_PREFIX + str(money);
