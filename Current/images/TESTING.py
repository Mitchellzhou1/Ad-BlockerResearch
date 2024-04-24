def check_match(url, rule):
    # Remove any leading or trailing whitespace characters from the rule
    rule = rule.strip()

    # Check if the rule is a valid filter rule
    if rule.startswith("||") and rule.endswith("^"):
        # Extract the domain from the rule
        domain = rule[2:-1]

        # Check if the domain is present in the URL
        if domain in url:
            return True

    return False


# Example usage
url = "https://ib.adnxs.com/prebid/setuid?bidder=rubicon&uid=LV64HREN-Y-4KRA&us_privacy=1YNN"
rule = "||adnxs.com^"
result = check_match(url, rule)
print(result)
print("DONE1")

a = [['bob', 1, 'failed'], ["tye", 1, 'worked'], ["jez", 1, 'worked'], ['sdd', 1, 'worked']]

curr_elem = 0
lst = a
excel = []


def test_elems():
    global curr_elem
    while 1:
        if curr_elem >= len(a):
            print("DONE")
            return "DONE"
        else:
            test()
            curr_elem += 1


def test():
    global curr_elem
    if a[curr_elem][2] == "worked":
        1

    else:
        if a[curr_elem][1] >= 0:
            a[curr_elem][1] -= 1
            if curr_elem + 1 < len(lst):
                lst[curr_elem], lst[curr_elem + 1] = lst[curr_elem + 1], lst[curr_elem]
                curr_elem -= 1
                return
        excel.append(lst[curr_elem])


test_elems()
