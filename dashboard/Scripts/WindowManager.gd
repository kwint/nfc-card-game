extends Node


func _ready():
	# Switch to full screen by default if desired
	if Settings.is_default_fullscreen():
		self.switch_to_fullscreen.call_deferred();


func _process(_delta):
	if Input.is_action_just_pressed("quit"):
		self.quit();
		return;
	if Input.is_action_just_pressed("toggle_fullscreen"):
		self.toggle_fullscreen();
		return;


func _notification(what):
	if what == NOTIFICATION_WM_CLOSE_REQUEST:
		self.quit();
		
		
func quit():
	self.get_tree().quit();


func toggle_fullscreen():
	if DisplayServer.window_get_mode() != DisplayServer.WINDOW_MODE_WINDOWED:
		self.switch_to_windowed();
	else:
		self.switch_to_fullscreen();


func switch_to_windowed():
	DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_WINDOWED);


func switch_to_fullscreen():
	DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_EXCLUSIVE_FULLSCREEN);
