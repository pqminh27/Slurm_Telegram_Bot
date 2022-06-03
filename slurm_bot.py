from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, Message, CallbackQuery
from telegram.ext import Updater, InlineQueryHandler, CommandHandler, CallbackQueryHandler, MessageHandler, CallbackContext, Filters, ConversationHandler
import sys
import json
import requests
import re
import os
from datetime import datetime
import time
import psycopg2
import aiogram

TOKEN_API = "5372374960:AAGWFq5WLfldVTg-EvFJG6zao_4qbjDdQtw"
connection = psycopg2.connect(dbname="fn1131_2021", user="student", password="bmstu", host="195.19.32.74",port="5432")

INPUT_USERNAME, JOB_ID = range(2)

def start_command(update: Update, context: CallbackContext):
    #add chat_id of user into db with name
    update.message.reply_text(f"Welcome {update.effective_user.first_name} to Slurm Bot!!\nYou can call /help for more details!\nYour chat_id is {update.effective_user.id}")
    update.message.reply_text("Please type in your username in db:")
    return INPUT_USERNAME

def insert_username_server_to_db(update: Update, context: CallbackContext):
    # cursor = connection.cursor()
    chat_id = update.message.chat_id
    username = update.message.text
    print(str(chat_id) + " - " + username)
    # cursor.execute(f"select count(*) from slurm_user where telegram_id='{chat_id}' and username='{username}'")
    # count = cursor.fetchone()[0]
    # connection.commit()
    # if not count:
    #     cursor.execute(f"insert into slurm_user(telegram_id, username, status) values ('{chat_id}', '{username}', 'False')")
    #     print(f"Inserted user {username} - {chat_id} into db")
    # else:
    #     print("You are already in our server!")
    # cursor.close()
    # update.message.reply_text(f"{update.effective_user.first_name} - {username} in our server")
    return ConversationHandler.END


def help_command(update: Update, context: CallbackContext):
    update.message.reply_text(f"All the commands:\n/start : To start;\n/help : To see all the commands;\n/sinfo : To see the information of sinfo;\n/squeue_all : See the squeue of jobs of all users;\n/squeue_your_jobs: See the squeue of your jobs;\n/scontrol {{job_id}} : See the scontrol show job id (id of job);\n/subscribe : To start receiving information about starting and ending jobs;\n/unsubscribe : To stop receiving information about starting and ending jobs")

def read_file_json(filename):
    with open(filename, "r") as f:
        data = json.load(f)
        return data

def command_sinfo():
    os.system(f"sinfo --json > sinfo.json")
def get_info_sinfo(update: Update, context: CallbackContext):
    command_sinfo()
    data = read_file_json("sinfo.json")
    nodes_count = len(data["nodes"])
    if nodes_count > 0:
        for node in data["nodes"]:
            text =  "Partition: " + node["partitions"][0] + "\nState: "+node["state"] + "\nHostname: " + node["hostname"]+ "\nNodes: " + str(nodes_count)+"\nResources: "+node["tres"]
            update.message.reply_text(text)
        # return data
    else: update.message.reply_text("There is 0 Node running now!")

def command_squeue_json():
    os.system("squeue --json > squeue.json")
def get_info_squeue_from_json(update: Update, context: CallbackContext):
    command_squeue_json()
    data = read_file_json("squeue.json")
    if len(data["jobs"]) == 0:
        update.message.reply_text("There is no job of all users running right now!")
    else:
        for job in data["jobs"]:
            user_name = job["current_working_directory"].split("/")[2]
            user_id = job["user_id"]
            job_id = job["job_id"]
            job_name = job["name"]
            job_nodes = job["nodes"]
            job_partition = job["partition"]
            submit_time = datetime.fromtimestamp(job["submit_time"]).strftime('%Y-%m-%d %I:%M:%S %p')
            job_state = job["job_state"]
            # if job["start_time"] != 0:
            start_time = datetime.fromtimestamp(job["start_time"]).strftime('%Y-%m-%d %I:%M:%S %p')
            # if job["end_time"] != 0:
            end_time = datetime.fromtimestamp(job["end_time"]).strftime('%Y-%m-%d %I:%M:%S %p')
            text = f"Username: {user_name}\nUser_id: {user_id}\nJob_id: {str(job_id)}\nJob name: {job_name}\nNodes: {job_nodes}\nPartition: {job_partition}\nSubmit time: {submit_time}\nState: {job_state}\nStart time: {start_time}\nEnd time: {end_time}"
            update.message.reply_text(text)

            # update.message.reply_text(f"job_id: {str(job_id)}")
            # update.message.reply_text(f"name of job: {job_name}")
            # update.message.reply_text(f"partition: {job_partition}")
            # update.message.reply_text(f"submit time: {submit_time}")
            # update.message.reply_text(f"state:  {job_state}")
            # if(job_state == "CANCELED"):
            #     update.message.reply_text(f"Your job is canceled!")

            # current_time_now = datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')
            # print(current_time_now)
            # start_time = datetime.fromtimestamp(job["start_time"]).strftime('%Y-%m-%d %I:%M:%S %p')
            # if current_time_now == start_time:
            #     update.message.reply_text("Your job starts now!")
            #     update.message.reply_text(f"start time: {start_time}")

            # current_time_now = datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')
            # end_time = datetime.fromtimestamp(job["end_time"]).strftime('%Y-%m-%d %I:%M:%S %p')
            # if current_time_now == end_time:
            #     update.message.reply_text("Your job just ended!")
            #     update.message.reply_text(f"end time: {end_time}")
            # print()

def command_squeue(username):
    command = f"squeue --states=all --user={username} > squeue.txt"
    os.system(command)
