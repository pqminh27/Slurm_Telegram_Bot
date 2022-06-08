# f = open("./bash_script/test.txt", "r")
# f.readline()
# lines = f.readlines()


# f.close()
# print(lines[23])
# print(lines[23].split("=")[1])
# directory = lines[23].split("=")[1][0:-1]
# f2 = open(directory, "r")
# data = f2.read()
# print(data)
# for line in lines:
# from bot.slurm_bot import TOKEN_AP
# from dotenv import load_dotenv
# config = dotenv_values(".env")
# print(load_dotenv('TOKEN_API'))

# print(TOKEN_API)

# import json
# import os
# from dotenv import load_dotenv
# load_dotenv()

# print(os.getenv("Unsubscribe_string"))
# f = open("config.json", "r")
# config = json.load(f)
# print(config["TOKEN_API"])

# from ldap3 import Server, Connection, ALL, SUBTREE
# from ldap3.core.exceptions import LDAPException, LDAPBindError

# ldsp_server = f"ldap://195.19.32.74"
 
# # dn
# root_dn = "dc=example,dc=org"
 
# # ldap user and password
# ldap_user_name = 'student'
# ldap_password = 'bmstu'
 
# # user
# user = f'cn={ldap_user_name},root_dn'
# server = Server(ldsp_server, get_info=ALL)
 
# connection = Connection(server,
#                         user=user,
#                         password=ldap_password,
#                         auto_bind=True)
 
# print(f" *** Response from the ldap bind is \n{connection}" )


# def global_ldap_authentication(user_name, user_pwd):
#     """
#       Function: global_ldap_authentication
#        Purpose: Make a connection to encrypted LDAP server.
#        :params: ** Mandatory Positional Parameters
#                 1. user_name - LDAP user Name
#                 2. user_pwd - LDAP User Password
#        :return: None
    # """
 
    # ldap_user_name = user_name.strip()
    # ldap_user_pwd = user_pwd.strip()
    # tls_configuration = Tls(validate=ssl.CERT_REQUIRED, version=ssl.PROTOCOL_TLSv1_2)
    # server = Server('ldap://<server_name_here>:389', use_ssl=True, tls=tls_configuration)
    # conn = Connection(server, user=ldap_user_name, password=ldap_user_pwd, authentication=NTLM,
    #                   auto_referrals=False)
    # if not conn.bind():
    #     print(f" *** Cannot bind to ldap server: {conn.last_error} ")
    # else:
    #     print(f" *** Successful bind to ldap server")
    # return

# import paramiko
# import sys
# import subprocess

# results = []

# def ssh_conn():
#     client = paramiko.SSHClient()
#     client.load_system_host_keys()
#     client.connect("195.19.32.74", username="student", password="bmstu", port=3002, key_filename="/home/pm/.ssh/id_rsa")

#     username = "pqm"
#     ssh_stdin, ssh_stdout, ssh_stderr = client.exec_command("")
#     # client.exec_command("pqm")
#     # ssh_stdout = client.exec_command("ls -ld")

#     for line in ssh_stdout:
#         # print(line)
#         results.append(line.strip("\n"))
#     # print(ssh_stdout)

# ssh_conn()

# for i in results:
#     print(i.strip())

# sys.exit()

# import subprocess

# import pexpect
# import os

# username = "new1"
# password = "new1"

# child = pexpect.spawn(f"su - {username}")
# child.Pexpect(password)
# child.sendline("new1")
# child.expect("\$")
# child.sendline("cat hello.txt")

# p = subprocess.Popen(["su","-", username])
# pexpect(password)
# p.communicate("ls")

# subprocess.Popen(["su","-",password, username])

# os.system(f"su - {username}")
# os.system.

# import getpass
# import sys
# import ldap3
# import ldap

# # sys.stdout.write("Enter your username: ")
# # username = input.lower()
# # password = getpass.getpass("Enter your password: ")

# try:
#     ldap_client = ldap.initialize("ldap://ldap-server.domain")

#     ldap_client.set_option(ldap.OPT_REFERRALS,0)
#     ldap_client.simple_bind_s("{}@195.19.32.74 -p 3002".format("student"), "bmstu")
#     print("LDAP credentials are good!")
# except ldap.INVALID_CREDENTIALS:
#     ldap_client.unbind()
#     print("LDAP credentials incorrect!")

# import getpass
# import subprocess
# COMMAND = ['ls -l']
# mypass = getpass.getpass('This needs administrator privileges: ')
 
# proc = subprocess.Popen(['sudo', '-kS'] + COMMAND, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
# # proc.stdin.write(mypass + '\n')
# o, e = proc.communicate()
 
# if proc.returncode:
#     print('command failed')
# else:
#     print('success')
# print(o)
# print(e)
# subprocess.call(["su", "new1"])
# print("user switched to new1!")

import pexpect
sudo_user = 'pm'
sudo_password = "1"
user_name = "pm"
password = "new"

child = pexpect.spawn(f'/usr/bin/sudo /usr/bin/login {user_name}', encoding='utf-8')
child.expect_exact(f'[sudo] password for {sudo_user}: ')
child.sendline(sudo_password)
return_code = child.expect(['Sorry, try again', 'Password: '])
if return_code == 0:
    print('Can\'t sudo')
    print(child.after)  # debug
    child.kill(0)
else:
    child.sendline(password)
    return_code = child.expect(['Login incorrect', '[#\\$] '])
    if return_code == 0:
        print('Can\'t login')
        print(child.after)  # debug
        child.kill(0)
    elif return_code == 1:
        print('Login OK.')
        print('Shell command prompt', child.after)
