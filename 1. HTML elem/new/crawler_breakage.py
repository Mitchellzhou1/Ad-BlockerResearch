import argparse
import sys
import multiprocessing
import json
from pyvirtualdisplay import Display

from functions import *
from base_code import *


def store_results(data):
    if args.replay == 0:
        folder = 'json'
    else:
        folder = 'results'

    print(f"Writting Results for {extn_lst[0]} {HTML_TEST[0]}\n" * 5)
    if not os.path.exists(folder):
        os.makedirs(folder)
    json.dump(data, open(f"{folder}/{args.html}_{extn}.json", 'w'))

if __name__ == "__main__":
    # Parse the command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--replay', type=int)
    parser.add_argument('--html', type=str)
    parser.add_argument('--extn', type=str)
    parser.add_argument('--size', type=int)
    if len(sys.argv) < 2:
        parser.print_help(sys.stderr)
        sys.exit(1)
    args = parser.parse_args()

    HTML_TEST = [args.html]
    extn_lst = [args.extn]
    SIZE = args.size

    # initial data structures
    manager = multiprocessing.Manager()
    data_dict = manager.dict()

    scrapper = Driver(args.html, args.extn, args.replay, data_dict)

    if args.replay == 0:
        extn_lst = ["control"]      # just double-checking here
        with open('websites.json', 'r') as f:
            websites = json.load(f)

    else:
        with open(f"json/{args.html}_control.json") as f:
            websites = list(json.load(f))
        f.close()


    chunks_list = list(divide_chunks(websites, SIZE))


    for extn in extn_lst:
        print('#' * 10 + f"\n {extn} -- {HTML_TEST}\n" + '#' * 10)
        try:
            print("testing", len(chunks_list[0]), "site(s)")

            for chunk in chunks_list:

                xvfb_args = [
                    '-maxclients', '1024'
                ]
                # vdisplay = Display(backend='xvfb', size=(1920, 1280), visible=False, extra_args=xvfb_args)
                vdisplay = Display(visible=True)
                vdisplay.start()
                display = vdisplay.display

                jobs = []
                for site_index in range(len(chunk)):
                    print('website:', site_index, chunk[site_index])
                    try:
                        p1 = multiprocessing.Process(target=run, args=(
                            chunk[site_index], extn, args.replay, scrapper, display))
                        jobs.append(p1)
                    except IndexError as e:
                        print("Index Error")
                    except Exception as e:
                        print(e)

                for job in jobs:
                    print(f"starting {job}\t\t{job._args[0]}")
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
                            time.sleep(5)
                        else:
                            break

                    if job.is_alive():
                        print('timeout exceeded... terminating job')
                        job.terminate()
                time.sleep(2)

                conversion_dict = {}
                if args.replay == 0:
                    conversion_dict = dict(data_dict)

                else:
                    with open(f"json/{args.html}_control.json", 'r') as f:
                        control = json.load(f)
                        for site in data_dict.keys():
                            conversion_dict[site] = data_dict[site]
                            if len(control[site]) != len(conversion_dict[site]):
                                number = len(control[site]) - len(conversion_dict[site])
                                print(f"We lost {number} elements!!!!!! for {site}")
                            else:
                                print(f"all values written for {site}")

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

                store_results(conversion_dict)

        except Exception as e:
            print("Error" * 100)
            print(e)

    print(f"FINISHED ALL {HTML_TEST[0]} FOR {extn_lst}!!!!!\n" * 2)
