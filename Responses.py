import json
import hashlib
from datetime import date

class Responses:

    responses = {}

    @staticmethod
    def filenametoday():
        todaystr = date.today().isoformat()
        return 'responses-'+todaystr+'.txt'

    def load_responses(self):
        try:
            resp_file = open(self.filenametoday())
            self.responses=json.load(resp_file)
        except FileNotFoundError:
            print('No resp file found for today, starting a new one')

    def save_responses(self):
        f = self.filenametoday()
        with open(f, 'w+') as resp:
            json.dump(self.responses, resp, indent=2)
            resp.write("\n")

    def update_response(self, id, resp):
        self.responses[id] = resp
        self.save_responses()
        
    def get_response(self, id):
        return response[id]

def main():
    resp = Responses()

    resp.update_response("aaa", 0)
    resp.update_response("aaa", 1)
    resp.update_response("bbb", 1)

if __name__ == '__main__':
    main()
