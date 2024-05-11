extends Node

var socket = WebSocketPeer.new()

enum PacketClientType {
	GameState = 1,
}

func _ready():
	socket.connect_to_url(Global.WEBSOCKET_API_URL);

func _process(delta):
	# Keep progressing the socket
	socket.poll()
	
	var state = socket.get_ready_state()
	if state == WebSocketPeer.STATE_OPEN:
		while socket.get_available_packet_count():
			var packet_raw = socket.get_packet();
			if packet_raw.is_empty():
				continue;

			var packet_str = packet_raw.get_string_from_utf8();
			if packet_str.is_empty():
				print("Got malformed packet, invalid UTF-8: ", str(packet_raw));
				continue;

			var packet = JSON.parse_string(packet_str);
			if packet == null:
				print("Got malformed packet, invalid JSON: ", str(packet_raw));
				continue;

			self.handle_raw_packet(packet);

	elif state == WebSocketPeer.STATE_CLOSING:
		# Keep polling to achieve proper close.
		pass

	elif state == WebSocketPeer.STATE_CLOSED:
		var code = socket.get_close_code()
		var reason = socket.get_close_reason()
		print("WebSocket closed with code: %d, reason %s. Clean: %s" % [code, reason, code != -1])
		set_process(false) # Stop processing.
		# TODO: reconnect on failure!


func handle_raw_packet(packet: Dictionary):
	if !packet.has("packet_id"):
		print("Got malformed packet, no packet_id: ", packet);
	if !packet.has("data"):
		print("Got malformed packet, no data: ", packet);
	handle_packet(packet["packet_id"], packet["data"]);


func handle_packet(packet_id: int, data: Dictionary):
	if !PacketClientType.values().has(packet_id):
		print("Got malformed packet, unknown packet ID: ", str(packet_id));
		return;
		
	match packet_id:
		PacketClientType.GameState:
			handle_game_state(data);
		_:
			print("Failed to handle packet with ID ", str(packet_id), ", missing handler?");


func handle_game_state(state: Dictionary):
	print("Got game state: ", str(state));
