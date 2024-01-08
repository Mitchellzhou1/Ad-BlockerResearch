import os

current_dir = os.path.dirname(os.path.realpath(__file__))
extensions_dir = os.path.abspath(os.path.join(current_dir, 'Extensions'))

easy_list = open(f"{extensions_dir}/easylist.txt", "r")
easy_privacy = open(f"{extensions_dir}/easyprivacy.txt", "r")
peter_lowe = open(f"{extensions_dir}/Peter Lowe", "r")

combined = []

for rule in easy_privacy:
    if rule[:2] == "||":
        rule = rule.strip().lstrip("||").rstrip("$^")
        combined.append(rule)

for rule in easy_list:
    if rule[:2] == "||":
        rule = rule.strip().lstrip("||").rstrip("$^")
        combined.append(rule)

for rule in peter_lowe:
    if rule[:10] == "127.0.0.1 ":
        rule = rule.strip()[10:]
        combined.append(rule)

combined = sorted(combined)

for i in range(1000):
    print(combined[i])