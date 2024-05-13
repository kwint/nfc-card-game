class_name Global

const MINE_ID: int = 1;

const API_URL: String = "http://localhost:8000/api";
const API_PATH_DASHBOARD: String = "/dashboard";

const WEBSOCKET_API_URL: String = "ws://localhost:8000/api/ws";

enum TeamId { TEAM1 = 1, TEAM2 = 2 }

enum MinerType { MINER1 = 1, MINER2 = 2, MINER3 = 3 };


# TODO: fetch these from server
static func miner_type_name(type: MinerType) -> String:
	match type:
		MinerType.MINER1:
			return "Mijnwerker";
		MinerType.MINER2:
			return "Drilboor";
		MinerType.MINER3:
			return "Bulldozer";
		_:
			print("No name configured for miner type ", type);
			return "+1";
