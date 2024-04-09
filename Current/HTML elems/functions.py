import os
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoAlertPresentException
from selenium.common import NoSuchElementException, StaleElementReferenceException, InvalidSelectorException, \
    ElementNotSelectableException
from selenium.common.exceptions import TimeoutException

import time
import multiprocessing
import replay_0
import argparse
import os
import subprocess
from pyvirtualdisplay import Display
from xvfbwrapper import Xvfb
import sys
import random
import math
import signal
import inspect
import shutil
import logging
from datetime import datetime
from base_code import *
import functools


def cleanup_tmp():
    files_to_delete = []

    # List all files in the temporary directory
    all_files = os.listdir('/tmp')

    # Filter out files that start with the specified characters
    for file_name in all_files:
        if '.org.chromium' in file_name or '.com.google.Chrome' in file_name or '.X11' in file_name:
            #  or 'go-build' in file_name:
            files_to_delete.append(os.path.join('/tmp', file_name))

    # Delete the files
    for file_path in files_to_delete:
        try:
            subprocess.run(["sudo", "rm", "-rf", file_path], check=True)
            # shutil.rmtree(file_path)
            print(f"Deleted: {file_path}")
        except Exception as e:
            print(f"Error deleting {file_path}: {e}")


def cleanup_chrome():
    os.system('pkill chrome')
    time.sleep(5)


def cleanup_X():
    os.system('pkill Xvfb')
    time.sleep(5)


def error_catcher(e, driver, tries, url):
    error = ''
    if driver.tries != 3:
        driver.reinitialize()
        tries += 1
        return tries

    # if isinstance(e, ElementClickInterceptedException):
    #     error = "N/A - Element Click Intercepted"
    if isinstance(e, ElementNotSelectableException):
        error = "N/A - Not Selectable"
    elif isinstance(e, StaleElementReferenceException):
        error = "StaleElementReferenceException"
    elif isinstance(e, NoSuchElementException):
        error = "N/A - No such Element"
    elif isinstance(e, InvalidSelectorException):
        error = "N/A - InvalidSelectorException"
    elif isinstance(e, IndexError):
        error = e
    elif isinstance(e, TimeoutError):
        print("Timeout")
        # write_noscan_row(url)
        tries = 1
        driver.tries = 1
        driver.curr_elem += 1
        print("TIME OUT EERRORRR")
        return tries
    else:
        error = str(e).split("\n")[0]
    return error


def timeout(seconds):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            def handler(signum, frame):
                raise TimeoutError

            signal.signal(signal.SIGALRM, handler)
            signal.alarm(seconds)

            result = func(*args, **kwargs)
            signal.alarm(0)
            return result

        return wrapper

    return decorator


def error(site, html, fname, err):
    f = open('error.txt', 'a')
    f.write(f"Time: {datetime.now().strftime('%Y-%m-%d - %H:%M:%S')}\n")
    f.write(f'Site Name: {site}\n')
    f.write(f'HTML Object: {html}\n')
    f.write(f'Function Name: {fname}\n')
    f.write(f'Error: {err}\n')
    f.close()


def check_port(port):
    try:
        # Run netstat command and grep the port
        result = subprocess.check_output(['netstat', '-tulpn'], text=True)
        if str(port) in result:
            return True
        else:
            return False
    except subprocess.CalledProcessError as e:
        error('', '', inspect.currentframe().f_code.co_name, e)
        return False
    except Exception as e:
        error('', '', inspect.currentframe().f_code.co_name, e)
        return False


def divide_chunks(l, n):
    # looping till length l
    for i in range(0, len(l), n):
        yield l[i:i + n]


def is_loaded(webdriver):
    return webdriver.execute_script("return document.readyState") == "complete"


def wait_until_loaded(webdriver, timeout=30, period=0.25, min_time=0):
    start_time = time.time()
    mustend = time.time() + timeout
    while time.time() < mustend:
        if is_loaded(webdriver):
            if time.time() - start_time < min_time:
                time.sleep(min_time + start_time - time.time())
            return True
        time.sleep(period)
    return False


