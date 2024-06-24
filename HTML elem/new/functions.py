import os
import subprocess
import time
from base_code import *
import functools


def cleanup_tmp():
    files_to_delete = []

    # List all files in the temporary directory
    all_files = os.listdir('/tmp')

    # Filter out files that start with the specified characters
    for file_name in all_files:
        if '.org.chromium' in file_name or '.com.google.Chrome' in file_name: # or '.X11' in file_name:
            #  or 'go-build' in file_name:
            files_to_delete.append(os.path.join('/tmp', file_name))

    # Delete the files
    for file_path in files_to_delete:
        try:
            'I know this is really bad...'
            # subprocess.run(["echo", "'mitch'", "|", "sudo", "rm", "-rf", file_path], check=True)

            #for debugging!!! don't want it to fill output:
            subprocess.run(["rm", "-rf", file_path], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            # shutil.rmtree(file_path)
            # print(f"Deleted: {file_path}")
        except Exception as e:
            print(f"Error deleting {file_path}: {e}")


def cleanup_chrome():
    os.system('pkill -f chrome')
    time.sleep(5)


def cleanup_X():
    os.system('pkill -f Xvfb')
    time.sleep(5)


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


def remove_cmp_banner(options):
    options.add_extension(f'/home/mitch/work/pes/measurements/extensions/extn_crx/Consent-O-Matic.crx')
    return options


def run(site, extn, replay, driver_dict, display_num, html_test):
    options = Options()
    options.add_argument("start-maximized")
    options.add_argument(
        "user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36")
    options.binary_location = "/home/mitch/work/pes/chrome_113/chrome"

    options = remove_cmp_banner(options)
    # options = use_catapult(options, extn, temp_port1, temp_port2)

    if extn != 'control':
        options.add_extension(f'/home/mitch/work/pes/measurements/extensions/extn_crx/{extn}.crx')

    # display number
    os.environ['DISPLAY'] = f":{display_num}"

    retval = driver_dict.initialize(options, 3, site)
    if retval == 0:
        print("Failed to initialize browser!\n"*3)
        return


    if replay == 0:
        try:
            if driver_dict.load_site(site):

                # key = ''
                # if 'www' in site:
                #     key = site.split('www.')[1]
                # else:
                #     key = site.split('://')[1]
                # driver_dict.take_ss(f'{key}.png')

                driver_dict.scroll()
                driver_dict.scan_page()
        except TimeoutException:
            print(f"Timeout url:{site}")

        except Exception as e:
            print(e)

    if replay == 1:
        if driver_dict.replay_initialize():
            tries = 1
            while driver_dict.curr_site > -1:
                try:
                    driver_dict.click_on_elms(tries)
                except Exception as e:
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

        # with open(f'logs/{extn}_{html}.txt', 'a') as f:
        #     try:
        #         logs = driver_dict.get_logs()
        #         if logs != None:
        #             f.write(f'{site}\n')
        #             for log in logs:
        #                 f.write(log['level'])
        #                 f.write('\n')
        #                 f.write(log['message'])
        #                 f.write('\n')
        #     except Exception as e:
        #         f.write(str(e))
        #         f.write('\n')
        #         f.write('Driver is already closed')
        #         f.write('\n')
        # f.close()

    driver_dict.close()