from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, Message, CallbackQuery
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
import asyncio
import pexpect
from dotenv import load_dotenv
load_dotenv()

TOKEN_API = os.getenv("TOKEN_API")
connection = psycopg2.connect(dbname=os.getenv("dbname"), user=os.getenv("user"), password=os.getenv("password"), host=os.getenv("host"),port=os.getenv("port"))

Start_string = os.getenv("Start_string")
Help_string = os.getenv("Help_string")
Get_notifications_string = os.getenv("Get_notifications_string")
Sinfo_string = os.getenv("Sinfo_string")
Squeue_all_string = os.getenv("Squeue_all_string")
Squeue_my_jobs_string = os.getenv("Squeue_my_jobs_string")
Scontrol_string = os.getenv("Scontrol_string")
Unsubscribe_string = os.getenv("Unsubscribe_string")

sudo_user = os.getenv("sudo_user")
sudo_password = os.getenv("sudo_password")

INPUT_USERNAME, INPUT_PASSWORD, JOB_ID = range(3)

def start_command(update: Update, context: CallbackContext):
    buttons = [[KeyboardButton(Start_string), KeyboardButton(Get_notifications_string), KeyboardButton(Help_string), KeyboardButton(Sinfo_string)], [KeyboardButton(Squeue_all_string), KeyboardButton(Squeue_my_jobs_string), KeyboardButton(Scontrol_string), KeyboardButton(Unsubscribe_string)]]
    reply_markup=ReplyKeyboardMarkup(buttons)
    update.message.reply_text(f"Welcome {update.effective_user.first_name} {update.effective_user.last_name} to Slurm Bot!!\nYou can call /help for more details!\nYour chat_id is {update.effective_user.id}", reply_markup=reply_markup)
   
def check_valid_username_password_in_server(username: str, password: str):
    child = pexpect.spawn(f'/usr/bin/sudo /usr/bin/login {username}', encoding='utf-8')
    child.expect_exact(f'[sudo] password for {sudo_user}: ')
    child.sendline(sudo_password)
    return_code = child.expect(['Sorry, try again', 'Password: '])
    if return_code == 0:
        child.kill(0)
        return "FAIL"
    else:
        child.sendline(password)
        return_code = child.expect(['Login incorrect', '[#\\$] '])
        if return_code == 0:
            child.kill(0)
            return "FAIL"
        elif return_code == 1:
            return "OK"

def link_telegram_chat_id_with_username_in_server(update: Update, context: CallbackContext):
    update.message.reply_text("Please enter your name in server:")
    return INPUT_USERNAME

def get_password_after_username(update: Update, context: CallbackContext):
    context.user_data["username"] = update.message.text
    update.message.reply_text("Password:")
    return INPUT_PASSWORD

def insert_username_server_to_db(update: Update, context: CallbackContext):
    cursor = connection.cursor()
    chat_id = update.message.chat_id
    password = update.message.text
    username = context.user_data["username"]
    check_result = check_valid_username_password_in_server(username, password)
    if check_result == "FAIL":
        update.message.reply_text("Your username or password is incorrect! Please choose /get_notifications or 'Starting receiving notifications about my jobs' again!")
        return ConversationHandler.END
    elif check_result == "OK":
        cursor.execute(f"select count(*) from slurm_user where username='{username}' and telegram_id={chat_id}")
        count = cursor.fetchone()[0]
        connection.commit()
        if count == 0:
            cursor.execute(f"insert into slurm_user(telegram_id, username, status) values ({chat_id}, '{username}', False)")
            connection.commit()
            update.message.reply_text(f"Welcome {update.effective_user.first_name} {update.effective_user.last_name} - {username} to our Slurm Bot!")
        elif count > 0:
            update.message.reply_text(f"You are already in our server with username: {username}")
        cursor.close()
        return ConversationHandler.END

def help_command(update: Update, context: CallbackContext):
    update.message.reply_text(f"All the commands:\n/start : To start with the bot;\n/get_notifications: To start receiving informations about your jobs in server;\n/help : To see all the commands available;\n/sinfo : To see the information of sinfo;\n/squeue_all : See the squeue of jobs of all users;\n/squeue_your_jobs: See the squeue of your jobs;\n/scontrol : See scontrol show job_id;\n/unsubscribe : To stop receiving informations about starting and ending jobs\nNOTES: If you want to change your username in our server, please call /unsubscribe first and then call /get_notifications")

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
    else: update.message.reply_text("There is 0 Node running now!")

def command_squeue_json():
    os.system("squeue --json > squeue.json")
def get_info_squeue_from_json(update: Update, context: CallbackContext):
    username = get_username_by_telegram_chat_id(update.message.chat_id)
    if username == "":
        update.message.reply_text("You are not in our server! Please choose 'Start receiving notifications about my jobs'!")
    
    else:
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
                submit_time = datetime.fromtimestamp(job["submit_time"]).strftime('%d/%m/%Y %I:%M:%S %p')
                job_state = job["job_state"]
                start_time = datetime.fromtimestamp(job["start_time"]).strftime('%d/%m/%Y %I:%M:%S %p')
                end_time = datetime.fromtimestamp(job["end_time"]).strftime('%d/%m/%Y %I:%M:%S %p')
                text = f"Username: {user_name}\nUser_id: {user_id}\nJob_id: {str(job_id)}\nJob name: {job_name}\nNodes: {job_nodes}\nPartition: {job_partition}\nSubmit time: {submit_time}\nState: {job_state}\nStart time: {start_time}\nEnd time: {end_time}"
                update.message.reply_text(text)