def remove_popup(driver):
    print('popup:', driver.current_url)
    close_button = []
    close_anchor = []
    # Find the close button (this uses a common convention of 'x' or 'close' text)
    try:
        close_button = driver.find_elements(By.XPATH,
                                            "//button[contains(translate(., 'CLOSE', 'close'), 'close') or contains(translate(@aria-label, 'CLOSE', 'close'), 'close')]")
        close_anchor = driver.find_elements(By.XPATH,
                                            "//a[contains(translate(., 'CLOSE', 'close'), 'close') or contains(translate(@aria-label, 'CLOSE', 'close'), 'close')]")
    except Exception as e:
        # print(close_button, close_anchor)
        error(driver.current_url, '', inspect.currentframe().f_code.co_name, e)
        # print('close_button find element error', 1, e)

    close_button.extend(close_anchor)
    if len(close_button) > 0:
        for i in close_button:
            try:
                # print(i.text)
                i.click()

            except Exception as e:
                error(driver.current_url, '', inspect.currentframe().f_code.co_name, e)
                # print('popup', 2, e)


# could possibly make the driver stale. plz check!
def remove_alert(driver):
    print('alert:', driver.current_url)
    alert_find = 1
    # Alert
    try:
        # Wait for the alert to be present
        WebDriverWait(driver, 5).until(EC.alert_is_present())
    except Exception as e:
        alert_find = 0
        # error(inspect.currentframe().f_code.co_name, e)
        # print("No alert present.", 1, e)

    # Wait for the modal to be visible
    try:
        WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.XPATH, "//*[contains(@class, 'modal') and contains(@role, 'dialog')]"))
        )
    except Exception as e:
        alert_find = 0
        # print('modal element not found', 2, e)
        # error(inspect.currentframe().f_code.co_name, e)

    if alert_find:
        try:
            # Switch to the alert
            alert = driver.switch_to.alert

            # You can also retrieve alert text if needed: alert_text = alert.text

            # Accept the alert (clicks "Ok")
            alert.accept()

            # If you need to dismiss the alert (clicks "Cancel"), use: alert.dismiss()
        except Exception as e:
            error(driver.current_url, '', inspect.currentframe().f_code.co_name, e)
            # print("couldn't switch to alert", 3, e)


def remove_cmp_banner(options):
    options.add_extension(f'/home/mitch/work/pes/measurements/extensions/extn_crx/Consent-O-Matic.crx')
    return options


# this removes captcha and brings determinism
def use_catapult(options, fname, port1, port2):
    folder_path = f"/home/mitch/work/pes/measurements/break/html_elements/wpr_data/{fname}_{port1}"
    if not os.path.exists(folder_path):
        # Create the folder
        os.makedirs(folder_path)

    # options.add_argument(f'--user-data-dir={folder_path}')
    # options.add_argument(folder_path)
    options.add_argument(
        f'--host-resolver-rules=MAP *:80 127.0.0.1:{port1},MAP *:443 127.0.0.1:{port2},EXCLUDE localhost')
    options.add_argument(
        '--ignore-certificate-errors-spki-list=PhrPvGIaAMmd29hj8BCZOq096yj7uMpRNHpn5PDxI6I=,2HcXCSKKJS0lEXLQEWhpHUfGuojiU0tiT5gOF9LP6IQ=')
    return options


def check_if_ports_open(ports_list):
    for port in ports_list:
        pid1 = get_pid_by_port(port)
        if pid1 == None:
            print(port)
            time.sleep(100)
            return False
    return True


def get_used_ports():
    # Execute the ss command to get a list of used ports
    result = subprocess.run(['ss', '-tuln'], stdout=subprocess.PIPE, text=True)
    lines = result.stdout.split('\n')

    used_ports = set()
    for line in lines:
        if 'LISTEN' in line:
            parts = line.split()
            # Extract the port number from the last column, which is in the form *:port or [::]:port
            port = parts[-1].split(':')[-1]
            if port.isdigit():
                used_ports.add(int(port))
    return used_ports


