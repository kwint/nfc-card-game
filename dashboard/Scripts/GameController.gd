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


func _process(_delta):
	# Keep fetching stats to prevent game desync
	@warning_ignore("integer_division")
	var now = Time.get_ticks_msec() / 1000;
	if self.fetch_stats_at <= now:
		self.fetch_stats();


func add_miners(team_id: Global.TeamId, miner_type: Global.MinerType, amount: int, effective: int, animate_text = null):
	self.mines[team_id].add_miners(miner_type, amount, animate_text);
	self.levels[team_id].add_levels(miner_type, effective);


func set_miners(team_id: Global.TeamId, miner_type: Global.MinerType, amount: int, effective: int):
	self.mines[team_id].set_miners(miner_type, amount, null);
	self.levels[team_id].set_level(miner_type, effective);


func fetch_stats():
	@warning_ignore("integer_division")
	self.fetch_stats_at = Time.get_ticks_msec() / 1000 + FETCH_STATS_INTERVAL;
	stats_http_client.request(Global.API_URL + Global.API_PATH_DASHBOARD + "/" + str(Global.MINE_ID));


func _on_stats_fetched(_result, _response_code, _headers, body):
	var json = JSON.parse_string(body.get_string_from_utf8())
	if json == null:
		print("Got malformed JSON body: ", body);
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
	# TODO: derive miner types from global enum
	var items = team["items"];
	for i in range(items.size()):
		var item = items[i];
		self.set_miners(team_id, i + 1, item["amount"], item["effective"]);


func update_money(team_id: Global.TeamId, amount: int, flowing_label: bool = true):
	self.money[team_id].set_money(amount, flowing_label);
