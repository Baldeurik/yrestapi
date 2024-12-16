import argparse
import logging
from api_module import APIModule
from params_module import parse_params

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Change configuration using API.")
    parser.add_argument("--base_url", required=True, help="Base URL of the API")
    parser.add_argument("--username", required=True, help="Username for authentication")
    parser.add_argument("--password", required=True, help="Password for authentication")
    parser.add_argument("--profile_id", required=True, help="Profile ID for configuration")
    parser.add_argument("--param", nargs='*', help="Configuration parameters in key=value format")

    args = parser.parse_args()

    api = APIModule(base_url=args.base_url)
    api.authenticate(username=args.username, password=args.password)

    config_params = parse_params(args)
    set_config_response = api.set_config(profile_id=args.profile_id, config_params=config_params)
    if set_config_response:
        logging.info("Configuration set successfully.")
        logging.info(f"Response: {json.dumps(set_config_response, indent=2)}")
    else:
        logging.error("Failed to set configuration.")
