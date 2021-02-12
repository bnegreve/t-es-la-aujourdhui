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
    url=config.get_config('index_url')
    
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "T'es là?"
    msg['From'] = "tesla"
    msg['To'] = email

    urlyes = url+'?id='+str(user_id)+'&q=respond&resp=yes'
    urlno = url+'?id='+str(user_id)+'&q=respond&resp=no'

    text = "Salut!\nT'es là aujourd'hui?"
    text += "\n"
    text += "Oui: "+urlyes+"\n"
    text += "Non: "+urlno+"\n"
    text += "\n"
    text += "Oui pour toute cette semaine: "+urlyes+"?validity=next_moday\n"
    text += "Non pour toute cette semaine: "+urlno+"?validity=next_moday\n"
    text += "\n"

    html = "<body>"
    html += "Salut!<p>T'es à Dauphine aujourd'hui?</p>"
    html += "\n<p>"
    html += "<a href='"+urlyes+"'>Oui</a><br/>"
    html += "<a href='"+urlno+"'>Non</a>"
    html += "<p>"
    html += "<a href='"+urlyes+"?validity=next_moday'>Oui pour toute la semaine</a>\n"
    html += "<br/>"
    html += "<a href='"+urlno+"?validity=next_moday'>Non pour toute la semaine</a>\n"
    html += "</p>"
    html += "<p>"
    html += "<a href='"+url+"'>Voir ce que font les autres</a>"    
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

for (id, user) in users.all_users():
    print("id = ", id, "user : ", user)
    if responses.send_email_today(id):
        print("Sending email to", user)
        send_mail(user['email'], create_email(id, user['email'], user['firstname'], user['lastname'] ))
    else:
        print("Not sending an email to",user,": to early")
    


