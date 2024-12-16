import logging
import json

def run_cr_test(api_module, profile_id, config_params):
    # Логика выполнения теста CR
    response = api_module.set_config(profile_id, config_params)
    if response:
        logging.info("CR test set successfully.")
        logging.info(f"Response: {json.dumps(response, indent=2)}")
    else:
        logging.error("Failed to set CR test configuration.")
