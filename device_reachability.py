#!/usr/bin/env python
__author__ = 'ed adkins'

import logging
import sys
import argparse
from core_files.connect import DeviceReachability

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
    parser.add_argument("-i", "--INPUT", help="name of hosts CSV file", required=True)
    args = parser.parse_args()
    params = {key: value for key, value in args._get_kwargs()}
    return params


def verify_reachability(host_file):
    verify_reachability = DeviceReachability('{0}{1}'.format('host_files/', host_file))
    verify_reachability.is_up_down()


if __name__ == "__main__":
    """
    Take users arguments and
    calls push_config to configure devices.
    """
    user_args = get_user_args()
    verify_reachability(user_args['INPUT'])
    LOGGER.info("Job complete!..")
