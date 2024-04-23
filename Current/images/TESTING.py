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
