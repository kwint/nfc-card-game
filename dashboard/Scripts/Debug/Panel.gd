extends PanelContainer


func _ready():
	self.visible = Settings.is_show_debug();
