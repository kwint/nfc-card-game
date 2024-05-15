extends Node


func _process(_delta):
	if Input.is_action_just_pressed("quit"):
		self.quit();
		return;


func _notification(what):
	if what == NOTIFICATION_WM_CLOSE_REQUEST:
		self.quit();
		
		
func quit():
	self.get_tree().quit();
