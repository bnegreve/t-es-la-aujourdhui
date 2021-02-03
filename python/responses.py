import json
import hashlib
from datetime import date

class Responses:

    responses = {}
    current_file = None
    
    def __init__(self):
        self.load_responses()

    def check_new_day(self):
        filename = self.filenametoday()
        if filename != self.current_file:
            print("new day! switching to file", filename)
            self.responses.clear()
            self.load_responses()

    @staticmethod
    def filenametoday():
        todaystr = date.today().isoformat()
        return 'responses-'+todaystr+'.txt'

    def load_responses(self):
        try:
            filename = self.filenametoday()
            resp_file = open(filename)
            self.responses=json.load(resp_file)
            self.current_file = filename
            print("Loading response file", filename)
        except FileNotFoundError:
            self.current_file = self.filenametoday()
            print('No resp file found for today, starting a new one')
            

    def save_responses(self):
        self.check_new_day()

        f = self.filenametoday()
        with open(f, 'w+') as resp:
            json.dump(self.responses, resp, indent=2)
            resp.write("\n")

    def update_response(self, id, resp):
        self.responses[id] = resp
        self.save_responses()
        
    def get_response(self, id):
        self.check_new_day()        
        return response[id]

    def has_responded(self, id):
        self.check_new_day()
        return id in self.responses.keys()

    def get_list(self):
        self.check_new_day()
        return self.responses

def main():
    resp = Responses()

    resp.update_response("aaa", 0)
    resp.update_response("aaa", 1)
    resp.update_response("bbb", 1)

if __name__ == '__main__':
    main()
