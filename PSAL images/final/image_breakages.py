from helper import *
import multiprocessing


websites = [
    # "https://www.example.com",
    "https://www.google.com",
    # "https://www.wikipedia.org",
    # "https://www.github.com"
]

extensions = [
    "control",
    "ublock",
    # "adblock",
    # "privacy-badger",
]

SIZE = 4

all_processes = {}
driver_dictionary = {}
control_dict = multiprocessing.Manager().dict()
packet_dict = multiprocessing.Manager().dict()

for i in range(SIZE):
    driver_dictionary[i] = Driver()

chunks = list(divide_chunks(websites, SIZE))
for chunk in chunks:
    for i, website in enumerate(chunk):
        packet_dict[website] = multiprocessing.Manager().dict()
        all_processes[website] = {
            'control-scanner1': multiprocessing.Process(target=driver_dictionary[i].filter, args=(website, 'control-scanner1', control_dict)),
            'control-scanner2': multiprocessing.Process(target=driver_dictionary[i].filter, args=(website, 'control-scanner2', control_dict)),
        }
        for extn in extensions:
            all_processes[website][extn] = multiprocessing.Process(target=run, args=(website, json_data_dict, all_processes))

    for website in chunk:
        all_processes[website]['control-scanner1'].start()
        all_processes[website]['control-scanner2'].start()
        if packet_dict[website]['control-scanner1'] == packet_dict[website]['control-scanner2']:
            for extn in extensions:
                all_processes[website][extn].start()
