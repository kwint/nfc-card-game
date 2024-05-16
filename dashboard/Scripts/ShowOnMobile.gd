extends CanvasItem


func _ready():
	if !Settings.is_mobile():
		self.visible = false;
		self.queue_free();
