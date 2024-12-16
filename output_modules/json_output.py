import json

def output_to_json(data, file_path):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)
