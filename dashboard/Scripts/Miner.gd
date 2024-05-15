extends Node2D

const FLASH_DURATION: float = 1.0;
const FLASH_COLOR: Color = Color.GREEN;

@export var type: Settings.MinerType = Settings.MinerType.MINER1;
@export var color: Color = Color.WHITE;
@export var animate: bool = true;

@onready var sprite = $Sprite;

# Called when the node enters the scene tree for the first time.
func _ready():
	self.update_miner_type(self.type);
	self.sprite.modulate = self.color;
	
	# Animate flash
	if self.animate:
		var tween = self.create_tween();
		tween.tween_property(self.sprite, "modulate", self.sprite.modulate, 1.0);
		self.sprite.modulate = FLASH_COLOR;


func update_miner_type(type: Settings.MinerType):
	match type:
		Settings.MinerType.MINER1:
			self.sprite.animation = "miner1";
		Settings.MinerType.MINER2:
			self.sprite.animation = "miner2";
		Settings.MinerType.MINER3:
			self.sprite.animation = "miner3";
		_:
			assert(false, "unknown miner type");


func destroy():
	if is_instance_valid(self):
		self.queue_free();
