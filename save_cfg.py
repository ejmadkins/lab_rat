#!/usr/bin/env python
__author__ = 'ed adkins'

import argparse
import logging
import datetime
import sys
import os
from core_files.connect import DeviceManager

PATH = ".lab_rat/configs/{0}".format(str(datetime.datetime.now().strftime("%y-%m-%d-%H-%M-%S")))

FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(format=FORMAT, filename=".lab_rat/logs/lab_manager.log", level=logging.INFO)
LOGGER = logging.getLogger('labrat.{}'.format(__name__.rstrip('.py')))
LOGGER_OUT = logging.StreamHandler(sys.stdout)
LOGGER_OUT.setFormatter(logging.Formatter(FORMAT))
LOGGER.addHandler(LOGGER_OUT)


def get_user_args():
    """
    Get user commands and return a
    dictionary with the user input.

    Returns:
        A dict containing the user input including
        username, password, host file and command
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--COMMAND", help="command to execute", required=True)
    parser.add_argument("-i", "--INPUT", help="name of hosts CSV file", required=True)
    parser.add_argument("-u", "--USERNAME", help="username of hosts", required=True)
    parser.add_argument("-p", "--PASSWORD", help="password of hosts", required=True)
    args = parser.parse_args()
    params = {key : value for key, value in args._get_kwargs()}
    return params


def save_config(un_pw_hf_cmd):
    """ Configures devices with a set of commands.

    Args:
        un_pw_hf_cmd: A list containing the
        username, password, host file and command.
    """
    host_file_path = 'host_files/' + un_pw_hf_cmd[2]
    executecmd = DeviceManager(un_pw_hf_cmd[0], un_pw_hf_cmd[1], host_file_path)
    executecmd.send_command(['copy running-config flash:{0}'.format(un_pw_hf_cmd[3]),
                             '\n'])


if __name__ == "__main__":
    """
    Take users arguments and
    calls push_config to configure devices.
    """
    user_args = get_user_args()
    if os.path.isfile(os.path.join('./host_files', user_args['INPUT'])):
        save_config(['cisco',
                     'C15coSDA!',
                     user_args['INPUT'],
                     user_args['COMMAND']])
        LOGGER.info("Job complete!..")
    else:
        print('> ERROR: \'{}\' does not exist'.format(user_args['INPUT']))
        print('> Files in the host_files directory:')
        for idx, host_file in enumerate(os.listdir('./host_files')):
            if not host_file.startswith('.'):
                print('  {0}: {1}'.format(idx,host_file))
