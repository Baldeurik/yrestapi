import logging
import json
from api_module import APIModule
from params_module import parse_params
from input_modules.cli_input import get_cli_input
from input_modules.cli_input import convert_time_to_us
from test_modules.cr_test import run_cr_test
from output_modules.json_output import output_to_json
from loopback_module import LoopbackModule # Новый импорт

def check_object_exists(api_module, profile_id):
    config_response = api_module.get_config(profile_id)
    if config_response:
        logging.info(f"Object with profile_id {profile_id} exists.")
        return config_response
    else:
        logging.error(f"Object with profile_id {profile_id} does not exist.")
        return None

def check_enabled_services(config):
    """Parse enabled services from config"""
    enabled = []
    if config.get("result"):
        params = config["result"][1]["answer"][0]["parameters"]
        services = params.get("y1564", {}).get("services", [])
        for i, service in enumerate(services):
            if service.get("enabled", False):
                enabled.append(i)
    return enabled

if __name__ == "__main__":
    args = get_cli_input()

    if not all([args.url, args.username, args.password]):
        logging.error("Missing authentication arguments")
        exit(1)

    api = APIModule(base_url=args.url)
    api.authenticate(username=args.username, password=args.password)

    # Проверка наличия всех необходимых аргументов
    if not api.session_id:
        logging.error("Authentication failed")
        exit(1)

    if args.loopback_force:
            loopback_module = LoopbackModule(api)
            if loopback_module.force_enable_loopback(args.profile_id):
                logging.info("Loopback force operation completed successfully")
                exit(0)
            else:
                logging.error("Loopback force operation failed")
                exit(1)
             

    if args.loopback_only:
        # Run only loopback test
        loopback_module = LoopbackModule(api)
        loopback_config = {
            "status": args.loopback.lower() == 'true',
            "trial": {
                "ifaces": {
                    "0": {
                        "disabled": args.loopback_iface0_disabled.lower() == 'true'
                    },
                    "1": {
                        "disabled": args.loopback_iface1_disabled.lower() == 'true'
                    }
                },
            },
            "loopback": {
                "duration_us": args.loopback_duration,
                "type": args.loopback_type
            }
        }
        loopback_module.set_loopback_config(args.profile_id, loopback_config)
        exit(0)
    if args.loopback_duration:
        try:
            duration_us = convert_time_to_us(args.loopback_duration)
            loopback_config = {
                "status": True,
                "trial": {
                    "ifaces": {
                        "0": {"name": args.loopback_iface0_name, "disabled": False},
                        "1": {"name": args.loopback_iface1_name, "disabled": True}
                    },
                },
                "loopback": {
                    "duration_us": duration_us,
                    "type": args.loopback_type
                }
            }
            loopback_module = LoopbackModule(api)  # Создание экземпляра нового модуля
            current_config_params = loopback_module.get_loopback_config(args.profile_id)
            logging.debug(f"Current loopback config params: {json.dumps(current_config_params, indent=2)}")
            if not loopback_module.set_loopback_config(args.profile_id, loopback_config):
                logging.error("Failed to apply loopback configuration")
                exit(1)
        except ValueError as e:
            logging.error(f"Invalid duration format: {e}")
            exit(1)  
    
        
        
        # Проверка, что сессия активна
    if not api.session_id:
        logging.error("Session ID is not set. Authentication may have failed.")
        exit(1)


    if args.force_start:
        current_config = check_object_exists(api, args.profile_id)
        if current_config:
            enabled_services = check_enabled_services(current_config)
            logging.info(f"Found enabled services: {enabled_services}")
            api.start_test(args.profile_id)
            loopback_module.start_loopback_test(args.profile_id)
            exit(0)

    current_config = check_object_exists(api, args.profile_id)
    if not current_config:
        logging.error("Cannot proceed with configuration change. Object does not exist.")
        exit(1)

    # Получаем текущие параметры конфигурации
    current_params = current_config["result"][1]["answer"][0]["parameters"]
    logging.debug(f"Current config params: {json.dumps(current_params, indent=2)}")
    try:
        config_params = parse_params(args, current_params)
        response = api.set_config(args.profile_id, config_params)
        if not response or response.get("result", [None, None])[1].get("retcode") != 0:
            logging.error("Failed to apply configuration changes")
            exit(1)
    except ValueError as e:
        logging.error(f"Configuration error: {e}")
        exit(1)

    # Применение обновленной конфигурации
    run_cr_test(api, args.profile_id, config_params)

    # Настройка сервисов для profile0
    if args.profile0_service_count:
        for service_index in range(args.profile0_service_count):
            service_params = config_params["y1564"]["services"][service_index]
            response = api.set_service_config(args.profile_id, service_index, service_params)
            if response:
                retcode = response.get("result", [None, None])[1].get("retcode")
                retmsg = response.get("result", [None, None])[1].get("retmsg")
                if retcode == 0:
                    logging.info(f"Service {service_index} configuration set successfully. Message: {retmsg}")
                else:
                    logging.error(f"Failed to set service {service_index} configuration. Code: {retcode}, Message: {retmsg}")

    # Настройка сервисов для profile1
    if args.profile1_service_count:
        for service_index in range(args.profile1_service_count):
            service_params = config_params["y1564"]["services"][service_index]
            response = api.set_service_config(args.profile_id, service_index, service_params)
            if response:
                retcode = response.get("result", [None, None])[1].get("retcode")
                retmsg = response.get("result", [None, None])[1].get("retmsg")
                if retcode == 0:
                    logging.info(f"Service {service_index} configuration set successfully. Message: {retmsg}")
                else:
                    logging.error(f"Failed to set service {service_index} configuration. Code: {retcode}, Message: {retmsg}")

    # Настройка loopback
    loopback_config = {
        "status": args.loopback_status.lower() == 'true',
        "trial": {
            "ifaces": {
                "0": {
                    "disabled": args.loopback_iface0_disabled.lower() == 'true'
                },
                "1": {
                    "disabled": args.loopback_iface1_disabled.lower() == 'true'
                }
            },
        },
        "loopback": {
            "duration_us": args.loopback_duration_us,
            "type": args.loopback_type
        }
    }
    response = loopback_module.set_loopback_config(args.profile_id, loopback_config)
    if response:
        retcode = response.get("result", [None, None])[1].get("retcode")
        retmsg = response.get("result", [None, None])[1].get("retmsg")
        if retcode == 0:
            logging.info(f"Loopback configuration set successfully. Message: {retmsg}")
        else:
            logging.error(f"Failed to set loopback configuration. Code: {retcode}, Message: {retmsg}")

    # Запуск теста, если указан флаг --start_test
    if args.start_test:
        api.start_test(args.profile_id)
        loopback_module.start_loopback_test(args.profile_id)

    # Проверка применения конфигурации
    updated_config = api.get_config(args.profile_id)
    if updated_config:
        updated_params = updated_config["result"][1]["answer"][0]["parameters"]
        logging.info(f"Updated config params: {json.dumps(updated_params, indent=2)}")
    else:
        logging.error("Failed to retrieve updated configuration.")

    if args.output_format == 'JSON':
        output_to_json(config_params, 'output.json')
    current_config_params = loopback_module.get_loopback_config(args.profile_id)
    logging.debug(f"Current loopback config params: {json.dumps(current_config_params, indent=2)}")
            