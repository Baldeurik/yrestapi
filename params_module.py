import argparse
import logging
import json

def parse_params(args, current_config):
    config_params = current_config.copy()
    config_params["y1564"]["cir_enabled"] = args.cir_enabled.lower() == 'true'
    config_params["y1564"]["eir_enabled"] = args.eir_enabled.lower() == 'true'
    config_params["y1564"]["tp_enabled"] = args.tp_enabled.lower() == 'true'

    # Настройка длительности теста
    if args.perf_enabled:
        if not args.perf_duration_type or not args.perf_duration:
            logging.error("Performance duration type and value must be provided when performance test is enabled.")
            raise ValueError("Performance duration type and value must be provided when performance test is enabled.")

        config_params["y1564"]["perf_enabled"] = True
        if args.perf_duration_type == "useconds":
            config_params["y1564"]["perf_duration"] = {
                "type": "useconds",
                "useconds": args.perf_duration,
                "packets": "0",
                "bytes": "0",
                "pld_useconds": args.perf_duration,
                "pld_bytes": "0"
            }
        elif args.perf_duration_type == "packets":
            config_params["y1564"]["perf_duration"] = {
                "type": "packets",
                "useconds": "0",
                "packets": args.perf_duration,
                "bytes": "0",
                "pld_useconds": "0",
                "pld_bytes": "0"
            }
        elif args.perf_duration_type == "bytes":
            config_params["y1564"]["perf_duration"] = {
                "type": "bytes",
                "useconds": "0",
                "packets": "0",
                "bytes": args.perf_duration,
                "pld_useconds": "0",
                "pld_bytes": "0"
            }
    else:
        config_params["y1564"]["perf_enabled"] = False

    # Настройка сервисов для profile0
    if args.profile0_service_count:
        services = []
        for service_index in range(args.profile0_service_count):
            service_params = {
                "frame_size": getattr(args, f"profile0_service_{service_index}_frame_size", 64),
                "header": {
                    "src": {
                        "mac": getattr(args, f"profile0_service_{service_index}_src_mac"),
                        "ip": getattr(args, f"profile0_service_{service_index}_src_ip"),
                        "udp_port": getattr(args, f"profile0_service_{service_index}_src_udp_port", 0)
                    },
                    "dst": {
                        "mac": getattr(args, f"profile0_service_{service_index}_dst_mac"),
                        "ip": getattr(args, f"profile0_service_{service_index}_dst_ip"),
                        "udp_port": getattr(args, f"profile0_service_{service_index}_dst_udp_port", 0)
                    },
                    "vlan": {
                        "count": getattr(args, f"profile0_service_{service_index}_vlan_count", 0),
                        "tags": json.loads(getattr(args, f"profile0_service_{service_index}_vlan_tags", "[]"))
                    },
                    "mpls": {
                        "count": getattr(args, f"profile0_service_{service_index}_mpls_count", 0),
                        "labels": json.loads(getattr(args, f"profile0_service_{service_index}_mpls_labels", "[]"))
                    },
                    "qos_type": getattr(args, f"profile0_service_{service_index}_qos_type", "diffserv"),
                    "dscp": getattr(args, f"profile0_service_{service_index}_dscp", 0),
                    "ecn": getattr(args, f"profile0_service_{service_index}_ecn", 0),
                    "tos": getattr(args, f"profile0_service_{service_index}_tos", 0),
                    "precedence": getattr(args, f"profile0_service_{service_index}_precedence", 0)
                },
                "sac": {
                    "loss_percents": getattr(args, f"profile0_service_{service_index}_loss_percents", "0.10000"),
                    "frame_delay_ms": getattr(args, f"profile0_service_{service_index}_frame_delay_ms", "1.00000"),
                    "delay_variation_ms": getattr(args, f"profile0_service_{service_index}_delay_variation_ms", "1.00000"),
                    "mfactor_mbps": getattr(args, f"profile0_service_{service_index}_mfactor_mbps", "0.10000"),
                    "unordered_percents": getattr(args, f"profile0_service_{service_index}_unordered_percents", "0.44000")
                },
                "bandwidth": {
                    "cir_rate": {
                        "value": getattr(args, f"profile0_service_{service_index}_cir_rate_value", "10.00000"),
                        "units": getattr(args, f"profile0_service_{service_index}_cir_rate_units", "mbps"),
                        "layer": getattr(args, f"profile0_service_{service_index}_cir_rate_layer", 2)
                    },
                    "eir_rate": {
                        "value": getattr(args, f"profile0_service_{service_index}_eir_rate_value", "1.00000"),
                        "units": getattr(args, f"profile0_service_{service_index}_eir_rate_units", "mbps"),
                        "layer": getattr(args, f"profile0_service_{service_index}_eir_rate_layer", 2)
                    },
                    "tp_rate": {
                        "value": getattr(args, f"profile0_service_{service_index}_tp_rate_value", "11.00000"),
                        "units": getattr(args, f"profile0_service_{service_index}_tp_rate_units", "mbps"),
                        "layer": getattr(args, f"profile0_service_{service_index}_tp_rate_layer", 2)
                    }
                },
                "layer": getattr(args, f"profile0_service_{service_index}_layer", 2)  # Добавляем слой
            }
            logging.debug(f"Service {service_index} params for profile0: {json.dumps(service_params, indent=2)}")
            services.append(service_params)
        config_params["y1564"]["services"] = services

    # Настройка сервисов для profile1
    if args.profile1_service_count:
        services = []
        for service_index in range(args.profile1_service_count):
            service_params = {
                "frame_size": getattr(args, f"profile1_service_{service_index}_frame_size", 64),
                "header": {
                    "src": {
                        "mac": getattr(args, f"profile1_service_{service_index}_src_mac"),
                        "ip": getattr(args, f"profile1_service_{service_index}_src_ip"),
                        "udp_port": getattr(args, f"profile1_service_{service_index}_src_udp_port", 0)
                    },
                    "dst": {
                        "mac": getattr(args, f"profile1_service_{service_index}_dst_mac"),
                        "ip": getattr(args, f"profile1_service_{service_index}_dst_ip"),
                        "udp_port": getattr(args, f"profile1_service_{service_index}_dst_udp_port", 0)
                    },
                    "vlan": {
                        "count": getattr(args, f"profile1_service_{service_index}_vlan_count", 0),
                        "tags": json.loads(getattr(args, f"profile1_service_{service_index}_vlan_tags", "[]"))
                    },
                    "mpls": {
                        "count": getattr(args, f"profile1_service_{service_index}_mpls_count", 0),
                        "labels": json.loads(getattr(args, f"profile1_service_{service_index}_mpls_labels", "[]"))
                    },
                    "qos_type": getattr(args, f"profile1_service_{service_index}_qos_type", "diffserv"),
                    "dscp": getattr(args, f"profile1_service_{service_index}_dscp", 0),
                    "ecn": getattr(args, f"profile1_service_{service_index}_ecn", 0),
                    "tos": getattr(args, f"profile1_service_{service_index}_tos", 0),
                    "precedence": getattr(args, f"profile1_service_{service_index}_precedence", 0)
                },
                "sac": {
                    "loss_percents": getattr(args, f"profile1_service_{service_index}_loss_percents", "0.10000"),
                    "frame_delay_ms": getattr(args, f"profile1_service_{service_index}_frame_delay_ms", "1.00000"),
                    "delay_variation_ms": getattr(args, f"profile1_service_{service_index}_delay_variation_ms", "1.00000"),
                    "mfactor_mbps": getattr(args, f"profile1_service_{service_index}_mfactor_mbps", "0.10000"),
                    "unordered_percents": getattr(args, f"profile1_service_{service_index}_unordered_percents", "0.44000")
                },
                "bandwidth": {
                    "cir_rate": {
                        "value": getattr(args, f"profile1_service_{service_index}_cir_rate_value", "10.00000"),
                        "units": getattr(args, f"profile1_service_{service_index}_cir_rate_units", "mbps"),
                        "layer": getattr(args, f"profile1_service_{service_index}_cir_rate_layer", 2)
                    },
                    "eir_rate": {
                        "value": getattr(args, f"profile1_service_{service_index}_eir_rate_value", "1.00000"),
                        "units": getattr(args, f"profile1_service_{service_index}_eir_rate_units", "mbps"),
                        "layer": getattr(args, f"profile1_service_{service_index}_eir_rate_layer", 2)
                    },
                    "tp_rate": {
                        "value": getattr(args, f"profile1_service_{service_index}_tp_rate_value", "11.00000"),
                        "units": getattr(args, f"profile1_service_{service_index}_tp_rate_units", "mbps"),
                        "layer": getattr(args, f"profile1_service_{service_index}_tp_rate_layer", 2)
                    }
                },
                "layer": getattr(args, f"profile1_service_{service_index}_layer", 2)  # Добавляем слой
            }
            logging.debug(f"Service {service_index} params for profile1: {json.dumps(service_params, indent=2)}")
            services.append(service_params)
        config_params["y1564"]["services"] = services

    # Настройка loopback
    if not hasattr(args, 'loobpack_force') or not args.loopback_force:
        config_params["loopback"] = {
            "status": args.loopback_status.lower() == 'true',
            "trial": {
                "ifaces": {
                    "0": {
                        "name": args.loopback_iface0_name,
                        "disabled": args.loopback_iface0_disabled.lower() == 'true'
                    },
                    "1": {
                        "name": args.loopback_iface1_name,
                        "disabled": args.loopback_iface1_disabled.lower() == 'true'
                    }
                },
                "wait_time_ms": args.loopback_wait_time_ms,
                "learn_time_ms": args.loopback_learn_time_ms
            },
            "loopback": {
                "duration_us": args.loopback_duration_us,
                "type": args.loopback_type
            }
        }

    logging.debug(f"Updated config params: {json.dumps(config_params, indent=2)}")
    return config_params
