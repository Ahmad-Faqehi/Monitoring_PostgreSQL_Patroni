from jsondiff import diff
import requests
import json
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import configparser


msg = []


# fun to update the work file
def update_work(boo):
    f = open('./work.json','r')
    work = json.loads(f.read())
    work['work'] = boo
    f.close()
    f = open('./work.json','w')
    f.write(json.dumps(work))
    f.close()


# fun to check send mail or no
def okay_to_send():
    x = open('./work.json','r')
    work = json.loads(x.read())
    x.close()
    if work['work']:
        return True
    return False


# Update api.json file.
def update_file(hosts):
    for host in hosts:
        if (is_url_alive(host)):
            response = requests.get(host+"/cluster")
            data = response.json()
            with open("./api.json", 'w') as file:
                json.dump(data, file)
                file.close()
            return True
        
    return False




# Get patroni reachable
def is_url_alive(url):
    global msg
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return True
        else:
            # msg.append("There is issue with connection to Patroni API")
            return False
    except requests.ConnectionError:
        msg.append("There is issue with connection to Patroni API")
        return False
    except requests.Timeout:
        msg.append("There is issue with connection to Patroni API")
        return False


# Get the Leader
def leader(json):
    for i in json['members']:
        if i['role'] == 'leader':
            return i['name']


# Remove unnecessary json objects
def remove_unnecessary(json):
    unnecessary = ['port','api_url','timeline','tags','lag']
    for i in json['members']:
        for j in unnecessary:
            if j in i:
                del i[j]
    return json


# Create fun to Get if both is down
def cluster_status(json):
    global msg
    for i in json['members']:
        if i['state'] != 'running':
            # print(f"The node {i['name']} showing status {i['state']}")
            msg.append("The node " + i['name'] + " showing status "+ i['state'])
            return False
    # update_work(True)
    return True


# Get which node change 
def has_change(json1, json2, hosts):
    global msg
    if len(diff(json1, json2)) != 0:
        # print("T")
        for i in json1['members']:
            if i['role'] == 'leader':
                # print(f"There was failover happend, the current Leader is {i['name']}, which was {leader(json2)}")
                update_file(hosts)
                msg.append("There was failover happend, the current Leader is "+ i['name'] )
                return False
    return True

# Get if both is leader
def multi_leader(json):
    global msg
    leader_count = sum(1 for member in json['members'] if member['role'] == 'leader')
    if leader_count > 1:
        # print(f"The cluster has {leader_count} leader.")
        msg.append("The cluster has" + leader_count  + "leader.")
        return False
    return True


# Get if both is replica
def multi_replica(json):
    global msg
    replica_count = sum(1 for member in json['members'] if member['role'] == 'replica')
    if replica_count == num_host(json):
        # print("All the node in the cluster is replica.")
        msg.append("All the node in the cluster is replica.")
        return False
    return True


# Get number of hosts
def num_host(json):
    return len(json['members'])

def is_file_empty(file_path):
    return os.path.isfile(file_path) and os.path.getsize(file_path) == 0


# Create fun to append into msg
def append_into_msg(xmsg):
    global msg
    msg.append(xmsg)

#Extarct texts as string
def extract_texts(msgs):
    if type(msgs) is str:
        return msgs
    else:
        temp = ""
        for i in msgs:
            temp += "- " + i +"\n"
    return temp

def get_mails():
    config = configparser.ConfigParser()
    config.read('./config.ini')
    recipients = config.get('MAIL', 'recipients')
    mails = []
    for mail in recipients.split(','):
        mails.append(mail)
    return mails


def send_err(xmsg=""):
    global msg
    final_msg = ""
    if okay_to_send():
        config = configparser.ConfigParser()
        config.read('./config.ini')

        if len(xmsg) != 0:
            final_msg = xmsg
        else:
            final_msg = msg



        if final_msg:
            for mail in get_mails():
                recipients = mail
                message = MIMEMultipart("alternative")
                message["Subject"] = config.get('MAIL', 'Subject')
                message["From"] = config.get('MAIL', 'sendig_mail')
                message["To"] = recipients
                # write the text/plain part
                text = """\
    Dear All,

    """+ extract_texts(final_msg) + """

    This is auto email, no need for replay."""

                # convert both parts to MIMEText objects and add them to the MIMEMultipart message
                part1 = MIMEText(text, "plain")
                message.attach(part1)


                server = smtplib.SMTP(config.get('MAIL', 'host'), config.get('MAIL', 'port'))
                #server.set_debuglevel(1)
                server.login(str(config.get('MAIL', 'username')), str(config.get('MAIL', 'password')))
                server.sendmail(config.get('MAIL', 'sendig_mail'), recipients, message.as_string())
                server.quit()
                print("**  Email Send:  **")
                print(text)
                update_work(False)

