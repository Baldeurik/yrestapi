import logging
import json
from api_module import APIModule
from params_module import parse_params
from input_modules.cli_input import get_cli_input
from test_modules.cr_test import run_cr_test
from output_modules.json_output import output_to_json

def check_object_exists(api_module, profile_id):
    config_response = api_module.get_config(profile_id)
    if config_response:
        logging.info(f"Object with profile_id {profile_id} exists.")
        return config_response
    else:
        logging.error(f"Object with profile_id {profile_id} does not exist.")
        return None

if __name__ == "__main__":
    args = get_cli_input()

    # Проверка наличия всех необходимых аргументов
    if not args.base_url or not args.username or not args.password or not args.profile_id:
        logging.error("Missing required arguments.")
        exit(1)

    # Проверка, что хотя бы один параметр включен
    if not any([args.cir_enabled.lower() == 'true', args.eir_enabled.lower() == 'true', args.tp_enabled.lower() == 'true']):
        logging.error("At least one of cir_enabled, eir_enabled, or tp_enabled must be true.")
        exit(1)

    api = APIModule(base_url=args.base_url)
    api.authenticate(username=args.username, password=args.password)

    current_config = check_object_exists(api, args.profile_id)
    if not current_config:
        logging.error("Cannot proceed with configuration change. Object does not exist.")
        exit(1)

    # Получаем текущие параметры конфигурации
    current_params = current_config["result"][1]["answer"][0]["parameters"]
    logging.debug(f"Current config params: {json.dumps(current_params, indent=2)}")

    config_params = parse_params(args, current_params)

    # Применение обновленной конфигурации
    run_cr_test(api, args.profile_id, config_params)

    if args.output_format == 'JSON':
        output_to_json(config_params, 'output.json')
