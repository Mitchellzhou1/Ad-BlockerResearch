def match(rule, url):
    parts = rule.split("*")
    for part in parts:
        if part not in url:
            return False
    return True

def binary_search(easylist, url):
    low = 0
    high = len(easylist) - 1

    while low <= high:
        mid = (low + high) // 2
        rule = easylist[mid].lstrip("||").rstrip("$^")  # Strip characters for comparison
        if match(rule, url):
            return True  # Match found
        elif rule < url:
            low = mid + 1
        else:
            high = mid - 1

    return False  # No match found


url_to_check = 'https://geotargetly-api-ll.com/'

easylist_sample = [
    "||g990421675.co^",
    "||g990421676.co^",
    "||gbqofs.com^",
    "||geoedge.be^",
    "||geotargetly-api-*.com^"
]

# Sort the EasyList rules for binary search (assuming the list is not too large)
easylist_sample.sort()

# Perform binary search
result = binary_search(easylist_sample, url_to_check)
if result:
    print(f"{url_to_check} matches an EasyList rule.")
else:
    print(f"{url_to_check} does not match any EasyList rule.")
