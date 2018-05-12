#!/usr/bin/env python
__author__ = 'ed adkins'

import socket
import time
import logging
import sys
import paramiko
import nmap
import json

FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(format=FORMAT, filename="./logs/lab_manager.log", level=logging.INFO)
LOGGER = logging.getLogger('labrat.{}'.format(__name__.rstrip('.py')))
LOGGER_OUT = logging.StreamHandler(sys.stdout)
LOGGER_OUT.setFormatter(logging.Formatter(FORMAT))
LOGGER.addHandler(LOGGER_OUT)


class DeviceManager(object):
    """
    Broker to connect to devices in the hostfile
    and either get output or configure devices.
    """
    def __init__(self, username, password, host_file):
        """
        Initialises Deviemanager with
        the device username, password and hostfile.

        Args:
            username: The device hostname.
            password: The device password.
            hostfile: A csv file containing host IP address information.
        """
        self.username = username
        self.password = password
        self.host_file = host_file

    def _json_file_reader(self):
        """ Opens and reads a CSV file containing host IP addresses.

        Args:
            csvf: A csv file containing host IP address information.

        Returns:
            A list containing host IP addresses. For example:
            ['10.0.0.1', '10.0.0.2', '10.0.0.3']
        """
        with open(self.host_file) as json_file:
            return json.load(json_file)

    def _enable_pswd(self, ssh_conn):
        ssh_conn.send("\n")
        ssh_conn.send("enable\n")
        ssh_conn.send("C15coSDA!\n")
        ssh_conn.send("terminal length 0\n")
        time.sleep(1)
        ssh_conn.recv(1000)

    def _send_data(self, commands):
        output = {}
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        for host in self._json_file_reader():
            output[host] = {}
            try:
                ssh.connect(self._json_file_reader()[host]['ipAddress'],
                            port=self._json_file_reader()[host]['port'],
                            username=self.username,
                            password=self.password,
                            look_for_keys=False,
                            allow_agent=False)
                ssh_conn = ssh.invoke_shell()
                self._enable_pswd(ssh_conn)
                for command in commands:
                    if command != '\n':
                        LOGGER.info("{0} {1} {2} {3}".format("Successfully executed:", command.lower(), "on", host))
                    ssh_conn.send(command+'\n')
                    time.sleep(2)
                    conn_output = ssh_conn.recv(50000)
                    output[host][command] = conn_output
                ssh_conn.close()
            except (paramiko.SSHException, socket.error) as socket_error:
                LOGGER.error(socket_error)
        return output


    def send_command(self, send_command):
        """ Takes a list and passes it to _send_data to configure the devices.

        Args:
            getcommand: A lists containing the commands to be configured.
        """
        return self._send_data(send_command)


class DeviceReachability(object):
    """
    Verifies the reachibility of devices using ICMP and HTTP probes.
    """
    def __init__(self, host_file):
        """ Initialises Deviemanager with the device username, password and hostfile.

        Args:
            username: The device hostname.
            password: The device password.
            hostfile: A csv file containing host IP address information.
        """
        self.host_file = host_file

    def _json_file_reader(self):
        """ Opens and reads a CSV file containing host IP addresses.

        Args:
            csvf: A csv file containing host IP address information.

        Returns:
            A list containing host IP addresses. For example:
            ['10.0.0.1', '10.0.0.2', '10.0.0.3']
        """
        with open(self.host_file) as json_file:
            return json.load(json_file)

    def _nmap_alive(self, host, port):
        """ Verifies reachability of the network device using NMAP.

        Args:
            host: A string containing the host IP Address.
            port: A string containing the host port number.

        Returns:
            True if the True response is equal to one
        """
        nm = nmap.PortScanner()
        try:
            nm.scan(host, str(port))
            if nm[host]['tcp'][port]['state'] != "open":
                return False
        except Exception:
            return False
        return True

    def device_state_tracker(self):
        devices_alive = self._json_file_reader()
        for hostname in devices_alive:
            devices_alive[hostname]['alive'] = 0
        return devices_alive

    def _get_reachability(self, device_state):
        """ Connects to the devices in hostfile and returns requested command output.

        Args:
            get_command: A string containing the requested command.

        Returns:
            A dictionary containing command output from devices
        """
        for hostname in device_state:
            if self._nmap_alive(device_state[hostname]['ipAddress'], device_state[hostname]['port']) is True:
                device_state[hostname]['alive'] = 1
            else:
                device_state[hostname]['alive'] = 0
        return device_state

    def _alive_logger(self,hostname,ip_address,port,state):
        LOGGER.info("HOST: {0} | IP: {1} | PORT: {2}...is {3}".format(hostname,
                                                                      ip_address,
                                                                      port,
                                                                      state))

    def is_alive(self):
        device_state = self.device_state_tracker()
        LOGGER.info("verifying device reachability...")
        while True:
            if device_state is not None:
                for hostname in list(self._get_reachability(device_state)):
                    if device_state[hostname]['alive'] == 1:
                        self._alive_logger(hostname,
                                           device_state[hostname]['ipAddress'],
                                           device_state[hostname]['port'],
                                           'alive')
                        del device_state[hostname]
                    else:
                        pass
            else:
                break
                LOGGER.info("all devices reachable...")

    def is_up_down(self):
        device_state = self.device_state_tracker()
        LOGGER.info("verifying device reachability...")
        for hostname in list(self._get_reachability(device_state)):
            if device_state[hostname]['alive'] == 1:
                self._alive_logger(hostname,
                                   device_state[hostname]['ipAddress'],
                                   device_state[hostname]['port'],
                                   'alive')
            else:
                self._alive_logger(hostname,
                                   device_state[hostname]['ipAddress'],
                                   device_state[hostname]['port'],
                                   'dead')