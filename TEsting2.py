from bs4 import BeautifulSoup



def parse_html_string(html_string):
    soup = BeautifulSoup(html_string, 'html.parser')
    if soup:
        tag = soup.find()
        if tag:
            tag_info = {
                'tag_name': tag.name,
                'attributes': tag.attrs
            }
            return tag_info
    return None


def generate_xpath(parsed_info):
    if parsed_info:
        tag_name = parsed_info['tag_name']
        attributes = parsed_info['attributes']

        xpath = f'//{tag_name}'
        for attr, value in attributes.items():
            if attr == 'class':
                if isinstance(value, list):
                    for v in value:
                        xpath += f'[contains(@{attr}, "{v}")]'
                else:
                    xpath += f'[contains(@{attr}, "{value}")]'
            else:
                if isinstance(value, list):
                    xpath += f'[@{attr}="{value[0]}"]'
                else:
                    xpath += f'[@{attr}="{value}"]'

        return xpath
    return None



# Your HTML string
html = '<button class="cdx-button cdx-search-input__end-button">Search</button>'

parsed_info = parse_html_string(html)
xpath = generate_xpath(parsed_info)
print(xpath)
