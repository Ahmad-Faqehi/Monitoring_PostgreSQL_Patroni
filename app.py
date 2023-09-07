import requests
import json
import configparser
from func import *

# to read configureation file
config = configparser.ConfigParser()
config.read('./config.ini')
hosts_str = config.get('PATRONI', 'hosts')
hosts = [(item.strip()) for item in hosts_str.split(',')]


for host in hosts:
    if(is_url_alive(host)):
        response = requests.get(host+"/cluster")
        data = response.json()
        continue



#Check if there is not value in var data
try:
    data
except NameError:
    send_err("The Patroni API not return result.")
    exit()



#Note: Make sure the the api.json file is exist.
if is_file_empty('./api.json'):
    update_file(hosts)


#Get content of file
f = open('./api.json')
loaded = json.loads(f.read())
f.close()

dict1 = remove_unnecessary(data)
dict2 = remove_unnecessary(loaded)


#start montring
cluster_status = cluster_status(dict1)
has_change = has_change(dict1, dict2, hosts)
multi_leader = multi_leader(dict1)
multi_replica = multi_replica(dict1)
num_hostx = True
if num_host(dict1) <= 1:
    num_hostx = False
    append_into_msg("There is missing nodes in cluster, curretn nodes is:" + num_host(dict1))
send_err()

# update work.json file if there is no issue
if cluster_status and has_change and multi_leader and multi_replica and num_hostx:
    update_work(True)