import json
import random
import string
import hashlib
import config
from datetime import date,timedelta,datetime

class RegisteredUsers:

    users = {}
    config = None

    def __init__(self, config):
        self.config = config
        self.load_users()    

    @staticmethod
    def generate_id(email, firstname, lastname):
        hasher = hashlib.sha1()
        hasher.update(email.encode())
        hasher.update(firstname.encode())
        hasher.update(lastname.encode())
        random_str = ''.join(random.choice(string.ascii_letters) for i in range(16))
        hasher.update(random_str.encode())
        return hasher.hexdigest()

    def load_users(self):
        try:
            user_file = open(self.config.get_user_file())
            self.users=json.load(user_file)
        except FileNotFoundError:
            print('No user file found, starting a new one')


    def store_registered_users(self):
        with open(self.config.get_user_file(), 'w+') as user_file:
            json.dump(self.users, user_file, indent=2)
            user_file.write("\n")

    def add_user(self, email, firstname, lastname):
        id = self.generate_id(email, firstname, lastname)
        while id in self.users: ## regenerate an idea
            print("Collision! generating new id", id)
            id = self.generate_id(email, firstname, lastname)
        self.update_user(id, email, firstname, lastname)
        return id
    
    def update_user(self, id, email, firstname, lastname):
        
        new_user = False
        
        if not id in self.users.keys():            
            print("Adding new user '{}'\n".format(email))            
            self.users[id] = dict()
            new_user = True
        else:
            print("User {} already exists, updating\n".format(email))
            
        self.users[id] = { 'email' : email,
                           'firstname' : firstname,
                           'lastname' : lastname
                          }
        
        self.store_registered_users()

        return new_user

    def update_user_extra(self, id, data):
        if not id in self.users.keys():
            raise KeyError
        
        if not 'extra' in self.users[id].keys() or self.users[id]['extra'] == None:
            self.users[id]['extra'] = data
        else:
            self.users[id]['extra'].update(data)
        self.store_registered_users()

    def remove_user_extra_entries(self, id, key_list):
        for k in key_list:
            del self.users[id]['extra'][k]
        self.store_registered_users()

    def get_user_extra(self, id):
        return self.users[id]['extra']

    def set_no_spam(self, id, delta):
        d = date.today() + delta
        self.update_user_extra(id, { 'no_spam_until': d.isoformat()})

    def get_no_spam(self, id):
        try:
            d = self.users[id]['extra']['no_spam_until']
            return date.today() <= date.fromisoformat(d)
        except KeyError:
            return False

    def set_long_response(self, id, resp, delta):
        d = date.today() + delta
        self.update_user_extra(id, {'long_response': resp,
                                    'response_valid_until': d.isoformat()})        

    def reset_long_response(self, id):
        if 'extra' in self.users[id] and 'long_response' in self.users[id]['extra']:
            self.remove_user_extra_entries(id, ['long_response', 'response_valid_until'])

    def get_long_response(self, id):
        try:
            (r,d) = (self.users[id]['extra']['long_response'],
                     self.users[id]['extra']['response_valid_until'])
            print(date.today().isoformat(), date.fromisoformat(d).isoformat(), r)
            if date.today() <= date.fromisoformat(d):
                return r
            else:
                return None
        except KeyError:
            return None
    
    def remove_user(self, id, write_file=True):
        del self.users[id]
        if write_file:
            self.store_registered_users()

    def get_id_from_email(self, email):
        # TODO outch..
        for id,u in self.users.items():
            if u['email'] == email:
                return id
        return KeyError
            
    def get_user_from_email(self, email):
        id = self.get_id_from_email(email)
        return self.get_user_from_id(id)

    def get_user_from_id(self, id):
        print(id)
        if id in self.users.keys():
            return self.users[id]
        return None

    def has_registered(self, id):
        return id in self.users.keys()

    def all_users(self):
        for u in self.users.keys():
            yield (u, self.users[u])
    
def main():

    ru = RegisteredUsers()
    ru.load_users()
    
if __name__ == '__main__':
    main()
