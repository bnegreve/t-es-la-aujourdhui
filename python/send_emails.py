import registered_users as ru
import responses as resp
import config as conf
import smtplib, ssl

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

config = conf.Config()
users = ru.RegisteredUsers(config)
responses = resp.Responses(config, users)


def create_email(user_id, email, firstname, lastname):
    
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "T'es là?"
    msg['From'] = "tesla"
    msg['To'] = email

    url=config.get_config('index_url')
    urlid = url+'?id='+str(user_id)
    urlyes = urlid+'&q=respond&resp=yes'
    urlno = urlid+'&q=respond&resp=no'

    text = "Salut "+firstname+"!\nT'es là aujourd'hui?"
    text += "\n"
    text += "Oui: "+urlyes+"\n"
    text += "Non: "+urlno+"\n"
    text += "\n"
    text += "Oui jusqu'à la fin de la semaine: "+urlyes+"&validity=next_moday\n"
    text += "Non jusqu'à la fin de la semaine: "+urlno+"&validity=next_moday\n"
    text += "\n"
    text += "Accéder au site: "+urlid
    text += "Arrêter de spammer ma boite pendant 10 jours: "+urlid+"&q=response&resp=no_spam&validity=10'"    
    text += "Se désinscrire: "+urlid+'&q=remove'
    text += "\n"

    html = "<body>"
    html += "Salut "+firstname+"!<p>T'es à Dauphine aujourd'hui?"
    html += "\n<br/>"
    html += "<a href='"+urlyes+"'>Oui</a><br/>"
    html += "<a href='"+urlno+"'>Non</a>"
    html += "<p>"
    html += "<a href='"+urlyes+"&validity=next_moday'>Oui jusqu'à la fin de la semaine</a>\n"
    html += "<br/>"
    html += "<a href='"+urlno+"&validity=next_moday'>Non jusqu'à la fin de la semaine</a>\n"
    html += "</p>"
    html += "<p>"
    html += "<a href='"+urlid+"'>Accéder au site</a>"    
    html += "</p>"
    html += "<p>"
    html += "<a href='"+urlid+"&q=response&resp=no_spam&validity=10'>Arrêter de spammer ma boite pendant 10 jours</a><br/>"    
    html += "<a href='"+urlid+"&q=remove'>Se désinscrire</a>"    
    html += "</p>"
    html += "</body>"

    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')

    
    msg.attach(part1)
    msg.attach(part2)

    return msg


def send_mail(email, msg):
    context = ssl.create_default_context()
    smtp_server = config.get_config('smtp_server')
    smtp_port = config.get_config('smtp_port')
    smtp_user = config.get_config('smtp_user')
    smtp_password = config.get_config('smtp_password')
    sender_email = config.get_config('sender_email')
    
    with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
        server.login(smtp_user, smtp_password)
        server.sendmail(sender_email, email, msg.as_string())

def send_all_emails():

    for (id, user) in users.all_users():
        print("id = ", id, "user : ", user)
        if responses.send_email_today(id):
            print("Sending email to", user)
            send_mail(user['email'], create_email(id, user['email'], user['firstname'], user['lastname'] ))
        else:
            print("Not sending an email to",user,": to early")


def main():
    send_all_emails()

if __name__ == '__main__':
    main()
    
    


