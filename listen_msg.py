import os
import json
import time
from datetime import datetime 
import requests
import psycopg2
from dotenv import load_dotenv
load_dotenv()

TOKEN_API = os.getenv("TOKEN_API")
connection = psycopg2.connect(dbname=os.getenv("dbname"), user=os.getenv("user"), password=os.getenv("password"), host=os.getenv("host"),port=os.getenv("port"))

def read_file_json(filename):
    with open(filename, "r") as f:
        data = json.load(f)
        return data

def get_chat_id_from_db_by_username(username: str):
    cursor = connection.cursor()
    cursor.execute(f"select telegram_id from slurm_user where username='{username}'")
    chat_ids = cursor.fetchall()
    #1 username can have many chat_id at telegram
    ids = []
    for id in chat_ids:
        ids.append(id[0])
    # There is always at least telegram_id with username; username cannot be registered without telegram_id
    connection.commit()
    cursor.close()
    return ids


def command_squeue():
    os.system("squeue --json > squeue.json")
def get_info_squeue():
    command_squeue()
    data = read_file_json("squeue.json")
    current_time = datetime.now()
    time_stamp_now = int(round(current_time.timestamp()))
    current_time_right_format = current_time.strftime('%d/%m/%Y %I:%M:%S %p')
    for job in data["jobs"]:
        job_id = job["job_id"]
        job_name = job["name"]
        username = job["current_working_directory"].split("/")[2]
        chat_ids = get_chat_id_from_db_by_username(username)
        start_time = datetime.fromtimestamp(job["start_time"]).strftime('%d/%m/%Y %I:%M:%S %p')
        end_time = datetime.fromtimestamp(job["end_time"]).strftime('%d/%m/%Y %I:%M:%S %p')
        if job["start_time"]-time_stamp_now>-2 and job["start_time"]-time_stamp_now<2:
            for id in chat_ids:
                start_msg = f"{username}'s {job_name} job (job_id: {job_id}) started running at {start_time}!"
                URL = "https://api.telegram.org/bot"+TOKEN_API+"/sendMessage?chat_id="+str(id)+"&text="+start_msg
                requests.get(url=URL)
            
        if job["end_time"]-time_stamp_now>-2 and job["end_time"]-time_stamp_now<2:
            for id in chat_ids:
                end_msg = f"{username}'s {job_name} job (job_id: {job_id}) ended at {end_time}!"
                URL = "https://api.telegram.org/bot"+TOKEN_API+"/sendMessage?chat_id="+str(id)+"&text="+end_msg
                requests.get(url=URL)

while True:
    get_info_squeue()
    time.sleep(1)
