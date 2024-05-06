from helper import *
import multiprocessing



websites = [
    # "https://www.example.com",
    "https://canyoublockit.com/testing/",
    # "https://www.wikipedia.org",
    # "https://www.github.com"
]

extensions = [
    "control",
    # "ublock",
    # "adblock",
    # "privacy-badger",
]

SIZE = 4

all_processes = {}
driver_dictionary = {}
manager = multiprocessing.Manager()
control_dict = manager.dict()
final_data_dict = manager.dict()
packet_dict = manager.dict()

blacklist, inverse_lookup, regular_lookup = initialize_blacklists(Trie(), Trie())

for i in range(SIZE):
    driver_dictionary[i] = Driver()

chunks = list(divide_chunks(websites, SIZE))
for chunk in chunks:
    for i, website in enumerate(chunk):
        packet_dict[website] = manager.dict()
        final_data_dict[website] = manager.dict()
        all_processes[website] = {
            'control-scanner1': multiprocessing.Process(target=driver_dictionary[i].get_images,
                                                        args=(website, 'control-scanner1', packet_dict, blacklist, inverse_lookup, regular_lookup)),
            'control-scanner2': multiprocessing.Process(target=driver_dictionary[i].get_images,
                                                        args=(website, 'control-scanner2', packet_dict, blacklist, inverse_lookup, regular_lookup)),
        }
        for extn in extensions:
            all_processes[website][extn] = multiprocessing.Process(target=driver_dictionary[i].find_missing,
                                                                   args=(website, extn, final_data_dict,
                                                                         packet_dict, blacklist, inverse_lookup, regular_lookup))

    # open two control browsers and collect the images and test if they are the same.
    # if the images are the same then the site is considered "stable" to continue the scan
    for website in chunk:
        all_processes[website]['control-scanner1'].start()
        all_processes[website]['control-scanner2'].start()

    for website in chunk:
        all_processes[website]['control-scanner1'].join()
        all_processes[website]['control-scanner2'].join()

    for website in chunk:
        if site_filter(packet_dict[website]['control-scanner1'], packet_dict[website]['control-scanner2']):

            for extn in extensions:
                all_processes[website][extn].start()

            for extn in extensions:
                all_processes[website][extn].join()

        else:
            ...
            #write to the json, site was filtered out

print(final_data_dict.values())
