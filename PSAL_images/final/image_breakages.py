from helper import *
import multiprocessing
import json

user = 'character'
base_dir = os.getcwd()
current_path = f'{base_dir}/PSAL_images/final/RESULTS/'
os.makedirs(current_path, exist_ok=True)

# websites = [
    # "https://www.mrdonn.org/",
    # "https://canyoublockit.com/testing/",
    # "https://www.wikipedia.org",
    # "https://www.github.com",
    # "http://www.guit.edu.cn/en/info/1008/1050.htm"
# ]

with open('websites.json', 'r') as f:
    websites = json.load(f)

extensions = [
    "control",
    "ublock",
    "adblock",
    "privacy-badger",
]

SIZE = 40
TIMEOUT = 600

all_processes = {}
driver_dictionary = {}
manager = multiprocessing.Manager()
control_dict = manager.dict()
final_data_dict = manager.dict()
packet_dict = manager.dict()
filtered_websites = []
store_to_file_dict = {}

blacklist, inverse_lookup, regular_lookup = initialize_blacklists(Trie(), Trie())

for i in range(SIZE):
    driver_dictionary[i] = Driver()

chunks = list(divide_chunks(websites, SIZE))
for chunk in chunks:
    for i, website in enumerate(chunk):
        packet_dict[website] = manager.dict()
        final_data_dict[website] = manager.dict()
        for extn in extensions:
            final_data_dict[website][extn] = manager.dict()
        all_processes[website] = {
            'control-scanner1': multiprocessing.Process(target=driver_dictionary[i].get_images,
                                                        args=(website, 'control-scanner1', packet_dict, blacklist,
                                                              inverse_lookup, regular_lookup)),
            'control-scanner2': multiprocessing.Process(target=driver_dictionary[i].get_images,
                                                        args=(website, 'control-scanner2', packet_dict, blacklist,
                                                              inverse_lookup, regular_lookup)),
        }
        for extn in extensions:
            all_processes[website][extn] = multiprocessing.Process(target=driver_dictionary[i].find_missing,
                                                                   args=(website, extn, final_data_dict,
                                                                         packet_dict, blacklist, inverse_lookup,
                                                                         regular_lookup))

    print("Stage 1: Finished Initializing all Processes")
    # open two control browsers and collect the images and test if they are the same.
    # if the images are the same then the site is considered "stable" to continue the scan
    for website in chunk:
        print(f"Starting Filter: {website}")
        all_processes[website]['control-scanner1'].start()
        all_processes[website]['control-scanner2'].start()

    for website in chunk:
        packet_dict[website]['control-scanner1'] = 'Inconsistent Site'
        packet_dict[website]['control-scanner2'] = 'Inconsistent Site'
        try:
            all_processes[website]['control-scanner1'].join(timeout=TIMEOUT)
            all_processes[website]['control-scanner2'].join(timeout=TIMEOUT)
        except Exception as e:
            print(e)

    for website in chunk:
        print("Checking Control Scanner:", website)
        if site_filter(packet_dict[website]['control-scanner1'], packet_dict[website]['control-scanner2']):
            print("Passed Control filter:", website)
            for extn in extensions:
                all_processes[website][extn].start()

            for extn in extensions:
                try:
                    all_processes[website][extn].join(timeout=TIMEOUT)
                except Exception as e:
                    packet_dict[website][extn] = 'Inconsistent Site'
                    print(e)

            if final_data_dict[website]['control'] == 'Inconsistent Site':
                # remove the bad data... the site is too 'volatile'
                key = scheme_extractor(website)
                os.system(f'rm -rf {current_path}/{key}')
                final_data_dict.pop(website)

        else:
            print("Failed Filtered:", website)
            filtered_websites.append(website)

    file_path = os.path.join(current_path, 'data.json')
    with open(file_path, 'w') as file:
        for website in final_data_dict.keys():
            store_to_file_dict[website] = {}
            flag = True
            for extn in final_data_dict[website].keys():
                store_to_file_dict[website][extn] = {}
                if type(final_data_dict[website][extn]) == str:
                    continue
                for i in final_data_dict[website][extn].keys():
                    flag = False
                    store_to_file_dict[website][extn][i] = final_data_dict[website][extn][i]
            if flag:
                key = scheme_extractor(website)
                os.system(f'rm -rf {current_path}/{key}')

        json.dump(dict(store_to_file_dict), file)
    file.close()

    cleanup_X()
    cleanup_tmp()
    cleanup_chrome()


    # writing all the filtered sites
    file_path = os.path.join(current_path, 'filtered.txt')
    with open(file_path, "w") as file:
        for i in filtered_websites:
            file.write(i)
    file.close()

print("EVERTHING IS DONE!!\n" * 10)
