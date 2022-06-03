import os
import json
import time
from datetime import datetime 
import requests
import psycopg2

f = open("config.json", "r")
config = json.load(f)
TOKEN_API = config["TOKEN_API"]
connection = psycopg2.connect(dbname=config["dbname"], user=config["user"], password=config["password"], host=config["host"],port=config["port"])


# https://api.telegram.org/bot{TOKEN_API}/sendMessage?chat_id=<chat_id>&text=Привет%20мир

# import re
# datetime_format = "%Y-%m-%dT%H:%M:%S"
# datetime_format_regex = re.compile(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$')
# def datetime_parser(dct):
#     for k, v in dct.items():
#         if isinstance(v, str) and datetime_format_regex.match(v):
#             dct[k] = datetime.strptime(v, datetime_format)
#     return dct

# time_now = datetime.now()
# current_time_now = time_now.strftime('%Y-%m-%d %I:%M:%S %p')
# print(current_time_now)

def read_file_json(filename):
    with open(filename, "r") as f:
        data = json.load(f)
        return data

def get_chat_id_from_db_by_username(username: str):
# chat_id = 1210670436
    cursor = connection.cursor()
    cursor.execute(f"select telegram_id from slurm_user where username='{username}'")
    chat_id = cursor.fetchone()[0]
    connection.commit()
    cursor.close()
    return chat_id



def command_squeue():
    os.system("squeue --json > squeue.json")
def get_info_squeue():
    command_squeue()
    data = read_file_json("squeue.json")
    # time_stamp_now = int(round(datetime.now().timestamp()))
    current_time = datetime.now()
    time_stamp_now = int(round(current_time.timestamp()))
    current_time_right_format = current_time.strftime('%Y-%m-%d %I:%M:%S %p')
    # print(current_time_right_format)
    for job in data["jobs"]:
        job_id = job["job_id"]
        job_name = job["name"]
        username = job["current_working_directory"].split("/")[2]
        # print(username)
        chat_id = get_chat_id_from_db_by_username(username)
        # job_partition = job["partition"]
        # submit_time = datetime.fromtimestamp(job["submit_time"]).strftime('%Y-%m-%d %I:%M:%S %p')
        # job_state = job["job_state"]
        # if job["start_time"] != 0:
        # start_time = datetime.fromtimestamp(job["start_time"]).strftime('%Y-%m-%d %I:%M:%S %p')
        # if job["end_time"] != 0:
        # end_time = datetime.fromtimestamp(job["end_time"]).strftime('%Y-%m-%d %I:%M:%S %p')
        # print("job_id: " + str(job_id))
        # print("name of job: " + job_name)
        # print("partition: "+job_partition)
        # print("submit time: " + submit_time)
        # print("state: " + job_state)
        # print(job["start_time"] - job["end_time"])
        start_time = datetime.fromtimestamp(job["start_time"]).strftime('%Y-%m-%d %I:%M:%S %p')
        end_time = datetime.fromtimestamp(job["end_time"]).strftime('%Y-%m-%d %I:%M:%S %p')
        if job["start_time"]-time_stamp_now >= -1 and job["start_time"]-time_stamp_now <= 1:
            start_msg = f"{username}'s {job_name} job (job_id: {job_id}) started running at {start_time}!"
            URL = "https://api.telegram.org/bot"+TOKEN_API+"/sendMessage?chat_id="+str(chat_id)+"&text="+start_msg
            requests.get(url=URL)
            # https://api.telegram.org/bot5372374960:AAGWFq5WLfldVTg-EvFJG6zao_4qbjDdQtw/sendMessage?chat_id=1210670436&text=%22Test%22
            
        if job["end_time"]-time_stamp_now >= -1 and job["end_time"]-time_stamp_now <= 1:
            end_msg = f"{username}'s {job_name} job (job_id: {job_id}) ended at {end_time}!"
            URL = "https://api.telegram.org/bot"+TOKEN_API+"/sendMessage?chat_id="+str(chat_id)+"&text="+end_msg
            requests.get(url=URL)

while True:
    get_info_squeue()
    time.sleep(1)