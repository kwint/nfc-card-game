extends PanelContainer


func _ready():
	# Hide panel in non-debug builds
	self.visible = OS.has_feature("debug");
