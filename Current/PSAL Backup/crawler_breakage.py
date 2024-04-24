from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoAlertPresentException

import time
import multiprocessing
import json
import argparse
import os
import subprocess
from pyvirtualdisplay import Display
from xvfbwrapper import Xvfb
import sys
import random
import math
from functions import *
import signal
import inspect

from base_code import *
from Excel import *

extn_lst = [
    # 'manual'
    'control',
    # ,
    # 'adblock'
    #  ,
    'ublock'
    # , 'privacy-badger'
]
SIZE = 20
port = 9090
start_port = 11001

# HTML_TEST = {'buttons', "drop downs", "links", "login"}
# HTML_TEST = {"drop downs"}#, "links", "login"}
HTML_TEST = {'buttons'}

if __name__ == "__main__":
    # Parse the command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--replay', type=int)
    if len(sys.argv) < 2:
        parser.print_help(sys.stderr)
        sys.exit(1)
    args = parser.parse_args()

    # initial data structures
    master_port_list = []
    websites = []
    manager = multiprocessing.Manager()
    data_dict = manager.dict()
    excel_dict = manager.dict()
    driver_class_dict = {}
    data_dict['errors'] = manager.dict()
    excel_dict['errors'] = manager.dict()

    hierarchy_dict = manager.dict()
    save_hierarchy_dict = {}

    # multiprocess manager to local data
    save_dict = {}
    save_excel_dict = {}

    for extn in extn_lst:
        data_dict['errors'][extn] = manager.dict()
        excel_dict['errors'][extn] = manager.dict()

        data_dict[extn] = manager.dict()
        excel_dict[extn] = manager.dict()

        hierarchy_dict[extn] = manager.dict()

        save_dict[extn] = {}
        save_excel_dict[extn] = {}
        # hierarchy_dict = {'buttons': [], "drop downs": [], "links": [], "login": []}
        save_hierarchy_dict[extn] = {}
        # driver_class_dict[extn] = {}
        # driver_class_dict[extn] = Driver(attributes_dict[html]["attributes"], attributes_dict[html]["xpaths"], extn, args.replay, data_dict, excel_dict)

        for html in HTML_TEST:
            data_dict[extn][html] = manager.dict()
            excel_dict[extn][html] = manager.dict()
            excel_dict['errors'][extn][html] = manager.dict()

            save_dict[extn][html] = {}
            save_excel_dict[extn][html] = {}

            hierarchy_dict[extn][html] = manager.dict()
            save_hierarchy_dict[extn][html] = {}

            # driver_class_dict[extn][html] = Driver(attributes_dict[html]["attributes"], attributes_dict[html]["xpaths"], extn, html, args.replay, data_dict, excel_dict)

    for extn in extn_lst:
        driver_class_dict[extn] = Driver(attributes_dict[html]["attributes"], attributes_dict[html]["xpaths"], extn,
                                         args.replay, data_dict, excel_dict, hierarchy_dict)

    # with open("../../break/adblock_detect/inner_pages_custom_break.json", "r") as f:
    #     allsite_dict = json.load(f)
    # f.close()

    # # filtering the landing pages
    # for key in allsite_dict:
    #     websites.append(allsite_dict[key][0])

    if args.replay == 0:
        os.system('rm -f json/*.json')
        os.system('rm -f archive/*.wprgo')
        os.system('rm -rf wpr_data/*')
        os.system('rm -rf logs/*')

    # testing for 10000 sites
    # websites = random.sample(websites, 1000)
    #
    # # websites = websites[3500:4000]
    # with open('websites.json', 'w') as f:
    #     json.dump(websites, f)

    websites = [
    'http://www.thawte.com',
    'http://www.kbb.com',
    'http://www.feimaoyun.com',
    'https://en.wikipedia.org/wiki/Main_Page',
    'https://www.microsoft.com/en-us/',
    'https://www.office.com/',
    'https://weather.com/',
    'https://openai.com/',
    'https://www.bing.com/',
    'https://duckduckgo.com/',
    'https://cnn.com',
    'https://www.nytimes.com/',
    'https://www.twitch.tv/',
    'https://www.imdb.com/',
    'https://www.qq.com/',
    'https://mail.ru/',
    'https://naver.com',
    'https://zoom.us/',
    'https://www.globo.com/',
    'https://www.ebay.com/',
    'https://www.foxnews.com/',
    'https://www.instructure.com/',
    'https://www.walmart.com/',
    'https://www.indeed.com/',
    'https://www.paypal.com/us/home',
    'https://www.accuweather.com/',
    'https://www.pinterest.com/',
    'https://www.bbc.com/',
    'https://www.homedepot.com/',
    'https://www.breitbart.com/',
    'https://github.com/'
]

    # if args.replay == 2:
    #     with open("json/buttons_control.json", 'r') as f:
    #         websites = list(json.load(f))

    # if args.replay == 1:
    #     with open("websites.json", 'r') as f:
    #         websites = list(json.load(f))
    # f.close()

    if args.replay == 0:
        extn_lst = ["control"]

    # chunks_list = list(divide_chunks(websites, SIZE))
    chunks_list = list(divide_chunks(websites, SIZE))
    # print(chunks_list)

    for extn in extn_lst:
        print('#' * 10 + f"\n {extn} \n" + '#' * 10 )
        try:
            folder_path = f'/home/mitch/work/pes/measurements/break/html_elements/wpr_data/{extn}'
            if not os.path.exists(folder_path):
                # Create the folder
                os.makedirs(folder_path)

            num_sites = len(chunks_list[0])
            print(num_sites)
            processes, ports_list = start_servers(args.replay, num_sites, extn, 0, [], start_port)
            master_port_list.append(ports_list)
            print(ports_list)

            for chunk in chunks_list:
                # while not check_if_ports_open(ports_list):
                #     # restart all servers
                #     start_port += 2*num_sites
                #     error('', '', inspect.currentframe().f_code.co_name, 'all ports not open; resetting the servers')
                #     ports_list = master_port_list[-1]
                #     master_port_list.pop(-1)
                #     processes, ports_list = start_servers(args.replay, num_sites, extn, 1, ports_list, start_port)
                #     master_port_list.append(ports_list)

                xvfb_args = [
                    '-maxclients', '1024'
                ]
                vdisplay = Display(backend='xvfb', size=(1920, 1280), extra_args=xvfb_args)
                # vdisplay = Xvfb(width=1920, height=1280)
                vdisplay.start()
                display = vdisplay.display

                print(display)
                jobs = []
                for site_index in range(len(chunk)):
                    print('website:', chunk[site_index])
                    try:
                        p1 = multiprocessing.Process(target=run, args=(
                        chunk[site_index], extn, args.replay, ports_list[2 * site_index],
                        ports_list[(2 * site_index) + 1], driver_class_dict[extn], display, HTML_TEST,))
                        jobs.append(p1)
                    except IndexError as e:
                        error('', '', inspect.currentframe().f_code.co_name, e)
                    except Exception as e:
                        error(chunk[site_index], inspect.currentframe().f_code.co_name, e)

                for job in jobs:
                    print(f"starting {job}")
                    job.start()
                    time.sleep(5)

                time.sleep(5)

                TIMEOUT = 1000
                start = time.time()
                for job in jobs:
                    print(f"joining {job}")
                    job.join(timeout=60)

                    while time.time() - start <= TIMEOUT:
                        if job.is_alive():
                            sleep(5)
                        else:
                            break

                    if job.is_alive():
                        print('timeout exceeded... terminating job')
                        job.terminate()

                time.sleep(2)

                if args.replay == 0:
                    for html in HTML_TEST:
                        a = dict(data_dict[extn][html])
                        for site in a.keys():
                            save_dict[extn][html][site] = data_dict[extn][html][site]

                if args.replay:

                    with open("/home/mitch/work/pes/measurements/break/html_elements/json/buttons_control.json", 'r') as f:
                        control = json.load(f)
                    f.close()


                    for html in HTML_TEST:
                        a = dict(excel_dict[extn][html])
                        for site in a.keys():
                            save_excel_dict[extn][html][site] = []
                            if len(control[site]) != len(excel_dict[extn][html][site]):
                                number = len(control[site]) - len(excel_dict[extn][html][site])
                                print(f"We lost {number} elements!!!!!! for {site}")
                            else:
                                print(f"all values written for {site}")
                            for elem in excel_dict[extn][html][site]:
                                save_excel_dict[extn][html][site].append(elem)

                # if args.replay == 2:
                #     a = dict(hierarchy_dict[extn][html])
                #     for site in a.keys():
                #         save_hierarchy_dict[extn][html][site] = []
                #         for elem in hierarchy_dict[extn][html][site]:
                #             save_hierarchy_dict[extn][html][site].append(elem)

                # with open("hierarchy/final_hierarchy_results.json", 'w') as jsonfile:
                #     json.dump(save_hierarchy_dict, jsonfile)
                #     print("dumped json")
                # jsonfile.close()

                # closing open Xfvb server
                print("-" * 50)
                print("closing open xvfb processes")
                vdisplay.stop()
                # os.system('pkill Xvfb')
                print(os.system("ps aux | grep Xvfb | wc -l"))
                print("-" * 50)

                # sleep to close the xvfb normally
                time.sleep(5)

                # cleanup process
                cleanup_chrome()
                cleanup_tmp()
                cleanup_X()

            # sleep to close the xvfb normally
            time.sleep(5)

            if args.replay == 0:
                if not os.path.exists('/home/mitch/work/pes/measurements/break/html_elements/json'):
                    os.makedirs('/home/mitch/work/pes/measurements/break/html_elements/json')
                for html in HTML_TEST:
                    json.dump(save_dict[extn][html], open(f"/home/mitch/work/pes/measurements/break/html_elements/json/{html}_{extn}.json", 'w'))

            if args.replay == 1:
                if not os.path.exists('/home/mitch/work/pes/measurements/break/html_elements/xlsx'):
                    os.makedirs('/home/mitch/work/pes/measurements/break/html_elements/xlsx')
                for html in HTML_TEST:
                    json.dump(save_excel_dict[extn][html], open(f"/home/mitch/work/pes/measurements/break/html_elements/xlsx/{html}_{extn}.json", 'w'))

            if args.replay == 2:
                if not os.path.exists('/home/mitch/work/pes/measurements/break/html_elements/hierarchy'):
                    os.makedirs('/home/mitch/work/pes/measurements/break/html_elements/hierarchy')
                for html in HTML_TEST:
                    json.dump(save_excel_dict[extn][html], open(f"/home/mitch/work/pes/measurements/break/html_elements/hierarchy/{html}_{extn}.json", 'w'))

            time.sleep(2)  # time for port to be available again

            try:
                ports_list = master_port_list[-1]
                print(ports_list)
                stop_servers(ports_list)

            except ProcessLookupError:
                print(f"No process with PID {pid1} found.")
            except PermissionError:
                print(f"Permission denied to send signal to process {pid1}.")

        except KeyboardInterrupt:
            print('KeyboardInterrupt:', 'Interrupted')
            print(f"Closing any open servers")
            try:
                ports_list = master_port_list[-1]
                print(ports_list)
                stop_servers(ports_list)
            except ProcessLookupError:
                print(f"No process with PID {pid1} found.")
            except PermissionError:
                print(f"Permission denied to send signal to process {pid1}.")

            if args.replay == 0:
                if not os.path.exists('/home/mitch/work/pes/measurements/break/html_elements/json'):
                    os.makedirs('/home/mitch/work/pes/measurements/break/html_elements/json')
                for html in HTML_TEST:
                    json.dump(save_dict[extn][html], open(f"json/{html}_{extn}.json", 'w'))

            if args.replay == 1:
                if not os.path.exists('/home/mitch/work/pes/measurements/break/html_elements/xlsx'):
                    os.makedirs('/home/mitch/work/pes/measurements/break/html_elements/xlsx')
                for html in HTML_TEST:
                    json.dump(save_excel_dict[extn][html], open(f"xlsx/{html}_{extn}.json", 'w'))

            if args.replay == 2:
                if not os.path.exists('/home/mitch/work/pes/measurements/break/html_elements/hierarchy'):
                    os.makedirs('/home/mitch/work/pes/measurements/break/html_elements/hierarchy')
                for html in HTML_TEST:
                    json.dump(save_excel_dict[extn][html], open(f"hierarchy/{html}_{extn}.json", 'w'))

            pass

        except Exception as e:
            print('Interrupted:', e)

            print(f"Closing any open servers")
            try:
                ports_list = master_port_list[-1]
                print(ports_list)
                stop_servers(ports_list)

            except ProcessLookupError:
                print(f"No process with PID {pid1} found.")
            except PermissionError:
                print(f"Permission denied to send signal to process {pid1}.")

            if args.replay == 0:
                if not os.path.exists('/home/mitch/work/pes/measurements/break/html_elements/json'):
                    os.makedirs('/home/mitch/work/pes/measurements/break/html_elements/json')
                for html in HTML_TEST:
                    json.dump(save_dict[extn][html], open(f"json/{html}_{extn}.json", 'w'))

            if args.replay == 1:
                if not os.path.exists('/home/mitch/work/pes/measurements/break/html_elements/xlsx'):
                    os.makedirs('/home/mitch/work/pes/measurements/break/html_elements/xlsx')
                for html in HTML_TEST:
                    json.dump(save_excel_dict[extn][html], open(f"xlsx/{html}_{extn}.json", 'w'))

            if args.replay == 2:
                if not os.path.exists('/home/mitch/work/pes/measurements/break/html_elements/hierarchy'):
                    os.makedirs('/home/mitch/work/pes/measurements/break/html_elements/hierarchy')
                for html in HTML_TEST:
                    json.dump(save_excel_dict[extn][html], open(f"hierarchy/{html}_{extn}.json", 'w'))