def get_ports(max_ports=200, start_port=10001):
    used_ports = get_used_ports()
    available_ports = []

    for port in range(start_port, 65536):
        if len(available_ports) >= max_ports:
            break
        if port not in used_ports:
            available_ports.append(port)

    return available_ports


def start_servers(replay, num_servers, extn, reset, ports_list, start_port):
    if reset == 1:
        # if reset, the ports list remain the same for the filename to be the same
        stop_servers(ports_list)
    ports_list = get_ports(num_servers * 2, start_port)
    if not os.path.exists('/home/mitch/work/pes/measurements/break/html_elements/archive'):
        os.makedirs('/home/mitch/work/pes/measurements/break/html_elements/archive')

    processes = []

    folder_path = f'/home/mitch/work/pes/measurements/break/html_elements/wpr_data/{extn}'
    if not os.path.exists(folder_path):
        # Create the folder
        os.makedirs(folder_path)

    original_directory = os.getcwd()
    target_directory = '/home/mitch/go/src/catapult/web_page_replay_go/'

    # Change to the target directory
    os.chdir(target_directory)

    port = 0
    counter = 0
    # for counter in range(num_servers):
    while True:
        if counter == num_servers:
            break
        temp_port1 = ports_list[port]
        temp_port2 = ports_list[port + 1]
        print(f'starting servers with ports: {temp_port1} {temp_port2}')
        try:
            if replay:
                # cmd = ['go', 'run', 'src/wpr.go', 'replay', '--http_port', str(temp_port1), '--https_port', str(temp_port2), f'{archive_path}/{extn}_{counter}.wprgo']
                cmd = ['go', 'run', 'src/wpr.go', 'record', '--http_port', str(temp_port1), '--https_port',
                       str(temp_port2), f'{archive_path}/{extn}_{counter}.wprgo']
            else:
                cmd = ['go', 'run', 'src/wpr.go', 'record', '--http_port', str(temp_port1), '--https_port',
                       str(temp_port2),
                       f'/home/mitch/work/pes/measurements/break/html_elements/archive/{extn}_{counter}.wprgo']

            process = subprocess.Popen(cmd, env=os.environ.copy(), stdout=sys.stdout, stderr=sys.stdout)
            print('start servers', process, process.pid)
            processes.append(process)
            # os.system(" ".join(cmd))
            for i in range(10):
                print(f'Waiting for port {temp_port1} to be occupied')
                time.sleep(2)
                if check_port(temp_port1):
                    break

            if not check_port(temp_port1):
                process.kill()
                processes = processes[:-1]
                continue

        except subprocess.TimeoutExpired as t:
            print(f'Timeout for num_server: {index}')
            # sys.exit(1)
        except subprocess.CalledProcessError as e:
            # print(f'Error for num_server: {index}')
            error('', '', inspect.currentframe().f_code.co_name, e)
            # sys.exit(1)

        except Exception as e:
            error('', '', inspect.currentframe().f_code.co_name, e)
            # print(e)
            # sys.exit(1)

        port += 2
        counter += 1

    os.chdir(original_directory)

    return processes, ports_list


def stop_servers(ports_list):
    for port in ports_list:
        try:
            pid = get_pid_by_port(port)
            print('pid:', pid)

            if pid != None:
                os.kill(int(pid), signal.SIGINT)
                time.sleep(2)
            else:
                print(f'{port} is already closed')
            ports_list.remove(port)
        except ProcessLookupError:
            print(f"No process with PID {pid} found.")
        except PermissionError:
            print(f"Permission denied to send signal to process {pid}.")
        except Exception as e:
            # print(e)
            error('', '', inspect.currentframe().f_code.co_name, e)

    return ports_list


def get_pid_by_port(port):
    try:
        output = subprocess.check_output(['lsof', '-i', f'tcp:{port}']).decode()
    except subprocess.CalledProcessError as e:
        # print("Error:", subprocess.check_output(['lsof', '-i', 'tcp']).decode())
        return None
    except Exception as e:
        error('', '', inspect.currentframe().f_code.co_name, e)
        return None

    for line in output.splitlines():
        if "LISTEN" in line:
            parts = line.split()
            return parts[1]  # PID is typically in the second column
    return None