def get_info_squeue_from_txt(update: Update, context: CallbackContext):
    
    #db to get username
    username = "pm"
    ####################
    
    command_squeue(username)
    # print(os.path.exists("squeue.txt"))
    # Check to see if file exist or not
    # if os.path.exists("squeue.txt") == False:
    #     update.message.reply_text("You don't have any job running now!")
    # else:
    f = open("squeue.txt","r")
    f.readline()
    lines = f.readlines()
    f.close()
    for line in lines:
        datas = list(filter(lambda w: (w != ""), line.split(" ")))
        update.message.reply_text(f"Username: {datas[3]}\nJob_id: {datas[0]}\nJob name: {datas[2]}\nPartition: {datas[1]}\nState: {datas[4]}\nNodes: {datas[6]}\nRunning time: {datas[5]}\nReason: {datas[-1]}")
    
    os.system("rm -rf squeue.txt")


def command_scontrol_show_job_jobid(job_id):
    os.system(f"scontrol show job {job_id} > job_{job_id}.txt")
def get_input_jobid(update: Update, context: CallbackContext):
    update.message.reply_text("Type your job id for scontrol show job:")
    return JOB_ID

def get_info_scontrol_show_job_jobid(update: Update, context: CallbackContext):
    job_id = update.message.text
    # while update.message.text.isnumeric() == False:
        # job_id = update.message.text
        # update.message.reply_text("You just entered not number id!!!")
    if job_id.isnumeric() == True: 
        # job_id = update.message.text
        command_scontrol_show_job_jobid(job_id)
        if os.stat(f"job_{job_id}.txt").st_size == 0:
            update.message.reply_text("You just entered invalid job id!! If you want to show job id then call /scontrol again!")
            # os.system(f"rm -rf job_{job_id}.txt")
            # return JOB_ID
        else:
            f = open(f"job_{job_id}.txt", "r")
            data = f.read()
            f.close()
            update.message.reply_text(data)

        os.system(f"rm -rf job_{job_id}.txt")
        return ConversationHandler.END
    else:
        update.message.reply_text("You must enter your job id as a number! Please enter your job id again!")
        return JOB_ID

def error_handler(update: Update, context: CallbackContext):
    print(f"ERROR: {context.error} caused by {update}")

# def button(update, context):
#     query: CallbackQuery = update.callback_query
#     query.answer()
#     query.edit_message_text(text="Selected option: {}".format(query.data))

# def send_message_start_or_end_job():
#     command_squeue()
#     data = read_file_json("squeue.json")
#     if len(data["jobs"]) == 0:
#         print("There is no Job running now!")
#     else:
#         current_time_now = datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')
#         for job in data["jobs"]:
#             start_time = datetime.fromtimestamp(job["start_time"]).strftime('%Y-%m-%d %I:%M:%S %p')
#             end_time = datetime.fromtimestamp(job["end_time"]).strftime('%Y-%m-%d %I:%M:%S %p')
#             if(current_time_now == start_time):
#                 print(f"Your job started running at {start_time}!")
#             if(current_time_now == end_time):
#                 print(f"Your job ended at {end_time}")

#def get_subscribe_status_in_db():
subscribe_to_msg = False

#Change subscribe at db to True
def subscribe_receive_job_message(update: Update, context: CallbackContext):
    subscribe_to_msg = True
    update.message.reply_text("You will receive notifications about your jobs from now!!")

#Change subscribe at db to False
def unsubscribe_receive_job_message(update: Update, context: CallbackContext):
    subscribe_to_msg = False
    update.message.reply_text("You will stop receiving notifications about your jobs!!")

def main():
    #persistence=PicklePersistence(filename="bot_data"): To store data about history talking with bot
    updater: Updater = Updater(TOKEN_API, use_context=True)
    
    # updater.dispatcher.add_handler(CommandHandler("start", start_command))  # handling /start command

    conversation_handler_input_username= ConversationHandler(
        entry_points=[CommandHandler("start", start_command)],
        fallbacks=[],
        states={
            INPUT_USERNAME: [MessageHandler(Filters.text, insert_username_server_to_db)]
        }
    )

    conversation_handler_input_jobid = ConversationHandler(
        entry_points=[CommandHandler("scontrol", get_input_jobid)],
        fallbacks=[],
        states={
            JOB_ID: [MessageHandler(Filters.text, get_info_scontrol_show_job_jobid)]
        }
    )
    updater.dispatcher.add_handler(conversation_handler_input_username)
    updater.dispatcher.add_handler(conversation_handler_input_jobid)

    updater.dispatcher.add_handler(CommandHandler("help", help_command))  # handling /help command
    updater.dispatcher.add_handler(CommandHandler("sinfo", get_info_sinfo)) #handling /sinfo command
    updater.dispatcher.add_handler(CommandHandler("squeue_all", get_info_squeue_from_json)) #handling /squeue commands
    updater.dispatcher.add_handler(CommandHandler("squeue_your_jobs", get_info_squeue_from_txt)) #handling /squeue --user=username command
    # updater.dispatcher.add_handler(CommandHandler("scontrol", get_info_scontrol_show_job_jobid)) #handling /scontrol command
    
    # updater.dispatcher.add_handler(MessageHandler)
    updater.dispatcher.add_handler(CommandHandler("subscribe", subscribe_receive_job_message)) #handling /subscribe command
    updater.dispatcher.add_handler(CommandHandler("unsubscribe", unsubscribe_receive_job_message)) #handling /unsubscribe command

    
    updater.dispatcher.add_error_handler(error_handler)
    updater.start_polling()

    # Keep the program running until interrupted
    updater.idle()

if __name__ == '__main__':
    main()