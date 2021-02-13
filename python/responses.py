import registered_users
import json
import hashlib
import datetime 
from datetime import date,timedelta,datetime

class Responses:

    responses = {}
    current_file = None
    config = None
    users = None
    
    def __init__(self, config, users):
        self.config = config
        self.users = users
        self.load_long_responses()
        self.load_responses()
        

    def check_new_day(self):
        filename = self.filenametoday()
        if filename != self.current_file:
            print("new day! switching to file", filename)
            self.responses.clear()
            self.load_long_responses()
            self.load_responses()

    def filenametoday(self):
        todaystr = date.today().isoformat()
        return self.config.get_response_file_prefix()+todaystr+'.txt'

    def load_long_responses(self):
        for (id,u) in self.users.all_users():
            r = self.users.get_long_response(id)
            if r != None :
                print("Got long response from ",u['firstname'], u['lastname'], r)
                self.update_response(id, r, False)

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
        f = self.filenametoday()
        with open(f, 'w+') as resp:
            json.dump(self.responses, resp, indent=2)
            resp.write("\n")

    def update_response(self, id, resp, check_new_day=True):
        if check_new_day:
            self.check_new_day()
        if not id in self.responses:
            self.responses[id] = dict()
        self.responses[id]['resp'] = resp
        self.responses[id]['resp_date'] = datetime.now().isoformat()
        self.save_responses()
        
    def get_response(self, id):
        self.check_new_day()        
        return response[id]['resp']

    def send_email_today(self, id):
        if self.users.get_no_spam(id):
            return False
        return not id in self.responses.keys()

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