def run(site, extn, replay, temp_port1, temp_port2, driver_dict, display_num, html_lst):
    if not os.path.exists('/home/mitch/work/pes/measurements/break/html_elements/logs'):
        os.makedirs('/home/mitch/work/pes/measurements/break/html_elements/logs')
    logging.basicConfig(filename="logs/debug.log", filemode="w", format="%(name)s → %(levelname)s: %(message)s",
                        level=logging.INFO)
    # Prepare Chrome
    options = Options()
    options.set_capability('goog:logginPrefs', {'browser': 'ALL'})
    options.add_argument("start-maximized")
    # options.add_argument("--disable-dev-shm-usage")
    # options.add_argument("--no-sandbox")
    # options.add_argument("--disable-animations")
    # options.add_argument("--disable-web-animations")
    # options.add_argument("--disable-gpu")

    # options.add_argument("--disable-features=IsolateOrigins,site-per-process")
    # options.add_argument("--disable-features=AudioServiceOutOfProcess")
    options.add_argument(
        "user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36")
    options.binary_location = "/home/mitch/work/pes/chrome_113/chrome"

    # # only use when vdisplay off
    # options.add_argument("--window-size=1920,1280")

    options = remove_cmp_banner(options)
    # options = use_catapult(options, extn, temp_port1, temp_port2)

    if extn != 'control' and extn != 'manual':
        options.add_extension(f'/home/mitch/work/pes/measurements/extensions/extn_crx/{extn}.crx')

    # display number
    os.environ['DISPLAY'] = f":{display_num}"

    retval = driver_dict.initialize(options, 3, site)
    if retval == 0:
        e = f'error open browser instance for extn:{extn}'
        error(site, '', inspect.currentframe().f_code.co_name, e)
        driver_dict = None
        return

    for html in html_lst:
        driver_dict.set_html_obj(html)
        if replay == 0:  # can add clicking on the buttons
            #### Manual Analysis
            # scan + click
            try:
                # print('aaya')
                url = site
                if driver_dict.load_site(url):

                    key = ''
                    if 'www' in site:
                        key = site.split('www.')[1]
                    else:
                        key = site.split('://')[1]
                    # print(f'ss for {html} and site {url}')
                    driver_dict.take_ss(f'{key}.png')
                    # scroll
                    driver_dict.scroll()

                    # scan page
                    driver_dict.scan_page()
            except TimeoutException as e:
                print(f"Timeout url:{url}")
                e = str(e).split("\n")[0]
                error(site, '', inspect.currentframe().f_code.co_name, e)

            except Exception as e:
                e = str(e).split("\n")[0]
                error(site, '', inspect.currentframe().f_code.co_name, e)

        if replay == 1:
            driver_dict.replay_initialize()
            # click and compare
            tries = 1
            while driver_dict.curr_site > -1:
                try:
                    driver_dict.click_on_elms(tries)
                except Exception as e:
                    result = error_catcher(e, driver_dict, tries, driver_dict.url)
                    if type(result) is int:
                        tries = result
                    else:
                        print(driver_dict.url, "\t", result, driver_dict.initial_outer_html)
                        tries = 1
                        driver_dict.tries = 1
                        driver_dict.curr_elem += 1

        if replay == 2:
            driver_dict.replay_initialize()
            tries = 1
            driver_dict.curr_site = 0
            while driver_dict.curr_site > -1:
                try:
                    driver_dict.hierarchy_change(tries)

                except Exception as e:
                    tries = 1
                    driver_dict.tries = 1
                    driver_dict.curr_elem += 1

        with open(f'logs/{extn}_{html}.txt', 'a') as f:
            try:
                logs = driver_dict.get_logs()
                if logs != None:
                    f.write(f'{site}\n')
                    for log in logs:
                        f.write(log['level'])
                        f.write('\n')
                        f.write(log['message'])
                        f.write('\n')
            except Exception as e:
                f.write(str(e))
                f.write('\n')
                f.write('Driver is already closed')
                f.write('\n')
        f.close()

    driver_dict.close()