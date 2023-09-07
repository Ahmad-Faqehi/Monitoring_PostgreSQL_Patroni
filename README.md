# Monitoring_PostgreSQL_Patroni
Monitoring a PostgreSQL database cluster managed by [Patroni](https://patroni.readthedocs.io/en/latest/#) is crucial to ensure its stability, performance, and reliability.
This script will keep monitoring the cluster and will send Email throw smtp if notice any strange behavior on the cluster.

# How it's work?
Basically the script will listen on Patroni API and collects the matrix of the cluster then will analyze it, if found something weird will send email recipients.

## Prerequset
1) Python >= 3.6
2) SMTP server

## Install the Script

Clone the project to your machine:
```shell
git clone https://github.com/Ahmad-Faqehi/Monitoring_PostgreSQL_Patroni.git
cd Monitoring_PostgreSQL_Patroni/
```

Install the requirements.txt
```shell
pip install -r requirements.txt
```

## Add the Patroni and SMTP configurations on config.ini file.
The <b>config.ini</b> has some config the you should to provide it, which is the following,

- **recipients**, the emaill address of who will reseve the emails.
- **host**, the host for smtp server
- **username**, the username of smtp
- **password**, the password of smtp
- **sendig_mail**, the email address that will send the emails to recipients
- **hosts**, the hosts for patroni node, you can add multible host and put comma between them


## Run the Script
After fill the config.ini you can run the script 
```shell
python app.py
```

You can schedule a cronjob to run the script, and it's recommend it to schedule a cronjob for overwrite <b>work.json</b> file.
```shell
0 0 * * * echo '{"work": true}' > <Path_of_Script>/work.json
```
The <b>work.json</b>  file is to make sure the email will not send twice for same error.



<!-- CONTACT -->
## Contact

Ahmad Faqehi - alfaqehi775@hotmail.com

Project Link: [https://github.com/Ahmad-Faqehi/Monitoring_PostgreSQL_Patroni](https://github.com/Ahmad-Faqehi/Monitoring_PostgreSQL_Patroni)

