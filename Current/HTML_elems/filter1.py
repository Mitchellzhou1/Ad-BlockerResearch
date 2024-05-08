import json

extn_lst = [
    # 'control',
    'adblock',
    'ublock',
    'privacy-badger',
]
failed_websites = set()

HTML_TEST = {'buttons', "drop downs", "links", "login", "input"}
final_dict = {}
for extn in extn_lst:
    final_dict[extn] = {}
    for html_obj in HTML_TEST:
        final_dict[extn][html_obj] = {}

        with open(f"/home/mitch/Desktop/Ad-BlockerResearch/Current/HTML_elems/xlsx/{html_obj}_control.json", 'r') as file:
            control = json.load(file)

        with open(f"/home/mitch/Desktop/Ad-BlockerResearch/Current/HTML_elems/xlsx/{html_obj}_{extn}.json", 'r') as file:
            extn_data = json.load(file)

        key = None
        for url, result in extn_data.items():
            if extn == 'ublock':
                if html_obj == 'login':
                    if 'wpastra' in url:
                        print("hi")
            key = url
            final_dict[extn][html_obj][url] = []
            # if the website is not in the controls, just recheck the false ones
            if url not in control.keys():
                for extn_unit_data in result:
                    html_result = extn_unit_data[0].lower()
                    html_elem = extn_unit_data[3]
                    if 'false' in html_result:
                        final_dict[extn][html_obj][url].append([html_elem, 1])

            else:
                for control_unit_data in control[url]:
                    control_result = control_unit_data[0].lower()
                    control_elem = control_unit_data[3]

                    for extn_unit_data in result:
                        extn_result = extn_unit_data[0].lower()
                        extn_elem = extn_unit_data[3]

                        if control_elem == extn_elem:
                            if 'true' in control_result and 'false' in extn_result:
                                final_dict[extn][html_obj][url].append([extn_elem, 1])
                            elif 'false' in control_result and 'true' in extn_result:
                                final_dict[extn][html_obj][url].append([extn_elem, 1])
                            break

            if key and not final_dict[extn][html_obj][key]:
                del final_dict[extn][html_obj][key]
        destination = f'/home/mitch/Desktop/Ad-BlockerResearch/Current/HTML_elems/xfiltered_json/{html_obj}_{extn}.json'
        with open(destination, 'w') as json_file:
            json.dump(final_dict[extn][html_obj], json_file)


total_sites = set()
for extn in extn_lst:
    for html in HTML_TEST:
        for sites in final_dict[extn][html].keys():
            total_sites.add(sites)
print(total_sites)


destination = f'/home/mitch/Desktop/Ad-BlockerResearch/Current/HTML_elems/xfiltered_json/sites.json'
with open(destination, 'w') as json_file:
    json.dump(list(total_sites), json_file)



print('Done comparing all values')