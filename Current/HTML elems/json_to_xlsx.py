import pandas as pd
import json
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import os

# Path to your JSON file
# json_file_path = 'buttons_control.json'
# Path to your Excel file
# excel_file_path = 'buttons_control.xlsx'

# Load JSON data

extn_lst = [
    # 'manual'
    'control',
    'adblock',
    # 'ublock'
    # , 'privacy-badger'
    #     "ghostery",
    #     "adguard"
]

with open(f"xlsx/buttons_control.json", 'r') as file:
    control = json.load(file)

with open(f"xlsx/buttons_adblock.json", 'r') as file:
    curr_data = json.load(file)


HTML_TEST = {'buttons', "drop downs", "links", "login"}
HTML_TEST = {'buttons'}

# Your specified headers
# headers = ["URL_KEY", "HTML_obj Opened?", "Outer HTML Change", "DOM structure Change", "Initial Outer HTML",
#            "After Click Outer HTML", "Initial DOM Structure", "After Click DOM Structure", "Initial Link",
#            "After Click Link", "Tries"]

headers = ["URL_KEY", "Result", "Extn Result", "Control Result", "Initial Outer HTML"]

# Process the JSON data
for extn in extn_lst:
    # Iterate through each HTML object and its data
    for html_obj in HTML_TEST:

        with open(f"xlsx/{html_obj}_control.json", 'r') as file:
            control = json.load(file)

        with open(f"xlsx/{html_obj}_{extn}.json", 'r') as file:
            curr_data = json.load(file)

        rows = []
        for url_key, inner_data in curr_data.items():
            if url_key == 'http://www.dazn.com':
                1
            if curr_data[url_key] == []:
                continue
            if url_key not in control.keys():
                # Check everything if the site was not found in the control!!!
                rows.append([url_key] + ["Site not found in Control"] + [None] * (len(headers) - 2))  # URL row
                for unit_data in inner_data:
                    row_data = [None] + unit_data
                    rows.append(row_data[:len(headers)])

            else:
                # if the site was not found in the control!!!
                rows.append([url_key] + [None] * (len(headers) - 1))  # URL row
                pass_all = True
                for extn_unit_data in inner_data:
                    found = False
                    same_result = 'True'

                    for control_unit_data in control[url_key]:
                        # compare the outer HTML to make sure we looking at the right elem
                        if control_unit_data[3] == extn_unit_data[3]:
                            if control_unit_data[0][0] == extn_unit_data[0][0]:
                                pass
                            else:
                                pass_all = False
                                same_result = "False"
                                row_data = [None] + [same_result] + [extn_unit_data[0]] + [control_unit_data[0]] + [control_unit_data[3]]
                                rows.append(row_data[:len(headers)])
                            found = True
                            break

                    if not found:
                        row_data = ["elem not in control"] + control_unit_data
                        rows.append(row_data[:len(headers)])
                if pass_all:
                    rows.pop()

        # Create a DataFrame with the collected rows
        df = pd.DataFrame(rows, columns=headers)

        # Save the DataFrame to an Excel file
        df.to_excel(f"{html_obj}_{extn}_filtered.xlsx", index=False)

print('Data successfully saved to Excel file.')