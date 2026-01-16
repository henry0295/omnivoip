#!/usr/bin/env python3
import yaml
import sys

try:
    with open('docker-compose/prod-env/docker-compose.yml', 'r') as f:
        data = yaml.safe_load(f)
    
    # Check for ports configuration
    if 'services' in data:
        for service_name, service_config in data['services'].items():
            if 'ports' in service_config:
                ports = service_config['ports']
                print(f"{service_name}:")
                print(f"  Type: {type(ports)}")
                print(f"  Value: {ports}")
                print()
                
                # Check if ports is a list
                if not isinstance(ports, list):
                    print(f"ERROR: ports in {service_name} is not a list!")
                    sys.exit(1)
    
    print("YAML is valid!")
    sys.exit(0)
    
except yaml.YAMLError as e:
    print(f"YAML Error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
