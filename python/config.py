import json


class Config:

    data = {
        'response_file_prefix' : 'responses-',
        'user_file': 'users'
    }

    def __init__(self):
        self.load_config()

    def get_config(self, key):
        return self.data[key]

    def get_response_file_prefix(self):
        return self.data['response_file_prefix']

    def get_user_file(self):
        return self.data['user_file']

    def load_config(self, filename='config'):
        try:
            config = open(filename)
            self.data.update(json.load(config))
        except FileNotFoundError:
            print("No config file found at", filename, "using defaults.")            
        print("config")
        print(self.data)

            

