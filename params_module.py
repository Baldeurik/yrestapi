import argparse
import logging
import json

def parse_params(args, current_config):
    config_params = current_config.copy()
    config_params["status"] = args.status.lower() == 'true'
    config_params["y1564"]["cir_enabled"] = args.cir_enabled.lower() == 'true'
    config_params["y1564"]["eir_enabled"] = args.eir_enabled.lower() == 'true'
    config_params["y1564"]["tp_enabled"] = args.tp_enabled.lower() == 'true'
    logging.debug(f"Updated config params: {json.dumps(config_params, indent=2)}")
    return config_params
