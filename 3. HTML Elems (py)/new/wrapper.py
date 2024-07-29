import os
import argparse

SIZE = 40
port = 9090
start_port = 11001

# with open("/home/mitch/work/pes/measurements/break/adblock_detect/inner_pages_custom_break.json", "r") as f:
#     # has 16790 sites
#     allsite_dict = json.load(f)
#
# websites = []
# for key in allsite_dict:
#     websites.append(allsite_dict[key][0])
#
# websites = random.sample(websites, 4999)
# with open('websites.json', 'w') as f:
#     websites.append('http://www.thawte.com')
#     json.dump(websites, f)


extn_lst = ['control', 'adblock', 'ublock', 'privacy-badger']
HTML_ELEM = ['buttons', 'links', 'logins', 'drop_downs', 'inputs']
if __name__ == "__main__":
    # Parse the command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--replay', type=int, choices=[0, 1], required=True, help="Replay can only be 0 or 1")
    parser.add_argument('--html', type=str, choices=HTML_ELEM, nargs='+', help="HTML options: 'buttons', 'links', 'login', 'drop_downs', 'input'")
    parser.add_argument('--extn', type=str, choices=extn_lst, help="Extension options: 'control', 'adblock', 'ublock', 'privacy-badger'")
    parser.add_argument('--size', type=int, help="Size")

    args = parser.parse_args()

    for html in args.html:
        os.system(f"python3 crawler_breakage.py --replay {0} --html {html} --extn control --size {5}")

    for extn in args.extn:
        for html in args.html:
            os.system(f"python3 crawler_breakage.py --replay {1} --html {html} --extn {extn} --size {5}")
