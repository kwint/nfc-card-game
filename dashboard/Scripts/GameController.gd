extends Node

# TODO: change to 60*10 on release?
const FETCH_STATS_INTERVAL: int = 60 * 1;

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
	
	# # Spawn random set of miners on start in debug builds
	# if OS.has_feature("debug"):
	# 	for i in range(1 + randi() % 4):
	# 		self.add_miner.call_deferred(true, Global.MinerType.MINER1);
	# 	for i in range(1 + randi() % 4):
	# 		self.add_miner.call_deferred(false, Global.MinerType.MINER1);


func _process(_delta):
	# Keep fetching stats to prevent game desync
	@warning_ignore("integer_division")
	var now = Time.get_ticks_msec() / 1000;
	if self.fetch_stats_at <= now:
		self.fetch_stats();


func add_miner(team_id: Global.TeamId, miner_type: Global.MinerType):
	self.mines[team_id].add_miner(miner_type);
	self.levels[team_id].add_level(miner_type);


func add_miners(team_id: Global.TeamId, miner_type: Global.MinerType, amount: int):
	# TODO: add in batch!
	for _i in range(amount):
		self.add_miner(team_id, miner_type);


func set_miners(team_id: Global.TeamId, miner_type: Global.MinerType, amount: int):
	self.mines[team_id].set_miners(miner_type, amount);
	self.levels[team_id].set_level(miner_type, amount);
	

func fetch_stats():
	@warning_ignore("integer_division")
	self.fetch_stats_at = Time.get_ticks_msec() / 1000 + FETCH_STATS_INTERVAL;
	stats_http_client.request(Global.API_URL + Global.API_PATH_DASHBOARD + "/" + str(Global.MINE_ID));


func _on_stats_fetched(_result, _response_code, _headers, body):
	var json = JSON.parse_string(body.get_string_from_utf8())
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
	self.update_money(team_id, team["money"]);
	
	# Update miners
	# TODO: add existing miners in a more efficient way
	# TODO: derive miner types from global enum
	var items = team["items"];
	for i in range(items.size()):
		var item = items[i];
		var effective = item["effective"];
		set_miners(team_id, i + 1, effective);


func update_money(team_id: Global.TeamId, amount: int):
	self.money[team_id].set_money(amount);
