import argparse
import sys
import multiprocessing
import json
from pyvirtualdisplay import Display

from functions import *
from base_code import *


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
                            chunk[site_index], extn, args.replay, scrapper, display, args.html))
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
                    for html in HTML_TEST:
                        a = dict(data_dict)
                        for site in a.keys():
                            con = data_dict[extn][html][site]

                if args.replay:
                    try:
                        with open(
                                f"/home/mitch/work/pes/measurements/break/html_elements/json/{args.test}_control.json",
                                'r') as f:
                            control = json.load(f)
                        f.close()
                    except Exception as e:
                        print("There is actually no way it should be failing here...")
                        print(e)

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
                # cleanup_tmp()
                # cleanup_X()

                # sleep to close the xvfb normally
                time.sleep(5)

                if args.replay == 0:
                    print(f"Writting Results for {extn_lst[0]} {HTML_TEST[0]}\n" * 5)
                    if not os.path.exists('/home/mitch/work/pes/measurements/break/html_elements/json'):
                        os.makedirs('/home/mitch/work/pes/measurements/break/html_elements/json')
                    for html in HTML_TEST:
                        json.dump(save_dict[extn][html],
                                  open(f"/home/mitch/work/pes/measurements/break/html_elements/json/{html}_{extn}.json",
                                       'w'))

                if args.replay == 1:
                    print(f"Writting Results for {extn_lst[0]} {HTML_TEST[0]}\n" * 5)
                    if not os.path.exists('/home/mitch/work/pes/measurements/break/html_elements/xlsx'):
                        os.makedirs('/home/mitch/work/pes/measurements/break/html_elements/xlsx')
                    for html in HTML_TEST:
                        json.dump(save_excel_dict[extn][html],
                                  open(f"/home/mitch/work/pes/measurements/break/html_elements/xlsx/{html}_{extn}.json",
                                       'w'))

                if args.replay == 2:
                    if not os.path.exists('/home/mitch/work/pes/measurements/break/html_elements/hierarchy'):
                        os.makedirs('/home/mitch/work/pes/measurements/break/html_elements/hierarchy')
                    for html in HTML_TEST:
                        json.dump(save_excel_dict[extn][html], open(
                            f"/home/mitch/work/pes/measurements/break/html_elements/hierarchy/{html}_{extn}.json", 'w'))

            time.sleep(2)  # time for port to be available again

            # try:
            # ports_list = master_port_list[-1]
            # print(ports_list)
            # stop_servers(ports_list)

            # except ProcessLookupError:
            #     print(f"No process with PID {pid1} found.")
            # except PermissionError:
            #     print(f"Permission denied to send signal to process {pid1}.")

        except KeyboardInterrupt:
            # print('KeyboardInterrupt:', 'Interrupted')
            # print(f"Closing any open servers")
            # try:
            #     ports_list = master_port_list[-1]
            #     print(ports_list)
            #     stop_servers(ports_list)
            # except ProcessLookupError:
            #     print(f"No process with PID {pid1} found.")
            # except PermissionError:
            #     print(f"Permission denied to send signal to process {pid1}.")

            if args.replay == 0:
                print(f"Writting Results for {extn_lst[0]} {HTML_TEST[0]}\n" * 5)
                if not os.path.exists('/home/mitch/work/pes/measurements/break/html_elements/json'):
                    os.makedirs('/home/mitch/work/pes/measurements/break/html_elements/json')
                for html in HTML_TEST:
                    json.dump(save_dict[extn][html],
                              open(f"/home/mitch/work/pes/measurements/break/html_elements/json/{html}_{extn}.json",
                                   'w'))

            if args.replay == 1:
                print(f"Writting Results for {extn_lst[0]} {HTML_TEST[0]}\n" * 5)
                if not os.path.exists('/home/mitch/work/pes/measurements/break/html_elements/xlsx'):
                    os.makedirs('/home/mitch/work/pes/measurements/break/html_elements/xlsx')
                for html in HTML_TEST:
                    json.dump(save_excel_dict[extn][html],
                              open(f"/home/mitch/work/pes/measurements/break/html_elements/xlsx/{html}_{extn}.json",
                                   'w'))

            if args.replay == 2:
                if not os.path.exists('/home/mitch/work/pes/measurements/break/html_elements/hierarchy'):
                    os.makedirs('/home/mitch/work/pes/measurements/break/html_elements/hierarchy')
                for html in HTML_TEST:
                    json.dump(save_excel_dict[extn][html], open(
                        f"/home/mitch/work/pes/measurements/break/html_elements/hierarchy/{html}_{extn}.json", 'w'))
            print("KEYBOARD INTERRUPT!!" * 100)
            pass

        except Exception as e:
            print('Interrupted:', e)

            print(f"Closing any open servers")
            # try:
            #     ports_list = master_port_list[-1]
            #     print(ports_list)
            #     stop_servers(ports_list)

            # except ProcessLookupError:
            #     print(f"No process with PID {pid1} found.")
            # except PermissionError:
            #     print(f"Permission denied to send signal to process {pid1}.")

            if args.replay == 0:
                if not os.path.exists('/home/mitch/work/pes/measurements/break/html_elements/json'):
                    os.makedirs('/home/mitch/work/pes/measurements/break/html_elements/json')
                for html in HTML_TEST:
                    json.dump(save_dict[extn][html],
                              open(f"/home/mitch/work/pes/measurements/break/html_elements/json/{html}_{extn}.json",
                                   'w'))

            if args.replay == 1:
                if not os.path.exists('/home/mitch/work/pes/measurements/break/html_elements/xlsx'):
                    os.makedirs('/home/mitch/work/pes/measurements/break/html_elements/xlsx')
                for html in HTML_TEST:
                    json.dump(save_excel_dict[extn][html],
                              open(f"/home/mitch/work/pes/measurements/break/html_elements/xlsx/{html}_{extn}.json",
                                   'w'))

            if args.replay == 2:
                if not os.path.exists('/home/mitch/work/pes/measurements/break/html_elements/hierarchy'):
                    os.makedirs('/home/mitch/work/pes/measurements/break/html_elements/hierarchy')
                for html in HTML_TEST:
                    json.dump(save_excel_dict[extn][html], open(
                        f"/home/mitch/work/pes/measurements/break/html_elements/hierarchy/{html}_{extn}.json", 'w'))
            print("Error" * 100)
            print(e)
    print(f"FINISHED ALL {HTML_TEST[0]} FOR {extn_lst}!!!!!\n" * 2)
