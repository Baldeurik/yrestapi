import requests
import json
import jmespath
import logging

# Настройка логирования
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class APIModule:
    def __init__(self, base_url, headers=None):
        self.base_url = base_url
        self.headers = headers if headers else {"Content-Type": "application/json"}
        self.session_id = None
        logging.debug(f"APIModule initialized with base_url: {self.base_url}")

    def authenticate(self, username, password):
        auth_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "call",
            "params": ["00000000000000000000000000000000", "session", "login", {
                "username": username,
                "password": password,
                "timeout": 300
            }]
        }
        try:
            logging.info("Sending authentication request...")
            logging.debug(f"Auth request: {json.dumps(auth_request, indent=2)}")
            response = requests.post(self.base_url, json=auth_request, headers=self.headers)
            response.raise_for_status()  # Вызовет исключение для HTTP-ошибок
            auth_data = response.json()
            logging.debug(f"Authentication response: {json.dumps(auth_data, indent=2)}")
            result = auth_data.get("result", [])
            if len(result) > 1 and isinstance(result[1], dict):
                self.session_id = result[1].get("ubus_rpc_session")
                logging.info(f"Authentication successful. Session ID: {self.session_id}")
            else:
                logging.error("Unexpected response format")
                self.session_id = None
        except requests.exceptions.RequestException as e:
            logging.error(f"Authentication error: {e}")
            self.session_id = None

    def send_request(self, method, params):
        if not self.session_id:
            logging.error("Authentication required before sending requests.")
            return None

        request_data = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "call",
            "params": [self.session_id] + params
        }
        try:
            logging.info(f"Sending {method} request with params: {params}")
            logging.debug(f"Request data: {json.dumps(request_data, indent=2)}")
            response = requests.post(self.base_url, json=request_data, headers=self.headers)
            response.raise_for_status()  # Вызовет исключение для HTTP-ошибок
            logging.debug(f"Response: {json.dumps(response.json(), indent=2)}")
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Request error: {e}")
            return None

    def get_config(self, profile_id):
        params = ["y1564", "getprm", {"ids": {"profile": profile_id}}]
        return self.send_request("call", params)

    def set_config(self, profile_id, config_params):
        params = ["y1564", "setprm", {"ids": {"profile": profile_id}, "parameters": config_params}]
        response = self.send_request("call", params)
        if response:
            retcode = response.get("result", [None, None])[1].get("retcode")
            retmsg = response.get("result", [None, None])[1].get("retmsg")
            if retcode == 0:
                logging.info(f"Configuration set successfully. Message: {retmsg}")
            else:
                logging.error(f"Failed to set configuration. Code: {retcode}, Message: {retmsg}")
        return response

    def set_service_config(self, profile_id, service_id, config_params):
        params = ["y1564", "setprm", {"ids": {"profile": profile_id, "service": service_id}, "parameters": config_params}]
        response = self.send_request("call", params)
        if response:
            retcode = response.get("result", [None, None])[1].get("retcode")
            retmsg = response.get("result", [None, None])[1].get("retmsg")
            if retcode == 0:
                logging.info(f"Service configuration set successfully. Message: {retmsg}")
            else:
                logging.error(f"Failed to set service configuration. Code: {retcode}, Message: {retmsg}")
        return response

    def start_test(self, profile_id):
        params = ["y1564", "start", {"ids": {"profile": profile_id}}]
        response = self.send_request("call", params)
        if response:
            retcode = response.get("result", [None, None])[1].get("retcode")
            retmsg = response.get("result", [None, None])[1].get("retmsg")
            if retcode == 0:
                logging.info(f"Test started successfully. Message: {retmsg}")
            else:
                logging.error(f"Failed to start test. Code: {retcode}, Message: {retmsg}")
        return response

    def parse_response(self, response, key):
        if response:
            result = jmespath.search(key, response)
            logging.debug(f"Parsed response: {json.dumps(result, indent=2)}")
            return result
        else:
            logging.error("No response to parse.")
            return None
        
        
