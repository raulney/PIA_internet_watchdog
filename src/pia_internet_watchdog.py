import psutil
import socket
import time
import sys
import logging
import signal
import sys
from requests import get

TEST_URL = 'www.google.com'
PROCESSES_TO_KILL = ['pia', 'openvpn']
PROCESSES_TO_RUN = ['C:\\Program Files\\pia_manager\\pia_manager']
FETCH_IP_URL = 'http://api.ipify.org'

class ProcList():
    def __init__(self, test_mode=False):
        self.test_mode = test_mode
        signal.signal(signal.SIGINT, self.signal_handler)
        self.init_logger()
        self.init_health_check()

    def fetch_processes(self):
        pids = psutil.pids()
        procs = []
        for pid in pids:
            try:
                p = psutil.Process(pid)
                procs.append(p)
            except:
                print self.print_and_log_message('Error getting pid #%s information' % pid, log_level='ERROR')
        return procs

    def get_process(self, proc_name):
        procs = []
        running_procs = self.fetch_processes()
        for proc in running_procs:
            if proc_name in proc.name():
                procs.append(proc)
        return procs

    def kill_process(self, proc_name):
        procs = self.get_process(proc_name)
        for proc in procs:
            try:
                proc.terminate()
                self.print_and_log_message('Killing Process: %s pid: %s' % proc.name(), proc.pid)
            except Exception as e:
                self.print_and_log_message(e, log_level='ERROR')

    def internet_connected(self):
        try:
            host = socket.gethostbyname(TEST_URL)
            s = socket.create_connection((host, 80), 20)
            return True
        except Exception as e:
            pass
        return False

    def run_process(self, proc_name):
        try:
            proc = psutil.Popen(proc_name)
            self.print_and_log_message('Running Process: %s pid: %s' % proc.name(), proc.pid)
        except Exception as e:
            self.print_and_log_message(e, log_level='ERROR')

    def init_health_check(self):
        self.print_and_log_message('PIA Internet WatchDog started!')
        while True:
            if self.internet_connected():
                ip = self.get_ip_address()
                self.print_and_log_message('Internet Seems to be connected. External IP: %s. Checking again in 1 minute...' % ip, print_to_console=False)
                time.sleep(60)
            else:
                self.print_and_log_message('Internet not responding, seems to be disconnected. Restarting apps...')
                self.restart_processes()
                self.print_and_log_message('Apps restarted. Checking again in 1 minute...')
                time.sleep(60)

    def restart_processes(self):
        for proc_to_kill in PROCESSES_TO_KILL:
            self.kill_process(proc_to_kill);
        time.sleep(5)
        for proc_to_run in PROCESSES_TO_RUN:
            self.run_process(proc_to_run);

    def print_and_log_message(self, message, log_level='INFO', print_to_console=True):
        if print_to_console:
            print '[%s] [%s] %s' % (time.strftime("%d/%m/%Y %H:%M:%S"), log_level, message)
        if log_level == 'INFO':
            self.logger.info(message)
        else:
            self.logger.error(message)

    def init_logger(self):
        file_name = '%s.log' % (time.strftime("%Y%m%d"))
        logging.basicConfig(filename=file_name,
                            filemode='a',
                            format='[%(asctime)s] [%(levelname)s] %(message)s',
                            datefmt='%d/%m/%Y %H:%M:%S',
                            level=logging.DEBUG)
        self.logger = logging.getLogger('pia_internet_watchdog')

    def signal_handler(self, signal, frame):
        self.print_and_log_message('PIA Internet WatchDog finished!')
        sys.exit(0)

    def get_ip_address(self):
        ip = "N/A"
        try:
            ip = get(FETCH_IP_URL).text
        except Exception as e:
            self.print_and_log_message('Could not retrieve current IP Address', log_level='ERROR', print_to_console=False)
        return ip

if __name__ == "__main__":
    main = ProcList()
