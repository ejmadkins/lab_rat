#!/usr/bin/env python
__author__ = 'ed adkins'

import os
import argparse
import logging
import sys
from core_files.connect import DeviceManager
from core_files.create_output_file import create_dir

FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(format=FORMAT, filename="./logs/lab_manager.log", level=logging.INFO)
LOGGER = logging.getLogger('labrat.{}'.format(__name__.rstrip('.py')))
LOGGER_OUT = logging.StreamHandler(sys.stdout)
LOGGER_OUT.setFormatter(logging.Formatter(FORMAT))
LOGGER.addHandler(LOGGER_OUT)


def get_user_args():
    """ Get user commands and return a dictionary with the user input.

    Returns:
        A dict containing the user input including username, password, host file and command
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--COMMAND", help="command to execute", required=True)
    parser.add_argument("-i", "--INPUT", help="name of hosts JSON file", required=True)
    parser.add_argument("-u", "--USERNAME", help="username", required=True)
    parser.add_argument("-p", "--PASSWORD", help="password", required=True)
    args = parser.parse_args()
    params = {key : value for key, value in args._get_kwargs()}
    return params


def get_config(un_pw_hf_cmd):
    """ Creates a file with the output from the device and the device IP address as the filename.

    Args:
        un_pw_hf_cmd: A list containing the username, password, host file and command.
    """
    host_file_path = 'host_files/' + un_pw_hf_cmd[2]
    cfg_backup = DeviceManager(un_pw_hf_cmd[0], un_pw_hf_cmd[1], host_file_path)
    for device, responses in cfg_backup.send_command(un_pw_hf_cmd[3]).items():
        for command, response in responses.items():
            formatted_output = '\n'.join(response.split('\n')[1:-1])
            create_dir(str(device), command, formatted_output)
        LOGGER.info("Config capture for {0} complete...".format(device))


if __name__ == "__main__":
    """
    Take users arguments and
    calls push_config to configure devices.
    """
    user_args = get_user_args()
    if os.path.isfile(os.path.join('./host_files', user_args['INPUT'])):
        get_config([user_args['USERNAME'],
                    user_args['PASSWORD'],
                    user_args['INPUT'],
                    user_args['COMMAND']])
        LOGGER.info("Job complete!..")
    else:
        print('> ERROR: \'{}\' does not exist'.format(user_args['INPUT']))
        print('> Files in the host_files directory:')
        for idx, host_file in enumerate(os.listdir('./host_files')):
            if not host_file.startswith('.'):
                print('  {0}: {1}'.format(idx,host_file))