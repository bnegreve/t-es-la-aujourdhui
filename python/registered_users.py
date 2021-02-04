import json
import random
import string
import hashlib

class RegisteredUsers:

    users = {}
    
    def __init__(self):
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
            user_file = open('users.txt')
            self.users=json.load(user_file)
        except FileNotFoundError:
            print('No user file found, starting a new one')


    def store_registered_users(self):
        with open('users.txt', 'w+') as user_file:
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
                           'lastname' : lastname }
        
        self.store_registered_users()

        return new_user

    def remove_user(self, id, write_file=True):
        del self.users[id]
        if write_file:
            self.store_registered_users()

    def get_user_from_email(self, email):
        id = get_id_from_email(email)
        return self.get_user_from_id(id)

    def get_user_from_id(self, id):
        print(id)
        if not id in self.users:
            return None
        else:
            return self.users[id]

    def has_registered(self, id):
        return id in self.users.keys()
    
def main():

    ru = RegisteredUsers()
    ru.load_users()
    ru.update_user('qsd@qsd', 'jamal', 'atif')
    ru.update_user('flo@qsd', 'florian', 'sikou')
    ru.update_user('qsd@qsd', 'jamal', 'atif2')
    ru.update_user('ben@qsd', 'ben', 'bqsd')
    ru.update_user_email('qsd@qsd', 'jamal@atif')
    print(ru.get_user_from_email('jamal@atif'))
if __name__ == '__main__':
    main()
