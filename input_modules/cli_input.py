import argparse

def convert_time_to_us(time_str):
    """Convert HH:MM:SS to microseconds"""
    if time_str == '0' or time_str.lower() == 'endless':
        return '0'
    try:
        h, m, s = map(int, time_str.split(':'))
        return str((h * 3600 + m * 60 + s) * 1000000)
    except ValueError:
        raise ValueError("Time must be in HH:MM:SS format or '0'/'endless' for endless mode")


class ConditionalRequiredAction(argparse.Action):
    def __init__(self, option_strings, dest, **kwargs):
        super().__init__(option_strings, dest, **kwargs)
        self.base_required = {
            'url': ['--url'],
            'username': ['-u', '--username'],
            'password': ['-p', '--password'],
            'profile_id': ['--profile_id'],
            'output': ['--output']
        }
        self.y1564_params = {
            'cir_enabled': ['-c', '--cir_enabled'],
            'eir_enabled': ['-e', '--eir_enabled'], 
            'tp_enabled': ['-t', '--tp_enabled'],
            'duration_type': ['--duration_type'],
            'duration': ['--duration'],
            'profile0_service_0_frame_size': ['--profile0_service_0_frame_size'],
            'profile0_service_0_src_mac': ['--profile0_service_0_src_mac'],
            'profile0_service_0_src_ip': ['--profile0_service_0_src_ip'],
            'profile0_service_0_dst_mac': ['--profile0_service_0_dst_mac'],
            'profile0_service_0_dst_ip': ['--profile0_service_0_dst_ip'],
            'profile0_service_count': ['--profile0_service_count'],
        }
        self.loopback_required = [
            'loopback', 'loopback_iface0_name', 'loopback_iface0_mode',
            'loopback_iface0_host', 'loopback_iface0_disabled',
            'loopback_iface1_name', 'loopback_iface1_mode', 
            'loopback_iface1_host', 'loopback_iface1_disabled',
            'loopback_duration', 'loopback_type'
        ]

    def __call__(self, parser, namespace, values=None, option_string=None):
        setattr(namespace, self.dest, True)

        # Make all non-base params optional
        for action in parser._actions:
            if hasattr(action, 'required'):
                is_base = False
                for param_list in self.base_required.values():
                    if action.option_strings and any(opt in param_list for opt in action.option_strings):
                        is_base = True
                        break
                if not is_base:
                    action.required = False

        # Handle force modes
        if option_string in ['--force_start', '--loopback_force']:
            for action in parser._actions:
                if hasattr(action, 'required'):
                    is_base = False
                    for param_list in self.base_required.values():
                        if action.option_strings and any(opt in param_list for opt in action.option_strings):
                            is_base = True
                            break
                    action.required = is_base

        # Handle loopback mode
        if option_string == '--loopback_only':
            for action in parser._actions:
                if action.dest in self.loopback_required:
                    action.required = True
        

