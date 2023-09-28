from bs4 import BeautifulSoup


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
                same = True             # not the best way of doing this !!!!!!! MAY NEED TO FIX LATER
                break
    return same, section1, section2


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
            # we are looking at the same part of the website
            ref = id_checker(str(adblocker[i]), str(regular[j]))
            if ref[0]:
                if adblocker[i] == regular[j]:
                    data['same'].append(ref[1])
                else:
                    data['changed'].append(ref[1])
                i += 1
                j += 1
            else:
                data['dropped'].append(ref[2])
                i += 1

        while i < len(adblocker):
            data['dropped'].append(str(adblocker[i]))



    return data



f1 = open("adblocker.txt", "r")
f1 = grab_sections(''.join(f1.readlines()))

f2 = open("regular.txt", "r")
f2 = grab_sections(''.join(f2.readlines()))

ans = get_difference(f1, f2)

print(len(ans['dropped']))
