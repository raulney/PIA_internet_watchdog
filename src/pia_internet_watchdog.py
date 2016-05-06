import psutil
import socket
import time
import sys
import logging

TEST_URL = "www.google.com"
PROCESSES_TO_KILL = ['pia', 'openvpn']
PROCESSES_TO_RUN = ['C:\\Program Files\\pia_manager\\pia_manager']

class ProcList():
    def __init__(self, test_mode=False):
        self.test_mode = test_mode
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
                print self.print_and_log_message('Error getting pid #%s information' % pid)
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
                self.print_and_log_message('Killing Process: %s pid: %s' % proc.name(), proc.pid)
                proc.terminate()
            except Exception as e:
                print e

    def internet_connected(self):
        try:
            host = socket.gethostbyname(TEST_URL)
            s = socket.create_connection((host, 80), 2)
            return True
        except Exception as e:
            pass
        return False

    def run_process(self, proc_name):
        try:
            proc = psutil.Popen(proc_name)
            self.print_and_log_message('Running Process: %s pid: %s' % proc.name(), proc.pid)
        except Exception as e:
            raise

    def init_health_check(self):
        self.print_and_log_message('Internet health check started! The logs only show errors if any.')
        while True:
            if self.internet_connected():
                self.print_and_log_message('Internet Seems to be connected. Checking again in 1 minute...', print_to_console=False)
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

if __name__ == "__main__":
    main = ProcList()
