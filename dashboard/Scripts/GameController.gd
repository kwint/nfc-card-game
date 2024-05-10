extends Node

# TODO: change to 60*10 on release?
const FETCH_STATS_INTERVAL: int = 60 * 1;

@onready var stats_http_client = $StatsHttpClient;
@onready var mines = [
  $"../MinersLeft",
  $"../MinersRight",
];
@onready var levels = [
  $"../Viewport/BalanceGaugeLeft",
  $"../Viewport/BalanceGaugeRight",
];

var fetch_stats_at;


func _ready():
	# Connect stats HTTP client and fetch once
	stats_http_client.request_completed.connect(_on_stats_fetched)
	self.fetch_stats.call_deferred();
	
	# Spawn random set of miners on start in debug builds
	if OS.has_feature("debug"):
		for i in range(1 + randi() % 4):
			self.add_miner.call_deferred(true, Global.MinerType.MINER1);
		for i in range(1 + randi() % 4):
			self.add_miner.call_deferred(false, Global.MinerType.MINER1);


func _process(_delta):
	# Keep fetching stats to prevent game desync
	if self.fetch_stats_at <= Time.get_ticks_msec() / 1000:
		self.fetch_stats();


func add_miner(left: bool, miner_type: Global.MinerType):
	var i = 0 if left else 1;
	self.mines[i].add(miner_type);
	self.levels[i].add(miner_type);


func fetch_stats():
	self.fetch_stats_at = Time.get_ticks_msec() / 1000 + FETCH_STATS_INTERVAL;
	stats_http_client.request(Global.API_URL + Global.API_PATH_DASHBOARD);


func _on_stats_fetched(result, response_code, headers, body):
	var json = JSON.parse_string(body.get_string_from_utf8())
	print(json)
