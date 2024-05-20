import os

from helper import *
import multiprocessing
import json

user = 'character'
base_dir = os.getcwd()
current_path = f'{base_dir}/PSAL_images/final/RESULTS/'
os.makedirs(current_path, exist_ok=True)

websites = [
    "https://www.mrdonn.org/",
    "https://canyoublockit.com/testing/",
    "https://www.wikipedia.org",
    "https://www.github.com",
    "http://www.guit.edu.cn/en/info/1008/1050.htm",
    'http://www.bowencoinc.com'
]

# with open('websites.json', 'r') as f:
#     websites = json.load(f)

extensions = [
    "control",
    "ublock",
    "adblock",
    "privacy-badger",
]

SIZE = 3
TIMEOUT = 1800

all_processes = {}
driver_dictionary = {}
filtered_websites = []
store_to_file_dict = {}

blacklist = initialize_blacklists()
print("Stage 1: Finished Initializing Blacklist Trie")

for i in range(SIZE):
    driver_dictionary[i] = Driver()

chunks = list(divide_chunks(websites, SIZE))
for chunk in chunks:
    final_data_dict = {}   # used to store the results
    packet_dict = {}       # used to store the images
    for i, website in enumerate(chunk):
        packet_dict[website] = {}
        final_data_dict[website] = {}
        for extn in extensions:
            final_data_dict[website][extn] = {}

        all_processes[website] = {
            'control-scanner1': multiprocessing.Process(target=driver_dictionary[i].get_images,
                                                        args=(website, 'control-scanner1', blacklist)),
            'control-scanner2': multiprocessing.Process(target=driver_dictionary[i].get_images,
                                                        args=(website, 'control-scanner2', blacklist))
        }
        for extn in extensions:
            all_processes[website][extn] = multiprocessing.Process(target=driver_dictionary[i].find_missing,
                                                                   args=(website, extn, blacklist))
    # open two control browsers and collect the images and test if they are the same.
    # if the images are the same then the site is considered "stable" to continue the scan

    print(final_data_dict.keys())

    for website in chunk:
        all_processes[website]['control-scanner1'].start()
        all_processes[website]['control-scanner2'].start()

    for website in chunk:
        try:
            all_processes[website]['control-scanner1'].join(timeout=TIMEOUT)
            all_processes[website]['control-scanner2'].join(timeout=TIMEOUT)
        except Exception as e:
            print(e)

    for website in chunk:
        print("Checking Control Scanner:", website)
        key = scheme_extractor(website)
        if os.path.exists(f"tmp_data/{key}-control-scanner1.json"):
            with open(f"tmp_data/{key}-control-scanner1.json", 'r') as f:
                control_scanner_1 = json.load(f)
        else:
            print("\nmissing Control_scanner_1 data!\n Aborting site \n")
            continue

        if os.path.exists(f"tmp_data/{key}-control-scanner2.json"):
            with open(f"tmp_data/{key}-control-scanner2.json", 'r') as f:
                control_scanner_2 = json.load(f)
        else:
            print("\nmissing Control_scanner_2 data!\n Aborting site \n")
            continue

        if site_filter(control_scanner_2, control_scanner_1, website):
            print("Passed Control filter:", website)
            for extn in extensions:
                all_processes[website][extn].start()
            for extn in extensions:
                try:
                    all_processes[website][extn].join(timeout=TIMEOUT)
                except Exception as e:
                    print(e)

            control, ublock, adblock, privacy_badger = load_extn_data(website)
            if control == 'Inconsistent Site':
                print(f"Inconsistent Site: {website}")
                # remove the bad data... the site is too 'volatile'
                key = scheme_extractor(website)
                os.system(f'rm -rf {current_path}/{key}')
                final_data_dict.pop(website)
                filtered_websites.append(website)
            else:
                final_data_dict[website]["ublock"] = ublock
                final_data_dict[website]["adblock"] = adblock
                final_data_dict[website]["privacy-badger"] = privacy_badger

            # final_data_dict[website]["control"] = control

            if type(ublock) == str and type(adblock) == str and type(privacy_badger) == str:
                key = scheme_extractor(website)
                os.system(f'rm -rf {current_path}/{key}')

        else:
            print(f"filtered out: {website}")
            final_data_dict.pop(website)
            filtered_websites.append(website)

    store_to_file_dict.update(final_data_dict)
    file_path = os.path.join(current_path, 'data.json')
    with open(file_path, 'w') as file:
        json.dump(store_to_file_dict, file)
    file.close()


    # writing all the filtered sites
    file_path = os.path.join(current_path, 'filtered.txt')
    with open(file_path, "w") as file:
        for i in filtered_websites:
            file.write(i + '\n')
    file.close()

    cleanup_X()
    cleanup_tmp()
    cleanup_chrome()
    os.system(f'rm -rf tmp_data/*')

print("EVERTHING IS DONE!!\n" * 10)