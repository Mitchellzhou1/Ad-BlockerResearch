from bs4 import BeautifulSoup
from openpyxl import Workbook


def grab_sections(html):
    soup = BeautifulSoup(html, 'html.parser')
    elements = soup.find_all('div')
    return elements


def id_checker(adblocker, regular):
    section1 = adblocker[5:adblocker.find(">")].split()
    section2 = regular[5:regular.find(">")].split()
    same = False
    if adblocker[5:adblocker.find(">")] == regular[5:regular.find(">")]:
        same = True
    else:
        for option in section1:
            if option in section2:
                same = True  # not the best way of doing this !!!!!!! MAY NEED TO FIX LATER
                break
    return same, section1, section2


def export_data(data, original, adBlocker):
    workbook = Workbook()
    sheet = workbook.active
    sheet[f'A{1}'] = f'Original = {original} <div> tags'
    sheet[f'A{2}'] = f'AdBlocker = {adBlocker} <div> tags'

    sheet[f'C{1}'] = f"same : {len(data['same'])}"
    sheet[f'C{2}'] = f"dropped: {len(data['dropped'])}"
    sheet[f'C{3}'] = f"changed: {len(data['changed'])}"

    columns = [('A', 'changed'), ('C', 'dropped'), ('E', 'same')]

    start = 7
    sheet[f'A{start - 2}'] = f"{columns[0][1]}"
    sheet[f'C{start - 2}'] = f"{columns[1][1]}"
    sheet[f'E{start - 2}'] = f"{columns[2][1]}"
    for column, attribute in columns:
        for i in range(start, len(data[attribute]) + start):
            cell = column+str(i)
            sheet[cell] = ' '.join(data[attribute][i - start])

    workbook.save('output_file.xlsx')
    workbook.close()


def get_difference(adblocker, regular):
    # I am going under the assumption that the non-adblocker HTML code is
    # always longer than the HTML that elements blocked

    data = {
        'dropped': [],
        'changed': [],
        'same': []
    }
    if len(adblocker) > len(regular):
        print("Wierd!!!! Not suppose to happen!!!!")
    else:
        i = j = 0
        while j < len(adblocker):
            if i == 30:
                print()
            # we are looking at the same part of the website
            ref = id_checker(str(adblocker[i]), str(regular[j]))
            if ref[0]:
                if adblocker[i] == regular[j]:
                    data['same'].append(ref[1])
                else:
                    data['changed'].append(ref[2])
                i += 1
                j += 1
            else:
                data['dropped'].append(ref[2])
                j += 1

        while j < len(regular):
            data['dropped'].append(str(regular[j]))
            j += 1

    return data


f1 = open("adblocker.txt", "r")
f2 = open("regular.txt", "r")


# f1 = grab_sections(''.join(f1.readlines()))
f1 = grab_sections(f1.read())
import sys
for i in f1:
    print(f1.innerHTML)
    sys.exit(0)


f2 = grab_sections(''.join(f2.readlines()))

ans = get_difference(f1, f2)

f = open("output.txt", "a")

output = f"""
Original = {len(f2)} <div> tags
AdBlocker = {len(f1)} <div> tags
============================================
same = {len(ans['same'])}
dropped = {len(ans['dropped'])}
changed = {len(ans['changed'])}
=============================================
"""
export_data(ans, len(f2), len(f1))



