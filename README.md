# Slurm_Telegram_Bot
```
Telegram Bot for quick control of tasks on linux server!

Setup:
1) 
    sudo apt update
    sudo apt -y upgrade
	
2) 
    pip3 --version 
    (If pip3 is not installed, do the command: sudo apt install python3-pip)

3)
    pip3 install telegram python-telegram-bot

4) Setup for database:
    sudo apt install python3-dev lipq-dev
    pip3 install psycopg2

5) 
    pip3 install python-dotenv 
    pip3 install pexpect

6) Get telegram bot TOKEN at @BotFather with command /newbot

7) Create file ".env" and fill these values:
    TOKEN_API=
    sudo_user=
    sudo_password=
    dbname=
    user=
    password=
    host=
    port=
    Start_string=
    Help_string=
    Get_notifications_string=
    Sinfo_string=
    Squeue_all_string=
    Squeue_my_jobs_string=
    Scontrol_string=
    Unsubscribe_string=

8)
    python3 slurm_bot.py
    python3 listen_msg.py

9) Put these tasks to background of server

NOTE: Unable to start 1 bot when a bot is working with that TOKEN_API
```
