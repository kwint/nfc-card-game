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
	var mine_id = MINE_IDS[0];

	# Prefer mine ID from environment if valid
	var env = OS.get_environment("NFC_MINE_ID");
	if !env.is_empty() && MINE_IDS.has(env.to_int()):
		mine_id = env.to_int();

	return mine_id;


static func get_api_url() -> String:
	var url = API_URL;

	# Prefer API URL from environment
	var env = OS.get_environment("NFC_API_URL");
	if !env.is_empty():
		url = env;

	return url;


static func get_websocket_api_url() -> String:
	var url = WEBSOCKET_API_URL;

	# Prefer websocket API URL from environment
	var env = OS.get_environment("NFC_WEBSOCKET_API_URL");
	if !env.is_empty():
		url = env;

	return url;


static func is_default_fullscreen() -> bool:
	var fullscreen = !OS.has_feature("debug");

	# Prefer fullscreen setting from environment
	var env = OS.get_environment("NFC_FULLSCREEN");
	if !env.is_empty():
		fullscreen = env.to_lower() == "true" || env.to_int() > 0;

	return fullscreen;


static func is_show_debug() -> bool:
	var show_debug = OS.has_feature("debug");

	# Prefer debug setting from environment
	var env = OS.get_environment("NFC_DEBUG");
	if !env.is_empty():
		show_debug = env.to_lower() == "true" || env.to_int() > 0;

	return show_debug;
