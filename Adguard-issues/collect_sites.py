import requests
from bs4 import BeautifulSoup
from time import sleep
from urllib.parse import urlparse
import os
import subprocess

SEEN = []

def get_issues(response):
    issues = {}
    soup = BeautifulSoup(response.text, 'html.parser')
    issue_divs = soup.find_all('div', class_='Box-row Box-row--focus-gray p-0 mt-0 js-navigation-item js-issue-row')
    for issue_div in issue_divs:
        website = issue_div.find('a', class_='Link--primary v-align-middle no-underline h4 js-navigation-open markdown-title')
        if website:
            website = website.prettify().split("\n")[1].strip()
            issues[website] = {}

            target_link = issue_div.find('a',
                                    class_='Link--primary v-align-middle no-underline h4 js-navigation-open markdown-title')
            if target_link:
                href_value = target_link.get('href').strip()
                issues[website]['link'] = href_value

            labels = issue_div.find_all('a', class_='IssueLabel hx_IssueLabel')
            total = []
            if labels:
                for label in labels:
                    label = label.prettify().split("\n")[1].strip()
                    total.append(label)

            issues[website]['labels'] = total

    return issues


def get_base_url(url):
    parsed_url = urlparse(url)
    return parsed_url.netloc


def issue_details(link):
    try:
        response = requests.get(link)
        print("-"*30)
        print("Testing:", link)
    except Exception as e:
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    link = soup.find('p', {'dir': 'auto'}).find('a').prettify().split("\n")[1].strip()
    print("website:", link)
    path = get_base_url(link)

    os.makedirs(f"results/{path}", exist_ok=True)

    screen_shots = soup.find_all('details')
    for screen_shot in screen_shots:
        name = screen_shot.find('summary').text.strip()
        image = screen_shot.find('a', {'rel': "noopener noreferrer nofollow"})
        if image:
            image = image['href']
            response = requests.get(image)
            with open(f'results/{path}/{name}.png', 'wb') as file:
                file.write(response.content)

    try:
        problem_statement = soup.find('blockquote').find('p', {'dir': 'auto'}).text.strip()
    except Exception as e:
        problem_statement = "No comment"
    with open(f'results/{path}/comment.txt', 'w') as file:
        file.write(problem_statement)

    print("-" * 30)
    return link, path



def main():
    global SEEN
    try:
        ADDRESS = "https://github.com/AdguardTeam/AdguardFilters/issues?q=is%3Aissue+is%3Aopen+label%3A%22N%3A+AdGuard+Browser+Extension%22"
        response = requests.get(ADDRESS)
        response.raise_for_status()
        issue_websites = get_issues(response)
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        exit()

    BASE_URL = 'https://github.com'
    filters = ['N: AdGuard Browser Extension', 'T: Incorrect Blocking']
    for website in issue_websites.keys():
        if website not in SEEN:
            SEEN.append(website)
        else:   # we have seen all the sites.
            return

        if all(filter_value in issue_websites[website]['labels'] for filter_value in filters):
            github_problem_site = BASE_URL + issue_websites[website]['link']
            site_to_check, path = issue_details(github_problem_site)
            subprocess.run(['python3', 'image_breakages.py', site_to_check, path])

i = 1
while i:
    main()  # collects the images and the problem statement
    print("Cycle", i)
    sleep(300) # check every 5 mins.
    i += 1