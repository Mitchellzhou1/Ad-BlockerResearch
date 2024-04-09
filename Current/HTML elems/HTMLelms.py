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
    # 'adblock',
    'ublock'
    # , 'privacy-badger'
    #     "ghostery",
    #     "adguard"
]

HTML_TEST = {'buttons', "drop downs", "links", "login"}
HTML_TEST = {'buttons'}

# Your specified headers
# headers = ["URL_KEY", "HTML_obj Opened?", "Outer HTML Change", "DOM structure Change", "Initial Outer HTML",
#            "After Click Outer HTML", "Initial DOM Structure", "After Click DOM Structure", "Initial Link",
#            "After Click Link", "Tries"]

headers = ["URL_KEY", "Reason", "Result", "Extension Result", "Control Result", "HTML CODE"] + [None] * 5

# Process the JSON data
for extn in extn_lst:
    # Iterate through each HTML object and its data
    for html_obj in HTML_TEST:

        with open(f"previous/{html_obj}_control.json", 'r') as file:
            control = json.load(file)

        with open(f"previous/{html_obj}_{extn}.json", 'r') as file:
            curr_data = json.load(file)

        rows = []
        for url_key, large_lst_of_all_elms in curr_data.items():
            if large_lst_of_all_elms == []:
                continue

                # Check everything if the site was not found in the control!!!
            if url_key not in control.keys():
                rows.append([url_key] + ["Site not found in Control"] + [None] * (len(headers) - 2))  # URL row
                for unit_data in large_lst_of_all_elms:
                    row_data = [None] + unit_data
                    rows.append(row_data)

            else:
                # if the site was found in the control!!!
                temp_data = []
                missing_elem = []
                for extn_individual_elm in large_lst_of_all_elms:
                    found = False
                    for control_individual_elm in control[url_key]:
                        # compare the outer HTML to make sure we're looking at the right elem
                        if control_individual_elm[3] == extn_individual_elm[3]:
                            found = True
                            if control_individual_elm[0] == extn_individual_elm[0]:
                                pass
                            else:
                                # If the results were missing

                                # they are both true but different reasons for being true
                                if extn_individual_elm[0][0] == 'T' and control_individual_elm[0][0] == 'T':
                                    result = "True?"

                                elif extn_individual_elm[0][0] == "T" and control_individual_elm[0][0] == 'F':
                                    result = "Error with script"

                                elif extn_individual_elm[0][0] == "F" and control_individual_elm[0][0] == 'T':
                                    result = "BREAKAGE!"

                                else:
                                    result = "??? What other case could this be ??? Should have been filtered out"
                                data = ["Diff result"] + [result] + [extn_individual_elm[0]] + [control_individual_elm[0]] + [control_individual_elm[3]]
                                temp_data.append(data[:len(headers)])
                            break

                    if not found:
                        missing_elem.append(extn_individual_elm)

                if temp_data or missing_elem:
                    rows.append([] * 1)
                    rows.append([url_key] + [None] * (len(headers) - 1))  # URL row
                    if missing_elem:
                        for elem in missing_elem:
                            row_data = [None] + ["Not in control"] + [elem[0]] + [None] * 2 + [elem[3]]
                            rows.append(row_data[:len(headers)])
                    if temp_data:
                        for elem in temp_data:
                            row_data = [None] + elem
                            rows.append(row_data[:len(headers)])

        for i in rows:
            if len(i) > 6:
                1

        # Create a DataFrame with the collected rows
        df = pd.DataFrame(rows, columns=headers)

        # Save the DataFrame to an Excel file
        df.to_excel(f"{html_obj}_{extn}_filtered.xlsx", index=False)

print('Data successfully saved to Excel file.')