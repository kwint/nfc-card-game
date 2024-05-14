extends Node

# TODO: change to 60*10 on release?
const FETCH_STATS_INTERVAL: int = 60 * 1;
const FETCH_STATS_RETRY_INTERVAL: int = 10;

@onready var stats_http_client = $StatsHttpClient;
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

var fetch_stats_at: int;


func _ready():
	# Connect stats HTTP client and fetch once
	stats_http_client.request_completed.connect(_on_stats_fetched)
	self.fetch_stats.call_deferred();


func _process(_delta):
	# Keep fetching stats to prevent game desync
	if self.fetch_stats_at <= self.now():
		self.fetch_stats();


func add_miners(team_id: Global.TeamId, miner_type: Global.MinerType, amount: int, effective: int, animate_text = null):
	self.mines[team_id].add_miners(miner_type, amount, animate_text);
	self.levels[team_id].add_levels(miner_type, effective);


func set_miners(team_id: Global.TeamId, miner_type: Global.MinerType, amount: int, effective: int):
	self.mines[team_id].set_miners(miner_type, amount, null);
	self.levels[team_id].set_level(miner_type, effective);


func fetch_stats():
	self.fetch_stats_at = self.now() + FETCH_STATS_INTERVAL;
	stats_http_client.request(Global.API_URL + Global.API_PATH_DASHBOARD + "/" + str(Global.MINE_ID));


func _on_stats_fetched(result, _response_code, _headers, body):
	# Handle request failures
	if result != HTTPRequest.RESULT_SUCCESS:
		print("Failed to request mine stats (result: ", result, "), retrying in ", FETCH_STATS_RETRY_INTERVAL, " seconds...");
		self.fetch_stats_at = self.now() + FETCH_STATS_RETRY_INTERVAL;
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


func update_money(team_id: Global.TeamId, amount: int, flowing_label: bool = true, label = null):
	self.money[team_id].set_money(amount, flowing_label, label);


func now() -> int:
	@warning_ignore("integer_division")
	return Time.get_ticks_msec() / 1000;
