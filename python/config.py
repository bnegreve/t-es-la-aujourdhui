import json


class Config:

    data = {}

    def __init__(self):
        self.load_config()

    def get_config(self, key):
        return self.data[key]

    def get_response_file_prefix(self):
        return self.data['response_file_prefix']

    def get_user_file(self):
        return self.data['user_file']

    def get_server_ip(self):
        return self.data['server_ip']

    def get_server_port(self):
        return self.data['server_port']

    def load_config(self, filename='config'):
        try:
            config = open(filename)
        except FileNotFoundError:
            print("No config file found at", filename, "using defaults.")
            config = open('config.default')
        self.data.update(json.load(config))
        print("config")
        print(self.data)

            