def get_cli_input():
    parser = argparse.ArgumentParser(
        description="Y.1564/Loopback Test Configuration CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Loopback Test:
    %(prog)s --url http://example.com -u user -p pass --profile_id profile0 \\
        --loopback_only --loopback true --loopback_iface0_name porta \\
        --loopback_iface0_disabled false --loopback_iface1_name portb \\
        --loopback_iface1_disabled true --loopback_duration "00:10:00"
        
  Force Loopback:
    %(prog)s --url http://example.com -u user -p pass --profile_id profile0 --loopback_force
        

Examples:
  Force Start (minimal):
    %(prog)s --url http://example.com -u user -p pass --profile_id profile0 --output_format JSON -f
        
  Y.1564 Test:
    %(prog)s --url http://example.com -u user -p pass --profile_id profile0 --output_format JSON \\
        -c true -e false -t false --duration_type useconds --duration 10000000
        """
    )
    # Basic auth params
    auth_group = parser.add_argument_group('Authentication')
    auth_group.add_argument("--url", required=True)
    auth_group.add_argument("-u", "--username", required=True)
    auth_group.add_argument("-p", "--password", required=True)

    # Operation mode flags
    mode_group = parser.add_argument_group('Operation Mode')  
    mode_group.add_argument("-f", "--force_start", action=ConditionalRequiredAction, nargs=0)
    mode_group.add_argument("-l", "--loopback_only", action=ConditionalRequiredAction, nargs=0)
    mode_group.add_argument("--loopback_force", action=ConditionalRequiredAction, nargs=0, help="Force enable loopback for specified profile")

    # Loopback params
    loopback_group = parser.add_argument_group('Loopback Configuration')
    loopback_group.add_argument("--loopback", choices=['true', 'false'],
                               help="Enable/disable loopback test")
    loopback_group.add_argument("--loopback_iface0_name", help="Interface 0 name")
    loopback_group.add_argument("--loopback_iface0_disabled", choices=['true', 'false'],
                               help="Disable interface 0")
    loopback_group.add_argument("--loopback_iface1_name", help="Interface 1 name")
    loopback_group.add_argument("--loopback_iface1_disabled", choices=['true', 'false'],
                               help="Disable interface 1")
    loopback_group.add_argument("--loopback_duration", 
                               help="Test duration (HH:MM:SS or '0'/'endless' for endless mode)")
    loopback_group.add_argument("--loopback_type", choices=['layer2', 'layer3', 'layer4'],
                               default='layer4', help="Loopback type")

    # Y.1564 test params 
    y1564_group = parser.add_argument_group('Y.1564 Test Configuration')
    y1564_group.add_argument("--profile_id", required=True)
    y1564_group.add_argument("-c", "--cir", required=True, choices=['true', 'false'], help="Enable CIR")
    y1564_group.add_argument("-e", "--eir", required=True, choices=['true', 'false'], help="Enable EIR")
    y1564_group.add_argument("-t", "--tp", required=True, choices=['true', 'false'], help="Enable TP")
    y1564_group.add_argument("--output", choices=['JSON', 'CSV', 'PDF'], required=True, help="Output format")
    y1564_group.add_argument("--start", action='store_true', help="Start the test after setting the configuration")
    y1564_group.add_argument("--perf", action='store_true', help="Enable performance test")
    y1564_group.add_argument("--perf_duration_type", choices=['useconds', 'packets', 'bytes'], help="Performance test duration type")
    y1564_group.add_argument("--perf_duration", type=str, help="Performance test duration value")
    y1564_group.add_argument("--profile0_service_count", type=int, help="Number of services to configure in profile0")
    y1564_group.add_argument("--profile1_service_count", type=int, help="Number of services to configure in profile1")
    y1564_group.add_argument("--duration_type", required=True, choices=['useconds', 'packets', 'bytes'], help="Duration type for the test (useconds, packets, or bytes)")
    y1564_group.add_argument("--duration", required=True, help="Duration value for the test")

    # Service parameters for profile0
    for i in range(2):  # Assuming a maximum of 2 services for simplicity
        y1564_group.add_argument(f"--profile0_service_{i}_frame_size", type=int, help=f"Frame size for service {i} in profile0")
        y1564_group.add_argument(f"--profile0_service_{i}_src_mac", type=str, help=f"Source MAC for service {i} in profile0")
        y1564_group.add_argument(f"--profile0_service_{i}_src_ip", type=str, help=f"Source IP for service {i} in profile0")
        y1564_group.add_argument(f"--profile0_service_{i}_src_udp_port", type=int, help=f"Source UDP port for service {i} in profile0")
        y1564_group.add_argument(f"--profile0_service_{i}_dst_mac", type=str, help=f"Destination MAC for service {i} in profile0")
        y1564_group.add_argument(f"--profile0_service_{i}_dst_ip", type=str, help=f"Destination IP for service {i} in profile0")
        y1564_group.add_argument(f"--profile0_service_{i}_dst_udp_port", type=int, help=f"Destination UDP port for service {i} in profile0")
        y1564_group.add_argument(f"--profile0_service_{i}_vlan_count", type=int, help=f"VLAN count for service {i} in profile0")
        y1564_group.add_argument(f"--profile0_service_{i}_vlan_tags", type=str, help=f"VLAN tags for service {i} in profile0 (comma-separated list of dicts)")
        y1564_group.add_argument(f"--profile0_service_{i}_mpls_count", type=int, help=f"MPLS count for service {i} in profile0")
        y1564_group.add_argument(f"--profile0_service_{i}_mpls_labels", type=str, help=f"MPLS labels for service {i} in profile0 (comma-separated list of dicts)")
        y1564_group.add_argument(f"--profile0_service_{i}_qos_type", type=str, help=f"QoS type for service {i} in profile0")
        y1564_group.add_argument(f"--profile0_service_{i}_dscp", type=int, help=f"DSCP for service {i} in profile0")
        y1564_group.add_argument(f"--profile0_service_{i}_ecn", type=int, help=f"ECN for service {i} in profile0")
        y1564_group.add_argument(f"--profile0_service_{i}_tos", type=int, help=f"ToS for service {i} in profile0")
        y1564_group.add_argument(f"--profile0_service_{i}_precedence", type=int, help=f"Precedence for service {i} in profile0")
        y1564_group.add_argument(f"--profile0_service_{i}_loss_percents", type=str, help=f"Loss percents for service {i} in profile0")
        y1564_group.add_argument(f"--profile0_service_{i}_frame_delay_ms", type=str, help=f"Frame delay in ms for service {i} in profile0")
        y1564_group.add_argument(f"--profile0_service_{i}_delay_variation_ms", type=str, help=f"Delay variation in ms for service {i} in profile0")
        y1564_group.add_argument(f"--profile0_service_{i}_mfactor_mbps", type=str, help=f"M-factor in Mbps for service {i} in profile0")
        y1564_group.add_argument(f"--profile0_service_{i}_unordered_percents", type=str, help=f"Unordered percents for service {i} in profile0")
        y1564_group.add_argument(f"--profile0_service_{i}_cir_rate_value", type=str, help=f"CIR rate value for service {i} in profile0")
        y1564_group.add_argument(f"--profile0_service_{i}_cir_rate_units", type=str, help=f"CIR rate units for service {i} in profile0")
        y1564_group.add_argument(f"--profile0_service_{i}_cir_rate_layer", type=int, help=f"CIR rate layer for service {i} in profile0")
        y1564_group.add_argument(f"--profile0_service_{i}_eir_rate_value", type=str, help=f"EIR rate value for service {i} in profile0")
        y1564_group.add_argument(f"--profile0_service_{i}_eir_rate_units", type=str, help=f"EIR rate units for service {i} in profile0")
        y1564_group.add_argument(f"--profile0_service_{i}_eir_rate_layer", type=int, help=f"EIR rate layer for service {i} in profile0")
        y1564_group.add_argument(f"--profile0_service_{i}_tp_rate_value", type=str, help=f"TP rate value for service {i} in profile0")
        y1564_group.add_argument(f"--profile0_service_{i}_tp_rate_units", type=str, help=f"TP rate units for service {i} in profile0")
        y1564_group.add_argument(f"--profile0_service_{i}_tp_rate_layer", type=int, help=f"TP rate layer for service {i} in profile0")
        y1564_group.add_argument(f"--profile0_service_{i}_layer", type=int, help=f"Layer for service {i} in profile0")

    # Service parameters for profile1
    for i in range(2):  # Assuming a maximum of 2 services for simplicity
        y1564_group.add_argument(f"--profile1_service_{i}_frame_size", type=int, help=f"Frame size for service {i} in profile1")
        y1564_group.add_argument(f"--profile1_service_{i}_src_mac", type=str, help=f"Source MAC for service {i} in profile1")
        y1564_group.add_argument(f"--profile1_service_{i}_src_ip", type=str, help=f"Source IP for service {i} in profile1")
        y1564_group.add_argument(f"--profile1_service_{i}_src_udp_port", type=int, help=f"Source UDP port for service {i} in profile1")
        y1564_group.add_argument(f"--profile1_service_{i}_dst_mac", type=str, help=f"Destination MAC for service {i} in profile1")
        y1564_group.add_argument(f"--profile1_service_{i}_dst_ip", type=str, help=f"Destination IP for service {i} in profile1")
        y1564_group.add_argument(f"--profile1_service_{i}_dst_udp_port", type=int, help=f"Destination UDP port for service {i} in profile1")
        y1564_group.add_argument(f"--profile1_service_{i}_vlan_count", type=int, help=f"VLAN count for service {i} in profile1")
        y1564_group.add_argument(f"--profile1_service_{i}_vlan_tags", type=str, help=f"VLAN tags for service {i} in profile1 (comma-separated list of dicts)")
        y1564_group.add_argument(f"--profile1_service_{i}_mpls_count", type=int, help=f"MPLS count for service {i} in profile1")
        y1564_group.add_argument(f"--profile1_service_{i}_mpls_labels", type=str, help=f"MPLS labels for service {i} in profile1 (comma-separated list of dicts)")
        y1564_group.add_argument(f"--profile1_service_{i}_qos_type", type=str, help=f"QoS type for service {i} in profile1")
        y1564_group.add_argument(f"--profile1_service_{i}_dscp", type=int, help=f"DSCP for service {i} in profile1")
        y1564_group.add_argument(f"--profile1_service_{i}_ecn", type=int, help=f"ECN for service {i} in profile1")
        y1564_group.add_argument(f"--profile1_service_{i}_tos", type=int, help=f"ToS for service {i} in profile1")
        y1564_group.add_argument(f"--profile1_service_{i}_precedence", type=int, help=f"Precedence for service {i} in profile1")
        y1564_group.add_argument(f"--profile1_service_{i}_loss_percents", type=str, help=f"Loss percents for service {i} in profile1")
        y1564_group.add_argument(f"--profile1_service_{i}_frame_delay_ms", type=str, help=f"Frame delay in ms for service {i} in profile1")
        y1564_group.add_argument(f"--profile1_service_{i}_delay_variation_ms", type=str, help=f"Delay variation in ms for service {i} in profile1")
        y1564_group.add_argument(f"--profile1_service_{i}_mfactor_mbps", type=str, help=f"M-factor in Mbps for service {i} in profile1")
        y1564_group.add_argument(f"--profile1_service_{i}_unordered_percents", type=str, help=f"Unordered percents for service {i} in profile1")
        y1564_group.add_argument(f"--profile1_service_{i}_cir_rate_value", type=str, help=f"CIR rate value for service {i} in profile1")
        y1564_group.add_argument(f"--profile1_service_{i}_cir_rate_units", type=str, help=f"CIR rate units for service {i} in profile1")
        y1564_group.add_argument(f"--profile1_service_{i}_cir_rate_layer", type=int, help=f"CIR rate layer for service {i} in profile1")
        y1564_group.add_argument(f"--profile1_service_{i}_eir_rate_value", type=str, help=f"EIR rate value for service {i} in profile1")
        y1564_group.add_argument(f"--profile1_service_{i}_eir_rate_units", type=str, help=f"EIR rate units for service {i} in profile1")
        y1564_group.add_argument(f"--profile1_service_{i}_eir_rate_layer", type=int, help=f"EIR rate layer for service {i} in profile1")
        y1564_group.add_argument(f"--profile1_service_{i}_tp_rate_value", type=str, help=f"TP rate value for service {i} in profile1")
        y1564_group.add_argument(f"--profile1_service_{i}_tp_rate_units", type=str, help=f"TP rate units for service {i} in profile1")
        y1564_group.add_argument(f"--profile1_service_{i}_tp_rate_layer", type=int, help=f"TP rate layer for service {i} in profile1")
        y1564_group.add_argument(f"--profile1_service_{i}_layer", type=int, help=f"Layer for service {i} in profile1")

    

    args = parser.parse_args()
    return args
