import argparse

def get_cli_input():
    parser = argparse.ArgumentParser(description="Change configuration using API.")
    parser.add_argument("--base_url", required=True, help="Base URL of the API")
    parser.add_argument("--username", required=True, help="Username for authentication")
    parser.add_argument("--password", required=True, help="Password for authentication")
    parser.add_argument("--profile_id", required=True, help="Profile ID for configuration")
    parser.add_argument("--status", required=True, choices=['true', 'false'], help="Enable or disable the profile")
    parser.add_argument("--cir_enabled", required=True, choices=['true', 'false'], help="Enable CIR")
    parser.add_argument("--eir_enabled", required=True, choices=['true', 'false'], help="Enable EIR")
    parser.add_argument("--tp_enabled", required=True, choices=['true', 'false'], help="Enable TP")
    parser.add_argument("--output_format", choices=['JSON', 'CSV', 'PDF'], required=True, help="Output format")

    args = parser.parse_args()
    return args
