import json

def create_json_file(json_file, data=None):
    try:
        with open(json_file, "w") as file:
            if data is None:
                data = []
            json.dump(data, file)
    except Exception as e:
        print(e)
        
def read_json_file(json_file, errors=None):
    try:
        with open(json_file, 'r', errors=errors) as file:
            json_object = json.load(file)
            return json_object
    except Exception as e:
        print(e)