def command_squeue(username):
    command = f"squeue --states=all --user={username} > squeue.txt"
    os.system(command)
def get_username_by_telegram_chat_id(chat_id):
    cursor = connection.cursor()
    cursor.execute(f"select username from slurm_user where telegram_id={chat_id}")
    # Take the first username by telegram_id
    username = cursor.fetchone()
    # print(username)
    connection.commit()
    cursor.close()
    if username is None:
        return ""
    else: 
        return username[0]

def get_info_squeue_from_txt(update: Update, context: CallbackContext):
    username = get_username_by_telegram_chat_id(update.message.chat_id)
    if username == "":
        update.message.reply_text("You are not in our server! Please choose 'Start receiving notifications about my jobs'!")
    else:
        command_squeue(username)
        f = open("squeue.txt","r")
        f.readline()
        lines = f.readlines()
        if len(lines) == 0:
            update.message.reply_text("You have 0 job running right now!")
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
    if job_id.isnumeric() == True: 
        command_scontrol_show_job_jobid(job_id)
        if os.stat(f"job_{job_id}.txt").st_size == 0:
            update.message.reply_text("You just entered invalid job id!! If you want to show job id then call /scontrol again!")
        else:
            f_data = open(f"job_{job_id}.txt", "r")
            update.message.reply_text(f_data.read())
        os.system(f"rm -rf job_{job_id}.txt")
        return ConversationHandler.END
    else:
        update.message.reply_text("You must enter your job id as a number! Please enter your job id again!")
        return JOB_ID

def error_handler(update: Update, context: CallbackContext):
    print(f"ERROR: {context.error} caused by {update}")

def handle_text_message(update: Update, context: CallbackContext):
    if Start_string == update.message.text:
        start_command(update, context)
    elif Help_string == update.message.text:
        help_command(update, context)
    elif Sinfo_string == update.message.text:
        get_info_sinfo(update, context)
    elif Squeue_all_string == update.message.text:
        get_info_squeue_from_json(update, context)
    elif Squeue_my_jobs_string == update.message.text: 
        get_info_squeue_from_txt(update, context)
    elif Unsubscribe_string == update.message.text:
        unsubscribe_receive_job_message(update, context)

def unsubscribe_receive_job_message(update: Update, context: CallbackContext):
    cursor = connection.cursor()
    cursor.execute(f"delete from slurm_user where telegram_id={update.message.chat_id}")
    connection.commit()
    cursor.close()
    update.message.reply_text("You will stop receiving notifications about your jobs!! Goodbye!! To start with Slurm Bot again, call /start", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def main():
    updater: Updater = Updater(TOKEN_API, use_context=True)
    conversation_handler_input_username = ConversationHandler(
        entry_points=[CommandHandler("get_notifications", link_telegram_chat_id_with_username_in_server), MessageHandler(Filters.regex(Get_notifications_string), link_telegram_chat_id_with_username_in_server)],
        fallbacks=[],
        states={
            INPUT_USERNAME: [MessageHandler(Filters.text, get_password_after_username)],
            INPUT_PASSWORD: [MessageHandler(Filters.text, insert_username_server_to_db)]
        }
    )
    conversation_handler_input_jobid = ConversationHandler(
        entry_points=[CommandHandler("scontrol", get_input_jobid), MessageHandler(Filters.regex(Scontrol_string), get_input_jobid)],
        fallbacks=[],
        states={
            JOB_ID: [MessageHandler(Filters.text, get_info_scontrol_show_job_jobid)]
        }
    )

    updater.dispatcher.add_handler(conversation_handler_input_username) #handling /get_notifications command and "get notifications" text
    updater.dispatcher.add_handler(conversation_handler_input_jobid) #handling /scontrol command and "scontrol" text

    updater.dispatcher.add_handler(CommandHandler("start", start_command)) #handling /start command
    updater.dispatcher.add_handler(CommandHandler("help", help_command))  # handling /help command
    updater.dispatcher.add_handler(CommandHandler("sinfo", get_info_sinfo)) #handling /sinfo command
    updater.dispatcher.add_handler(CommandHandler("squeue_all", get_info_squeue_from_json)) #handling /squeue commands
    updater.dispatcher.add_handler(CommandHandler("squeue_your_jobs", get_info_squeue_from_txt)) #handling /squeue --user=username command
    updater.dispatcher.add_handler(CommandHandler("unsubscribe", unsubscribe_receive_job_message)) #handling /unsubscribe command

    updater.dispatcher.add_handler(MessageHandler(Filters.text, handle_text_message)) #handling text message
    updater.dispatcher.add_error_handler(error_handler)
    updater.start_polling()
    # Keep the program running until interrupted
    updater.idle()
if __name__ == '__main__':
    main()
