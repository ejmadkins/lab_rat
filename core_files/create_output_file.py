#!/usr/bin/env python
__author__ = 'ed adkins'

import os
import datetime
import logging
import sys

DATE_FORMAT = str(datetime.datetime.now().strftime("%y-%m-%d-%H-%M-%S"))
PATH = "./outputs/{0}".format(DATE_FORMAT)
FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(format=FORMAT, filename="./logs/lab_manager.log", level=logging.INFO)
LOGGER = logging.getLogger('labrat.create_output_file')
LOGGER_OUT = logging.StreamHandler(sys.stdout)
LOGGER_OUT.setFormatter(logging.Formatter(FORMAT))
LOGGER.addHandler(LOGGER_OUT)


def write_file(ip_address, command, device_output):
    """ Creates a file with the output from the device and the device IP address as the filename.

    Args:
        ip_address: A string containing the device IP address.
        device_output: A string containing the output from the device.
    """
    filepath = os.path.join(PATH, ip_address + "_" + command.replace(" ", "_") + ".txt")
    LOGGER.info('Writing device output to \'{0}\'...'.format(filepath))
    with open(filepath, 'w') as output_file:
        output_file.write(device_output)


def create_dir(ip_address, command, device_output):
    """ Creates a new directory if one does not exist with a timestamp.

    Args:
        ip_address: A string containing the device IP address.
        device_output: A string containing the output from the device.

    Returns:
        A list containing command output from devices
    """
    try:
        if not os.path.exists(PATH):
            LOGGER.info('Creating a new directory called \'{0}\' in the outputs directory...'.format(DATE_FORMAT))
            os.makedirs(PATH)
            write_file(ip_address, command, device_output)
        else:
            write_file(ip_address, command, device_output)
    except OSError as os_error:
        LOGGER.error("OS error: {0}".format(os_error))
