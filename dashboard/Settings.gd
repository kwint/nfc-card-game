class_name Settings

# Available mine IDs
const MINE_IDS = [1, 2, 3];

#const API_URL: String = "http://localhost:8000/api";
const API_URL: String = "https://nfc.qvdijk.nl/api";
const API_PATH_DASHBOARD: String = "/dashboard";

#const WEBSOCKET_API_URL: String = "ws://localhost:8000/api/ws";
const WEBSOCKET_API_URL: String = "wss://nfc.qvdijk.nl/api/ws";

enum TeamId { TEAM1 = 1, TEAM2 = 2 }

enum MinerType { MINER1 = 1, MINER2 = 2, MINER3 = 3 };


# Get the current time in seconds.
static func now() -> int:
	@warning_ignore("integer_division")
	return Time.get_ticks_msec() / 1000;


static func get_default_mine() -> int:
	return MINE_IDS[0];


static func get_api_url() -> String:
	return API_URL;


static func get_websocket_api_url() -> String:
	return WEBSOCKET_API_URL;


static func is_default_fullscreen() -> bool:
	return !OS.has_feature("debug");
