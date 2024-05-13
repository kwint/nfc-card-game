extends Node

@onready var game_controller = $"../../GameController";

var socket = WebSocketPeer.new()
var connected: bool = false;

enum PacketServerType {
	# data: mine ID
	SetMine = 1,
}

enum PacketClientType {
	# data: game state
	GameState = 1,
	MineState = 2,
	MineMoneyUpdate = 3,
	MineMinersAdded = 4,
}


func _ready():
	socket.connect_to_url(Global.WEBSOCKET_API_URL);


func _process(_delta):
	# Keep progressing the socket
	socket.poll()
	
	var state = socket.get_ready_state()
	if state == WebSocketPeer.STATE_OPEN:
		# Call on_connected the first time we connect
		if !self.connected:
			self.connected = true;
			self.on_connected();
		
		# Handle incoming packets
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
		self.connected = false;
		pass

	elif state == WebSocketPeer.STATE_CLOSED:
		self.connected = false;
		
		var code = socket.get_close_code()
		var reason = socket.get_close_reason()
		print("WebSocket closed with code: %d, reason %s. Clean: %s" % [code, reason, code != -1])
		set_process(false) # Stop processing.
		# TODO: reconnect on failure!


func on_connected():
	# Share client state with server
	self.send_set_mine(Global.MINE_ID);


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
		PacketClientType.MineState:
			handle_mine_state(data);
		PacketClientType.MineMoneyUpdate:
			handle_mine_money_update(data);
		PacketClientType.MineMinersAdded:
			handle_mine_miners_added(data);
		_:
			print("Failed to handle packet with ID ", str(packet_id), ", missing handler?");


func handle_game_state(_state: Dictionary):
	print("Ignoring game state packet");


func handle_mine_state(state: Dictionary):
	self.game_controller.process_stats(state);


func handle_mine_money_update(state: Dictionary):
	if state["mine_id"] != Global.MINE_ID:
		return;
	self.game_controller.update_money(state["team_id"], state["money"]);


func handle_mine_miners_added(state: Dictionary):
	if state["mine_id"] != Global.MINE_ID:
		return;
	self.game_controller.add_miners(
		state["team_id"],
		state["miner_type"],
		state["amount"],
		state["effective"],
		state["miner_type_name"],
	);


func send_packet(packet_id: PacketServerType, data: Dictionary):
	# TODO: ignore if not connected?
	
	var packet = {
		"packet_id": packet_id,
		"data": data,
	};
	print("Sending packet: ", str(packet));
	self.socket.send_text(JSON.stringify(packet, "", false));


func send_set_mine(mine_id: int):
	send_packet(PacketServerType.SetMine, {"mine_id": mine_id});
