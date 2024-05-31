import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException
from selenium_stealth import stealth
from pyvirtualdisplay import Display
from time import sleep
from PIL import Image
from urllib.parse import urlparse
import io
import os

SEEN = []
class Driver:
    def __init__(self):
        self.driver = None
        self.vdisplay = None

    def initialize(self, site, extn):
        try:
            xvfb_args = [
                '-maxclients', '1024'
            ]
            self.vdisplay = Display(backend='xvfb', size=(1920, 1280), visible=False, extra_args=xvfb_args)
            self.vdisplay.start()
            options = Options()
            if extn != 'control':
                options.add_extension(f"/home/character/Desktop/Ad-BlockerResearch/Extensions/extn_crx/{extn}.crx")

            options.add_argument("start-maximized")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument('--ignore-certificate-errors')
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-animations")
            options.add_argument("--disable-web-animations")
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-features=IsolateOrigins,site-per-process")
            options.add_argument("--disable-features=AudioServiceOutOfProcess")
            options.add_argument(
                "--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36")

            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
            stealth(driver,
                    languages=["en-US", "en"],
                    vendor="Google Inc.",
                    platform="Win32",
                    webgl_vendor="Intel Inc.",
                    renderer="Intel Iris OpenGL Engine",
                    fix_hairline=True,
                    )
            sleep(2)
            self.driver = driver
            self.driver.set_page_load_timeout(60)
            self.driver.get(site)
            sleep(3)

            print("taking ss of", extn)
            self.take_ss_entire(site, extn)

        except TimeoutException:
            print("Page load timed out")
        except Exception as e:
            print(str(e).split("\n")[0])
        self.cleanup()


    def take_ss_entire(self, url, extn):
        path = get_base_url(url)
        os.makedirs(f"results/{path}", exist_ok=True)

        self.driver.execute_script("window.scrollTo(0, 0);")
        sleep(1)
        self.driver.maximize_window()

        screenshots = []
        viewport_height = self.driver.execute_script("return window.innerHeight")
        page_height = self.driver.execute_script("return document.body.scrollHeight")
        page_width = self.driver.execute_script("return document.body.scrollWidth")
        scroll_height = 0

        while scroll_height < page_height:
            screenshot = self.driver.get_screenshot_as_png()
            screenshots.append(screenshot)

            scroll_height += viewport_height
            self.driver.execute_script(f"window.scrollTo(0, {scroll_height});")
            sleep(1)

        full_screenshot = Image.new('RGB', (page_width, page_height))
        current_height = 0
        for screenshot in screenshots:
            img = Image.open(io.BytesIO(screenshot))
            full_screenshot.paste(img, (0, current_height))
            current_height += viewport_height

        full_screenshot.save(f"results/{path}/" + f'{extn}_entire.png')

    def cleanup(self):
        if self.driver:
            self.driver.quit()
        if self.vdisplay:
            self.vdisplay.stop()


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


def issue_details(link, control, adguard):
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
    control.initialize(link, 'control')
    print("Finished Control")
    adguard.initialize(link, 'adguard')
    print("Finished Ad-guard")

    screen_shots = soup.find_all('details')
    for screen_shot in screen_shots:
        name = screen_shot.find('summary').text.strip()
        image = screen_shot.find('a', {'rel': "noopener noreferrer nofollow"})
        if image:
            image = image['href']
            response = requests.get(image)
            with open(f'results/{path}/{name}.png', 'wb') as file:
                file.write(response.content)

    problem_statement = soup.find('blockquote').find('p', {'dir': 'auto'}).text.strip()
    with open(f'results/{path}/comment.txt', 'w') as file:
        file.write(problem_statement)

    print("-" * 30)



def main():
    global SEEN

    print(os.getcwd())
    try:
        ADDRESS = "https://github.com/AdguardTeam/AdguardFilters/issues"
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
            driver1 = Driver()
            driver2 = Driver()
            issue_details(BASE_URL + issue_websites[website]['link'], driver1, driver2)


while 1:
    main()
    sleep(300) # check every 5 mins.