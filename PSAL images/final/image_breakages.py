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

for i in range(SIZE):
    driver_dictionary[i] = Driver()

chunks = list(divide_chunks(websites, SIZE))
for chunk in chunks:
    for website in chunk:
        all_processes[website] = {
            'control-scanner1': multiprocessing.Process(target=run, args=(website, json_data_dict, all_processes)),
            'control-scanner2': multiprocessing.Process(target=run, args=(website, json_data_dict, all_processes)),
        }
        for extn in extensions:
            all_processes[website][chunk] = multiprocessing.Process(target=run, args=(website, json_data_dict, all_processes))