extends Node

# TODO: change to 60*10 on release?
const FETCH_STATS_INTERVAL: int = 60 * 1;

@onready var stats_http_client = $StatsHttpClient;
@onready var mines = {
  Global.TeamId.TEAM1: $"../MinersTeam1",
  Global.TeamId.TEAM2: $"../MinersTeam2",
};
@onready var levels = {
  Global.TeamId.TEAM1: $"../Viewport/BalanceGaugeTeam1",
  Global.TeamId.TEAM2: $"../Viewport/BalanceGaugeTeam2",
};

var fetch_stats_at;


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
	if self.fetch_stats_at <= Time.get_ticks_msec() / 1000:
		self.fetch_stats();


func add_miner(team_id: Global.TeamId, miner_type: Global.MinerType):
	self.mines[team_id].add(miner_type);
	self.levels[team_id].add(miner_type);


func fetch_stats():
	self.fetch_stats_at = Time.get_ticks_msec() / 1000 + FETCH_STATS_INTERVAL;
	stats_http_client.request(Global.API_URL + Global.API_PATH_DASHBOARD + "/" + str(Global.MINE_ID));


func _on_stats_fetched(result, response_code, headers, body):
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
	var money = team["money"];
	var items = team["items"];
	
	# TODO: add existing miners in a more efficient way
	# TODO: derive miner types from global enum
	for i in range(items.size()):
		var item = items[i];
		var effective = item["effective"];
		for _i in range(effective):
			add_miner(team_id, i + 1);
