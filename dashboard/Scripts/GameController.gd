extends Node

# TODO: change to 60*10 on release?
const FETCH_STATS_INTERVAL: int = 60 * 1;
const FETCH_STATS_FAIL_RETRY_DELAY: int = 10;

@onready var stats_http_client = $StatsHttpClient;
@onready var websocket_client = $WebSocketClient;
@onready var mines = {
  Global.TeamId.TEAM1: $"../MinersTeam1",
  Global.TeamId.TEAM2: $"../MinersTeam2",
};
@onready var money = {
  Global.TeamId.TEAM1: $"../Viewport/MoneyTeam1",
  Global.TeamId.TEAM2: $"../Viewport/MoneyTeam2",
};
@onready var levels = {
  Global.TeamId.TEAM1: $"../Viewport/BalanceGaugeTeam1",
  Global.TeamId.TEAM2: $"../Viewport/BalanceGaugeTeam2",
};
@onready var background = $"../Viewport/Background";
@onready var mountain = $"../Viewport/AspectRatioContainer/ReferenceRect/Mountain";

@export var background_colors: Array[Color] = [
	Color.WHITE,
	Color(0.3, 1.5, 0.3),
	Color(1.5, 0.3, 0.3),
];
@export var mountain_textures: Array[Texture2D] = [
	preload("res://Sprites/Mountain/mountain1.png"),
	preload("res://Sprites/Mountain/mountain2.png"),
	preload("res://Sprites/Mountain/mountain3.png"),
];
@export var mountain_colors: Array[Color] = [
	Color(0.3, 0.5, 1.0),
	Color(0.4, 1.0, 0.5),
	Color(1.0, 0.6, 0.5),
];

var mine_id: int;
var fetch_stats_at: int;


func _ready():
	# Connect stats HTTP client and fetch once
	stats_http_client.request_completed.connect(_on_stats_fetched)
	
	# Connect on start
	self.switch_mine.call_deferred(Global.MINE_IDS[0]);


func _process(_delta):
	# Refresh current mine or cycle to next mine
	if Input.is_action_just_pressed("reconnect"):
		self.reconnect();
		return;
	if Input.is_action_just_pressed("next_mine"):
		self.cycle_mine();
		return;
	
	# Keep fetching stats to prevent game desync
	if self.fetch_stats_at <= Global.now():
		self.fetch_stats();


func add_miners(team_id: Global.TeamId, miner_type: Global.MinerType, amount: int, effective: int, animate_text = null):
	self.mines[team_id].add_miners(miner_type, amount, animate_text);
	self.levels[team_id].add_levels(miner_type, effective);


func set_miners(team_id: Global.TeamId, miner_type: Global.MinerType, amount: int, effective: int):
	self.mines[team_id].set_miners(miner_type, amount, null);
	self.levels[team_id].set_level(miner_type, effective);


func update_money(team_id: Global.TeamId, amount: int, flowing_label: bool = true, label = null):
	self.money[team_id].set_money(amount, flowing_label, label);


func reconnect():
	# Reset current visuals
	for team_id in Global.TeamId.values():
		self.update_money(team_id, 0, false);
		for miner_type in Global.MinerType.values():
			self.set_miners(team_id, miner_type, 0, 0);
	
	# Update miner ID and reconnect
	self.fetch_stats();
	self.websocket_client.reconnect();


func switch_mine(mine_id: int):
	if !Global.MINE_IDS.has(mine_id):
		assert(false, "Unknown mine ID");
	self.mine_id = mine_id;
	self.reconnect();
	
	# Update textures and colors
	if !self.background_colors.is_empty():
		self.background.modulate = self.background_colors[self.get_mine_index() % self.background_colors.size()];
	if !self.mountain_textures.is_empty():
		self.mountain.texture = self.mountain_textures[self.get_mine_index() % self.mountain_textures.size()];
	if !self.mountain_colors.is_empty():
		self.mountain.modulate = self.mountain_colors[self.get_mine_index() % self.mountain_colors.size()];


func cycle_mine():
	var next_mine_id = Global.MINE_IDS[(get_mine_index() + 1) % Global.MINE_IDS.size()];
	self.switch_mine(next_mine_id);


func get_mine_index() -> int:
	var i = Global.MINE_IDS.find(self.mine_id);
	if i == -1:
		assert(false, "Unknown mine ID");
	return i;


func fetch_stats():
	self.fetch_stats_at = Global.now() + FETCH_STATS_INTERVAL;
	self.stats_http_client.cancel_request();
	self.stats_http_client.request(Global.API_URL + Global.API_PATH_DASHBOARD + "/" + str(self.mine_id));


func _on_stats_fetched(result, _response_code, _headers, body):
	# Handle request failures
	if result != HTTPRequest.RESULT_SUCCESS:
		print("Failed to request mine stats (result: ", result, "), retrying in ", FETCH_STATS_FAIL_RETRY_DELAY, " seconds...");
		self.fetch_stats_at = Global.now() + FETCH_STATS_FAIL_RETRY_DELAY;
		return;
	
	body = body.get_string_from_utf8();
	if body.is_empty():
		print("Got malformed JSON body, ignoring: ", body);
		return;
	
	var json = JSON.parse_string(body);
	if !json:
		print("Got malformed JSON body, ignoring: ", body);
		return;
		
	self.process_stats(json);


func process_stats(stats: Dictionary):
	var teams_stats = stats["teams"];
	
	for team_id in Global.TeamId.values():
		if !teams_stats.has(str(team_id)):
			print("missing stats for team ", team_id);
			continue;
		
		var team_stats = teams_stats[str(team_id)];
		process_stats_team(team_id, team_stats);


func process_stats_team(team_id: Global.TeamId, team: Dictionary):
	self.update_money(team_id, team["money"], false);
	
	# Update miners
	var items = team["items"];
	for i in range(items.size()):
		var item = items[i];
		self.set_miners(team_id, item["miner_type"], item["amount"], item["effective"]);
