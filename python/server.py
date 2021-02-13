import http.server
import socketserver
import sys
from urllib.parse import unquote, quote, urlparse, parse_qs, urlunparse
import registered_users as ru
import responses as resp
import send_emails as se
import config as conf
from datetime import date,timedelta,datetime
import json    

# TODO fix this
conf = conf.Config()

class Handler(http.server.BaseHTTPRequestHandler):

    config = conf
    users = ru.RegisteredUsers(config)
    responses = resp.Responses(config, users)

    # def __init__(self):
    #     print("Initializing server")

    @staticmethod
    def extract_value(query, name, required=False):
        if name in query:
            return query[name][0]
        elif not required:
            return None
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

    def respond_with_message(self, query_type, msg, msg_type = 1):
        d = {'resp_type' : query_type, 'subtype' : 'message',
             'msg_string' : msg, 'message_type' : msg_type}
        self.respond_raw(200, d)
        self.log_error('MESSAGE %s: %s', str(200), msg)
        return 200

    def respond_with_error(self, query_type, msg):
        self.log_error('ERROR')
        self.respond_with_message(query_type, msg, -1) 
        return err

    def respond_with_parse_error(self, query_type, q):
        msg = "Error: cannot parse query: '" + q + "'"
        return self.respond_with_error(query_type, msg)

    def respond_with_data(self, query_type, data):
        d = {'resp_type' : query_type, 'subtype' : 'data',
             'data' : data }
        self.log_error('RESPOND WITH DATA %s', str(data)) 
        self.respond_raw(200, d)

    def respond_with_userinfo(self, id, firstname, lastname, email):
        self.respond_with_data('userinfo', {'id': id,
                                            'firstname':firstname,
                                            'lastname':lastname,
                                            'email':email})

    def respond_with_list(self, data):
        self.respond_with_data('list', data)

    def respond_with_register_success(self, id, msg):
        self.respond_with_data('register', { 'id' : id, 'msg_string' : msg })
    

    def get_delay_from_validity(self, validity):
        if validity != None: 
            if validity == 'next_monday':
                today = date.today()
                delay = timedelta(days=-today.weekday() - 1, weeks=1)
                return delay
            elif validity.isdigit():
                delay = timedelta(days=int(validity))
                return delay            
        raise ValueError

    def process_query_response(self, qs, query):

        try: 
            id = self.extract_value(query, 'id')
            resp = self.extract_value(query, 'resp', required = True)
            validity = self.extract_value(query, 'validity')
        except ValueError:
            self.respond_with_parse_error('response', qs)
            raise ValueError
            
        user = self.users.get_user_from_id(id)
        if id != None and user != None:
            try: 
                if resp == 'no_spam': 
                    if validity != None:
                        self.users.set_no_spam(id, self.get_delay_from_validity(validity))
                    else:
                        raise ValueError

                elif resp == 'yes' or resp == 'no':
                    if validity == None:
                        self.responses.update_response(id, resp=='yes')
                    else:
                        self.responses.update_response(id, resp=='yes')
                        self.users.set_long_response(id, resp=='yes',
                                    self.get_delay_from_validity(validity))
                else:
                    raise ValueError
            except ValueError:
                self.respond_with_parse_error('response', qs)
            self.respond_with_data("response", { 'msg_string' : "C'est noté." })
        else:
            self.respond_with_message("response", "Identifiant inconnu ou non renseigné. Il faut s'inscrire pour pouvoir voir ce que font les autres.", 0)

    def process_query_userinfo(self, qs, query):
        id = None

        id = self.extract_value(query, 'id')
            
        if id == None or not self.users.has_registered(id):
            self.respond_with_message('userinfo', 'Utilisateur inconnu : '+ id, 0)
            raise ValueError;

        u = self.users.get_user_from_id(id)
        self.respond_with_userinfo(id, u['firstname'], u['lastname'], u['email'])

    def process_query_register(self, qs, query):
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
                    self.respond_with_message('register',
                                              "T'es pas dans la base, {}.".format(firstname),
                                              0)
        else:
            self.respond_with_parse_error('register', qs)


    def respond_with_register_success(self, id, msg):
        self.respond_with_data('register', { 'id' : id, 'msg_string' : msg })
    
    def process_query_userinfo(self, qs, query):
        id = None

        id = self.extract_value(query, 'id')
            
        if id == None or not self.users.has_registered(id):
            self.respond_with_message('userinfo', 'Utilisateur inconnu : '+ id, 0)
            raise ValueError;

        u = self.users.get_user_from_id(id)
        self.respond_with_userinfo(id, u['firstname'], u['lastname'], u['email'])

    def process_query_sendemail(self, qs, query):
        email = self.extract_value(query, 'email')
        
        id = None
        try :
            id = self.users.get_id_from_email(email)
        except KeyError:
            self.respond_with_message('sendemail', "Email inconnu.")
            return

        user = self.users.get_user_from_id(id)
        se.send_mail(user['email'],
                     se.create_email(id, user['email'], user['firstname'], user['lastname'] ))
        self.respond_with_message('sendemail', "Email envoyé.") 


    def process_query_list(self, qs, query):
        id = None

        id = self.extract_value(query, 'id')
            
        if id == None or not self.users.has_registered(id):
            self.respond_with_message('list', "T'es pas inscrit(e), tu peux pas voir ce que font les autres.", 0)
        elif not self.responses.has_responded(id):
            self.respond_with_message('list', "T'as pas répondu aujourd'hui, tu peux pas voir ce que font les autres.", 0)
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

    def process_query_remove(self, qs, query):
        id = self.extract_value(query, 'id')

        if id != None:
            self.users.remove_user(id)
            self.respond_with_data('remove', { "msg_string": 'Supprimé(e)' })
        else:
            self.respond_with_message('remove', "Id inconnu", 0)


    def do_GET(self):
        req = urlparse(self.path)

        query = None

        qs = req.query

        try:
            query = parse_qs(qs, strict_parsing = True)
        except ValueError as e:
            self.respond_with_parse_error('-', qs)
            raise ValueError

        print("Received Query:",qs)

        q = self.extract_value(query, 'q')

        print("query type", q)

        if q == 'userinfo':
            self.process_query_userinfo(qs, query); 
        elif q == 'list':
            self.process_query_list(qs, query)
        elif q == 'respond' or q == 'response':
            self.process_query_response(qs, query)
        elif q == 'register':
            self.process_query_register(qs, query)
        elif q == 'sendemail':
            self.process_query_sendemail(qs, query)
        elif q == 'remove':
            self.process_query_remove(qs, query)
        else:
            # default, 
            self.process_query_list(qs, query)
            # self.respond_with_parse_error('-', qs)
            # raise ValueError

        return 0

    
        
def main():

    httpd = http.server.HTTPServer((conf.get_server_ip(), conf.get_server_port()), Handler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()
        sys.exit(0)




if __name__ == '__main__':
    main()
