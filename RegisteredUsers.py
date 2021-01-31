import json
import hashlib

class RegistredUsers:

    users = {}

    def load_users(self):
        try:
            user_file = open('users.txt')
            self.users=json.load(user_file)
        except FileNotFoundError:
            print('No user file found, starting a new one')

    def store_registred_users(self):
        with open('users.txt', 'w+') as user_file:
            json.dump(self.users, user_file, indent=2)
            user_file.write("\n")

    def update_user_email(self, old_email, new_email):
        
        hasher = hashlib.sha1()
        hasher.update(old_email.encode())
        old_id = hasher.hexdigest()

        if not old_id in self.users:
            print("Cannot find user {}".format(old_email))
            raise ValueError

        hasher = hashlib.sha1()
        hasher.update(new_email.encode())
        new_id = hasher.hexdigest()

        user = self.users[old_id]
        print(user)
        user['email'] = new_email
        self.remove_user(old_id, False)
        self.update_user(new_email, user['firstname'], user['lastname'])
    
    def update_user(self, email, firstname, lastname):

        hasher = hashlib.sha1()
        hasher.update(email.encode())
        id = hasher.hexdigest()

        print("searching for user ", id, email.encode())

        if not id in self.users.keys():
            print("Adding new user '{}'\n".format(email))
            self.users[id] = dict()
        else:
            print("User {} already exists, updating\n".format(email))
            
        self.users[id] = { 'email' : email,
                           'firstname' : firstname,
                           'lastname' : lastname }
        
        self.store_registred_users()

    def remove_user(self, id, write_file=True):
        del self.users[id]
        if write_file:
            self.store_registred_users()

    def get_user_from_email(self, email):
        hasher = hashlib.sha1()
        hasher.update(email.encode())
        id = hasher.hexdigest()
        return self.get_user_from_id(id)

    def get_user_from_id(self, id):
        if not id in self.users.keys():
            return None
        else:
            return self.users[id]
        
def main():

    ru = RegistredUsers()
    ru.load_users()
    ru.update_user('qsd@qsd', 'jamal', 'atif')
    ru.update_user('flo@qsd', 'florian', 'sikou')
    ru.update_user('qsd@qsd', 'jamal', 'atif2')
    ru.update_user('ben@qsd', 'ben', 'bqsd')
    ru.update_user_email('qsd@qsd', 'jamal@atif')
    print(ru.get_user_from_email('jamal@atif'))
if __name__ == '__main__':
    main()
