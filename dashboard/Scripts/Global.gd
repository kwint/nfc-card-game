class_name Global

const API_URL: String = "http://localhost:8000/api";
const API_PATH_DASHBOARD: String = "/dashboard";

enum MinerType { MINER1, MINER2, MINER3 };


static func miner_type_index(type: MinerType):
	match type:
		MinerType.MINER1:
			return 0;
		MinerType.MINER2:
			return 1;
		MinerType.MINER3:
			return 2;
		_:
			assert(false, "unknown miner type");
