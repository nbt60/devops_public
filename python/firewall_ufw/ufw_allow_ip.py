#!/usr/bin/python
## File : ufw_allow_ip.py
## Created : <2017-05-03>
## Updated: Time-stamp: <2017-08-03 11:48:06>
## Description :
##    Generate ip-host binding list for a list of nodes, when internal DNS is missing.
##    1. For existing nodes, allow traffic from new nodes
##    2. For new nodes, allow traffic from all nodes
##
## Sample:
##    python ./ufw_allow_ip.py --old_ip_list_file /tmp/old_ip_list --new_ip_list_file /tmp/new_ip_list \
##           --ssh_username root --ssh_port 22 --ssh_key_file ~/.ssh/id_rsa
##
##-------------------------------------------------------------------
import os, sys
import paramiko
import argparse

# multiple threading for a list of ssh servers
import Queue
import threading

import logging
log_folder = "%s/log" % (os.path.expanduser('~'))
if os.path.exists(log_folder) is False:
    os.makedirs(log_folder)
log_file = "%s/%s.log" % (log_folder, os.path.basename(__file__).rstrip('\.py'))

logging.basicConfig(filename=log_file, level=logging.DEBUG, format='%(asctime)s %(message)s')
logging.getLogger().addHandler(logging.StreamHandler())

def get_list_from_file(fname):
    l = []
    with open(fname,'r') as f:
        for row in f:
            row = row.strip()
            if row.startswith('#') or row == '':
                continue
            l.append(row)
    return l

def ufw_allow_ip_list(server_ip, ip_list, ssh_connect_args):
    [ssh_username, ssh_port, ssh_key_file, key_passphrase] = ssh_connect_args
    ssh_command = ""
    # TODO: improve this command, by using a library
    for ip in ip_list:
        ssh_command = "%s && ufw allow from %s" % (ssh_command, ip)
    if ssh_command.startswith(" && "):
        ssh_command = ssh_command[len(" && "):]

    print("Update ufw in %s" % (server_ip))
    print(ssh_command) # TODO
    # output = ""
    # try:
    #     ssh = paramiko.SSHClient()
    #     ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    #     key = paramiko.RSAKey.from_private_key_file(ssh_key_file, password=key_passphrase)
    #     ssh.connect(server_ip, username=ssh_username, port=ssh_port, pkey=key)
    #     stdin, stdout, stderr = ssh.exec_command(ssh_command)
    #     output = "\n".join(stdout.readlines())
    #     output = output.rstrip("\n")
    #     ssh.close()
    # except:
    #     return ("ERROR", "Unexpected on server: %s error: %s\n" % (server_ip, sys.exc_info()[0]))
    # return ("OK", output)

###############################################################

if __name__ == '__main__':
    # get parameters from users
    parser = argparse.ArgumentParser()
    parser.add_argument('--old_ip_list_file', required=True, \
                        help="IP list of current cluster", type=str)
    parser.add_argument('--new_ip_list_file', required=True, \
                        help="IP list of new nodes", type=str)
    parser.add_argument('--ssh_username', required=False, default="root", \
                        help="Which OS user to ssh", type=str)
    parser.add_argument('--ssh_port', required=False, default="22", \
                        help="Which port to connect sshd", type=int)
    parser.add_argument('--ssh_key_file', required=False, default="%s/.ssh/id_rsa" % os.path.expanduser('~'), \
                        help="ssh key file to connect", type=str)
    parser.add_argument('--key_passphrase', required=False, default="", \
                        help="Which OS user to ssh", type=str)

    l = parser.parse_args()
    ssh_connect_args = [l.ssh_username, l.ssh_port, l.ssh_key_file, l.key_passphrase]

    old_ip_list = get_list_from_file(l.old_ip_list_file)
    new_ip_list = get_list_from_file(l.new_ip_list_file)

    # TODO: speed up this process
    for old_ip in old_ip_list:
        ufw_allow_ip_list(old_ip, new_ip_list, ssh_connect_args)

    for new_ip in new_ip_list:
        ufw_allow_ip_list(new_ip, new_ip_list + old_ip_list, ssh_connect_args)
## File : ufw_allow_ip.py ends