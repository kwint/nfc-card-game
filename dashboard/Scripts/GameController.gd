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
	
	# TODO: set data for both teams
	var team_data = json["teams"][str(Global.TeamId.TEAM1)];
	
	# TODO: set money!
	var money = team_data["money"];
	
	# TODO: add existing miners in a more efficient way
	var i = 0;
	for item_stats in team_data["items"]:
		var effective = item_stats["effective"];
		for j in range(effective):
			add_miner(Global.TeamId.TEAM1, i + 1);
		i += 1;
		
	# TODO: do the same for the other team?
	team_data = json["teams"][str(Global.TeamId.TEAM2)];
	i = 0;
	for item_stats in team_data["items"]:
		var effective = item_stats["effective"];
		for j in range(effective):
			add_miner(Global.TeamId.TEAM2, i + 1);
		i += 1;
