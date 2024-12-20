import logging
import json

# Настройка логирования
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class LoopbackModule:
    def __init__(self, api_module):
        self.api_module = api_module

    def get_loopback_config(self, profile_id):
        params = [self.api.session_id, "loopback", "getprm", {"ids": {"profile": profile_id}}]
        response = self.api.send_request("call", params)
        if response:
            logging.debug(f"Loopback getprm response: {json.dumps(response, indent=2)}")
            return response.get("result", [None, None])[1].get("answer", [{}])[0].get("parameters", {})
        else:
            logging.error("Failed to get loopback configuration")
            return None

    def disable_loopback(self, profile_id):
        """Disable loopback before applying new configuration"""
        disable_config = {
            "status": False,
            "trial": {
                "ifaces": {
                    "0": {"name": "porta", "disabled": False},
                    "1": {"name": "portb", "disabled": True}
                },
                "wait_time_ms": 1000,
                "learn_time_ms": 1000
            },
            "loopback": {
                "duration_us": "0",
                "type": "layer4"
            }
        }
        
        logging.info(f"Disabling loopback for profile {profile_id}")
        response = self.api_module.send_request("call", 
            ["loopback", "setprm", {"ids": {"profile": profile_id}, "parameters": disable_config}])
        
        if not response or response.get("result", [None, None])[1].get("retcode") != 0:
            logging.error("Failed to disable loopback")
            return False
        return True

    def force_enable_loopback(self, profile_id):
        """Force enable loopback for specified profile"""
        logging.info(f"Force enabling loopback for profile {profile_id}")
        
        if not self.disable_loopback(profile_id):
            return False
            
        enable_config = {
            "status": True,
            "trial": {
                "ifaces": {
                    "0": {"name": "porta", "disabled": False},
                    "1": {"name": "portb", "disabled": True}
                },
                "wait_time_ms": 1000,
                "learn_time_ms": 1000
            },
            "loopback": {
                "duration_us": "0",
                "type": "layer4"
            }
        }
        
        response = self.api_module.send_request("call",
            ["loopback", "setprm", {"ids": {"profile": profile_id}, "parameters": enable_config}])
            
        if response:
            retcode = response.get("result", [None, None])[1].get("retcode")
            if retcode == 0:
                logging.info("Loopback force enabled successfully")
                return True
            else:
                logging.error(f"Failed to force enable loopback. Code: {retcode}")
        return False

    def set_loopback_config(self, profile_id, config_params):
        """Set loopback configuration with validation"""
        if not self.disable_loopback(profile_id):
            return False
            
        logging.info("Applying new loopback configuration...")
        response = self.api_module.send_request("call",
            ["loopback", "setprm", {"ids": {"profile": profile_id}, "parameters": config_params}])
        
        if response:
            retcode = response.get("result", [None, None])[1].get("retcode")
            retmsg = response.get("result", [None, None])[1].get("retmsg")
            if retcode == 0:
                logging.info(f"Loopback configuration set successfully. Message: {retmsg}")
                return True
            else:
                logging.error(f"Failed to set loopback configuration. Code: {retcode}, Message: {retmsg}")
        return False

    def start_loopback_test(self, profile_id):
        params = ["loopback", "start", {"ids": {"profile": profile_id}}]
        response = self.api_module.send_request("call", params)
        if response:
            retcode = response.get("result", [None, None])[1].get("retcode")
            retmsg = response.get("result", [None, None])[1].get("retmsg")
            if retcode == 0:
                logging.info(f"Loopback test started successfully. Message: {retmsg}")
            else:
                logging.error(f"Failed to start loopback test. Code: {retcode}, Message: {retmsg}")
        return response