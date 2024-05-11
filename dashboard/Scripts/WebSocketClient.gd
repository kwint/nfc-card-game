extends Node

var socket = WebSocketPeer.new()

func _ready():
	socket.connect_to_url(Global.WEBSOCKET_API_URL);

func _process(delta):
	# Keep progressing the socket
	socket.poll()
	
	var state = socket.get_ready_state()
	if state == WebSocketPeer.STATE_OPEN:
		while socket.get_available_packet_count():
			print("Packet: ", socket.get_packet())

	elif state == WebSocketPeer.STATE_CLOSING:
		# Keep polling to achieve proper close.
		pass

	elif state == WebSocketPeer.STATE_CLOSED:
		var code = socket.get_close_code()
		var reason = socket.get_close_reason()
		print("WebSocket closed with code: %d, reason %s. Clean: %s" % [code, reason, code != -1])
		set_process(false) # Stop processing.
		# TODO: reconnect on failure!
