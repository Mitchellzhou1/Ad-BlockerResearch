SIZE = 40
port = 9090
start_port = 11001

with open("/home/mitch/work/pes/measurements/break/adblock_detect/inner_pages_custom_break.json", "r") as f:
    # has 16790 sites
    allsite_dict = json.load(f)

websites = []
for key in allsite_dict:
    websites.append(allsite_dict[key][0])

websites = random.sample(websites, 4999)
with open('/home/mitch/work/pes/measurements/break/html_elements/websites.json', 'w') as f:
    websites.append('http://www.thawte.com')
    json.dump(websites, f)