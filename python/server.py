import http.server
import socketserver
import sys
from urllib.parse import unquote, quote, urlparse, parse_qs, urlunparse
import registered_users as ru
import responses as resp
import json    

class Handler(http.server.BaseHTTPRequestHandler):

    users = ru.RegisteredUsers()
    responses = resp.Responses()

    # def __init__(self):
    #     print("Initializing server")

    @staticmethod
    def yes_or_no(s):
        if s == 'yes':
            return 1
        elif s == 'no':
            return 0
        else:
            raise ValueError
    
    def respond_raw(self, code, data):
        datastr = json.dumps(data, ensure_ascii=False)
        print("ERROR ", code)
        self.send_response(code, code)
        self.send_header("Content-type", 'text/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(datastr.encode('utf-8'))
        print("Response ({}): ".format(datastr).encode('utf-8'));
        return code

    def respond_with_error(self, err, msg):
        data = { 'resp_type' : 'error', 'error' : err, 'error_msg' : msg }
        self.respond_raw(err, data)
        self.log_error('ERROR %s: %s', str(err), msg) 
        return err

    def respond_with_parse_error(self, q):
        msg = "Error: cannot parse query: '" + q + "'"
        return self.respond_with_error(422, msg)

    def respond_with_list(self, data):
        d = {'resp_type' : 'success', 'data' : data}
        self.respond_raw(200, d)
        self.log_error('SUCCESS %s: %s', str(200), data)
        return 200

    def respond_with_register_success(self, id, msg):
        d = {'resp_type' : 'register_success', 'id' : id, 'msg' : msg}
        self.respond_raw(200, d)
        self.log_error('SUCCESS %s: %s', str(200), d)
        return 200

    def respond_with_userinfo(self, id, firstname, lastname, email):
        d = {'resp_type' : 'userinfo', 'firstname':firstname, 'lastname':lastname, 'email':email}
        self.respond_raw(200, d)
        self.log_error('USERINFO %s: %s', str(200), firstname + ' ' + lastname + ' ' + email)
        return 200            

    def respond_with_message(self, msg):
        d = {'resp_type' : 'message', 'msg' : msg}
        self.respond_raw(200, d)
        self.log_error('MESSAGE %s: %s', str(200), msg)
        return 200

    
    def parse_today_qs(self, qs, query):

        try: 
            id = self.extract_value(query, 'id')
            resp = self.extract_value(query, 'resp', required = True)
            resp = self.yes_or_no(resp)
        except ValueError:
            self.respond_with_parse_error(qs)
            raise ValueError
            
        user = self.users.get_user_from_id(id)
        if id != None and user != None:
            print("Received response from ", user)
            self.responses.update_response(id, resp)
            self.respond_with_message("C'est noté.")
        else:
            self.respond_with_message("T'es pas inscrit(e), tu peux pas répondre")
            raise ValueError
        
        return query

    @staticmethod
    def extract_value(query, name, required=False):
        if name in query:
            return query[name][0]
        elif not required:
            return None
        else:
            raise ValueError

    def parse_userinfo_qs(self, qs, query):
        id = None

        id = self.extract_value(query, 'id')
            
        if id == None or not self.users.has_registered(id):
            self.respond_with_message('Utilisateur inconnu : '+ id)
            raise ValueError;

        u = self.users.get_user_from_id(id)
        print(u)
        self.respond_with_userinfo(id, u['firstname'], u['lastname'], u['email'])


    def parse_register_qs(self, qs, query):
        id = None
        email = None
                    
        id = self.extract_value(query, 'id')
        email = self.extract_value(query, 'email')
        firstname = self.extract_value(query, 'firstname')
        lastname = self.extract_value(query, 'lastname')
        remove = self.extract_value(query, 'remove')

        if email and firstname and lastname:
            # TODO test if someone with this email exists 
            if not id :                
                id = self.users.add_user(email, firstname, lastname)
                self.respond_with_register_success(id,
                                "Salut {}, t'as bien été ajouté.".format(firstname))
            else:
                if self.users.has_registered(id):
                    self.users.update_user(id, email, firstname, lastname)
                    self.respond_with_register_success(id,
                                                  "Salut {}, tes infos ont bien été mises à jour.".format(firstname))
                else:
                    self.respond_with_message("T'es pas dans la base, {}.".format(firstname))
        else:
            self.respond_with_parse_error(qs)


    def parse_list_qs(self, qs, query):
        id = None

        id = self.extract_value(query, 'id')
            
        if id == None or not self.users.has_registered(id):
            self.respond_with_message("T'es pas inscrit(e), tu peux pas voir.")
        elif not self.responses.has_responded(id):
            self.respond_with_message("T'as pas répondu aujourd'hui, tu peux pas voir.")
        else:
            resp_list = []
            resp = self.responses.get_list()
            # todo join
            for uid in resp.keys():
                u = self.users.get_user_from_id(uid)
                if u != None:
                    resp_list.append({'firstname' : u['firstname'],
                                      'lastname' : u['lastname'],
                                      'resp' : resp[uid]})
            self.respond_with_list(resp_list)

    def parse_remove_qs(self, qs, query):
        id = self.extract_value(query, 'id')

        if id != None:
            self.users.remove_user(id)
            self.respond_with_message("Supprimé(e)")
        else:
            self.respond_with_message("Faut un id, vois les mails que tu as reçu.")


    def do_GET(self):
        req = urlparse(self.path)

        query = None

        qs = req.query

        try:
            query = parse_qs(qs, strict_parsing = True)
        except ValueError as e:
            self.respond_with_parse_error(qs)
            raise ValueError

        q = self.extract_value(query, 'q', required=True)

        print("received Query:",q)

        if q=='userinfo':
            self.parse_userinfo_qs(qs, query); 
        elif q=='list':
            self.parse_list_qs(qs, query)            
        elif q=='respond':
            self.parse_today_qs(qs, query)
        elif q == 'register':
            self.parse_register_qs(qs, query)
        elif q == 'remove':
            self.parse_remove_qs(qs, query)
        else:
            self.respond_with_parse_error(qs)
            raise ValueError

        return 0

        
def main():

    
    # ru.update_user('qsd@qsd', 'jamal', 'atif')
    # ru.update_user('qsd@qsd', 'jamal', 'atif2')
    # ru.update_user('ben@qsd', 'ben', 'bqsd')
    # ru.update_user_email('qsd@qsd', 'jamal@atif')
    

    httpd = http.server.HTTPServer(('10.1.3.43', 8888), Handler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()
        sys.exit(0)




if __name__ == '__main__':
    main()
