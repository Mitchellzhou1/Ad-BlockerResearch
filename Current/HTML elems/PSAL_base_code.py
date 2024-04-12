# import pyautogui

from functions import *

import re

# options = Options()
# # options.headless = False
# # options.add_argument("--headless=new")
# options.add_argument("--no-sandbox")
# options.add_argument("--disable-animations")
# options.add_argument("--disable-web-animations")
# # options.add_argument("--incognito")
# # options.add_argument("--single-process")
# options.add_argument("--disable-gpu")
# # options.add_argument("--disable-dev-shm-usage")
# options.add_argument("--disable-web-security")
# options.add_argument("--disable-features=IsolateOrigins,site-per-process")
# options.add_argument("--disable-features=AudioServiceOutOfProcess")
# # options.add_argument("auto-open-devtools-for-tabs")
# options.add_argument(
#     "user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36")

# options.binary_location = '/home/mitch/work/pes/chrome_113/chrome'


attributes_dict = {
    "buttons": {
        "attributes": ['button', 'submit', '#'],
        "xpaths": ['@role', '@type']
    },
    "drop downs": {
        "attributes": ['false', 'true', 'main menu', 'open menu', 'all microsoft menu', 'menu', 'navigation',
                       'primary navigation', 'hamburger', 'settings and quick links', 'dropdown', 'dialog',
                       'js-menu-toggle', 'searchDropdownDescription', 'ctabutton',
                       'legacy-homepage_legacyButton__oUMB9 legacy-homepage_hamburgerButton__VsG7q',
                       'Toggle language selector', 'Open Navigation Drawer', 'guide', 'Expand Your Library',
                       'Collapse Your Library'],
        "xpaths": ['@aria-expanded', '@aria-label', '@class', '@aria-haspopup', '@aria-describedby', '@data-testid']
    },
    "links": {
        "attributes": [],
        "xpaths": ['href']
    },
    "login": {  # remember to enable HREF
        "attributes": ['button', 'submit', '#'],
        "xpaths": ['@role', '@type']
    }
    , "manual": {
        "attributes": [],
        "xpaths": []
    }

}


def error_catcher(e, driver, tries, url):
    error = ''
    if driver.tries != 3:
        driver.reinitialize()
        tries += 1
        return tries

    # if isinstance(e, ElementClickInterceptedException):
    #     error = "N/A - Element Click Intercepted"
    if isinstance(e, ElementNotSelectableException):
        error = "N/A - Not Selectable"
    elif isinstance(e, StaleElementReferenceException):
        error = "StaleElementReferenceException"
    elif isinstance(e, NoSuchElementException):
        error = "N/A - No such Element"
    elif isinstance(e, InvalidSelectorException):
        error = "N/A - InvalidSelectorException"
    elif isinstance(e, IndexError):
        error = e
    elif isinstance(e, TimeoutError):
        print("Timeout")
        # write_noscan_row(url)
        tries = 1
        driver.tries = 1
        driver.curr_elem += 1
        print("TIME OUT EERRORRR")
        return tries
    else:
        error = str(e).split("\n")[0]
    return error


class TimeoutError(Exception):
    pass


class PSALDriver:
    def __init__(self, attributes, xPATH, adB, replay, data_dict, excel_dict, hierarchy_dict):
        # specific test for these attributes
        self.attributes = attributes
        self.xPaths = xPATH

        # initializing the adBlocker
        self.adBlocker_name = adB
        self.driver = None
        self.tries = 1
        self.vdisplay = ''
        self.actions = None

        # used for optimization
        self.keywords = [
            'login', 'my account', 'sign in', 'sign-in', 'signin', 'log in',  # English
            '登录', '我的帐户',  # Chinese (Simplified)
            'вход', 'войти', 'мой аккаунт',  # Russian
            'iniciar sesión', 'mi cuenta'  # Spanish
        ]
        self.seen_sites = []
        self.xpath_remover = 3
        self.website_sleep_time = 3  # longer this value, more consistent the results
        self.html_obj = ''
        self.DOM_traversal_amt = 4
        self.scan_timeout = 180
        self.test_elem_timeout = 300

        # used for testing
        self.curr_site = 0
        self.curr_elem = 0
        self.initial_outer_html = ''
        self.after_outer_html = ''
        self.initial_local_DOM = ''
        self.after_local_DOM = ''
        self.url = ''
        self.url_key = ''
        self.redirect_url = ''
        self.DOM_changed = False
        self.outer_HTML_changed = False

        # used for random picking
        self.dictionary = data_dict
        self.excel = excel_dict
        self.hierarchy = hierarchy_dict
        self.excel_list = []
        self.excel_errors_list = []

        self.all_sites = {}
        self.no_elms = 15
        self.chosen_elms = []
        self.all_html_elms = []

        #### RITIK
        self.options = ''
        self.replay = replay

    # def initialize(self, options, num_tries, url):
    #     """
    #         This function will start a Chrome instance with the option of installing an ad blocker.
    #         Adjust the seconds parameter so that it will wait for the ad blocker to finish downloading.
    #     """
    #     self.url_key = url
    #
    #     key = ''
    #     if 'www' in url:
    #         key = url.split('www.')[1]
    #     if '://' in key:
    #         key = key.split('://')[1]
    #     # Specify the version of Chrome browser you are using
    #     self.chrome_version = "113.0.5672.0"  # Chrome browser version
    #
    #     while num_tries > 0:
    #         try:
    #             self.options = options
    #             log_file_path = f"/home/mitch/work/pes/measurements/break/html_elements/logs/chromedriver_{key}.log"
    #             service = Service(executable_path='/home/mitch/work/pes/chromedriver_113/chromedriver',
    #                               service_args=["--verbose", f"--log-path={log_file_path}"])
    #             # service = Service(ChromeDriverManager(version=self.chrome_version).install(), service_args=["--verbose", f"--log-path={log_file_path}"])
    #             self.driver = webdriver.Chrome(options=options, service=service)
    #             self.driver.set_page_load_timeout(45)
    #             time.sleep(2)
    #             break
    #         except Exception as e:
    #             if num_tries == 1:
    #                 print(f"couldn't create browser session... not trying again -- {self.url_key}")
    #                 error(self.url_key, self.html_obj, inspect.currentframe().f_code.co_name, e)
    #                 # print(1, e)
    #                 return 0
    #             else:
    #                 print("couldn't create browser session... trying again")
    #                 num_tries = num_tries - 1
    #                 time.sleep(5)
    #
    #     if self.adBlocker_name == 'adblock':
    #         time.sleep(15)
    #     elif self.adBlocker_name == 'ghostery':
    #         windows = self.driver.window_handles
    #         for window in windows:
    #             try:
    #                 self.driver.switch_to.window(window)
    #                 url_start = self.driver.current_url[:16]
    #                 if url_start == 'chrome-extension':
    #                     element = self.driver.find_element(By.XPATH, "//ui-button[@type='success']")
    #                     element.click()
    #                     time.sleep(2)
    #                     break
    #             except Exception as e:
    #                 error(self.url_key, self.html_obj, inspect.currentframe().f_code.co_name, e)
    #                 # print('ghostery', 1, e)
    #                 return 0
    #     return 1

    def initialize(self, seconds=14):
        """
            This function will start a Chrome instance with the option of installing an ad blocker.
            Adjust the seconds parameter so that it will wait for the ad blocker to finish downloading.
        """
        current_dir = os.path.dirname(os.path.realpath(__file__))
        parent_directory = os.path.dirname(os.path.dirname(current_dir))
        extensions_dir = os.path.abspath(os.path.join(parent_directory, 'Extensions', 'Ad-Blockers'))

        proxy_address = "127.0.0.1:8080"
        chrome_options = webdriver.ChromeOptions()
        # chrome_options.add_extension('Captcha-Solver-Auto-Recognition-and-Bypass.crx')
        chrome_options.add_argument('--enable-logging')
        options.add_argument('--proxy-server={}'.format(proxy_address))
        if self.adBlocker_name == 'AdBlockPlus':
            extension_path = os.path.join(extensions_dir, 'adBlockerPlus.crx')
            chrome_options.add_extension(extension_path)
        elif self.adBlocker_name == 'uBlock':
            extension_path = os.path.join(extensions_dir, 'uBlock-Origin.crx')
            chrome_options.add_extension(extension_path)

        chrome_options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        # self.driver = webdriver.Chrome(options=options)

        self.driver.set_window_size(1555, 900)
        # give it time to install
        if self.adBlocker_name == 'AdBlockPlus':
            sleep(seconds)
            pyautogui.hotkey('ctrl', 'w')
        self.actions = ActionChains(self.driver)

        # if self.html_obj:
        #     file_path = f'{self.html_obj}.replay_0'
        #     with open(file_path, 'r') as json_file:
        #         self.dictionary = replay_0.load(json_file)
        #     self.all_sites = list(self.dictionary.keys())

    def replay_initialize(self):
        # print('replay_initialize', self.html_obj)
        # used for testing
        self.curr_site = 0
        self.curr_elem = 0
        self.initial_outer_html = ''
        self.after_outer_html = ''
        self.initial_local_DOM = ''
        self.after_local_DOM = ''
        self.DOM_changed = False
        self.outer_HTML_changed = False
        # during replay phase
        # if self.replay:
        file_path = f"replay_0/{self.html_obj}_control.replay_0"
        # self.excel[self.adBlocker_name][self.html_obj][self.url_key] = []
        # self.excel['errors'][self.adBlocker_name][self.html_obj][self.url_key] = []

        try:
            if os.path.isfile(file_path):
                with open(file_path, 'r') as json_file:
                    self.dictionary = {}
                    self.dictionary[self.adBlocker_name] = {}
                    self.dictionary[self.adBlocker_name][self.html_obj] = {}
                    self.dictionary[self.adBlocker_name][self.html_obj][self.url_key] = replay_0.load(json_file)[
                        self.url_key]
                    # self.dictionary[self.url_key] = replay_0.load(json_file)[self.url_key]
                json_file.close()

            elems = self.dictionary[self.adBlocker_name][self.html_obj][self.url_key]
            self.all_sites = [self.url_key]

            # print('self.dictionary', self.dictionary)
        except KeyError as k:
            print(f"site not found in replay_0 --- site:{self.url_key}, extn:{self.adBlocker_name}, html: {self.html_obj}")
            return 0
        except Exception as e:
            error(self.url_key, self.html_obj, inspect.currentframe().f_code.co_name, e)
            # print(4, e)
            return 0

    time.sleep(2)

    def get_excel_dict(self):
        return self.excel[self.adBlocker_name][self.html_obj]

    def set_html_obj(self, html_obj):
        self.html_obj = html_obj
        return

    def is_loaded(self):
        return self.driver.execute_script("return document.readyState") == "complete"

    def wait_until_loaded(self, timeout=60, period=0.25, min_time=0):
        start_time = time.time()
        mustend = time.time() + timeout
        while time.time() < mustend:
            if self.is_loaded():
                if time.time() - start_time < min_time:
                    time.sleep(min_time + start_time - time.time())
                return True
            time.sleep(period)
        return False

    def get_url_key(self):
        return self.url_key

    def load_site(self, url):
        """
            makes selenium load the site. will add http://www. if needed and filters out to see if the website is
            accessible or not.
        """
        try:
            if self.driver == None:
                error(self.url_key, self.html_obj, inspect.currentframe().f_code.co_name,
                      f"driver doesn't exist for {self.url_key}")
                # print(1, self.html_obj)
                return False
            self.driver.get(url)
            self.wait_until_loaded()
            time.sleep(2)

            self.url = self.driver.current_url
            # self.url_key = url
            if self.url not in self.seen_sites:
                # write_results(self.url)
                self.seen_sites.append(self.url)
            # print(2, self.html_obj)
            return True

        except Exception as e:
            self.dictionary['errors'][self.adBlocker_name][self.url_key] = str(e)
            # print(3, e)
            error(self.url_key, self.html_obj, inspect.currentframe().f_code.co_name, e)
            # self.seen_sites.append(url)
            return False

    # def remove_stuff(self):
    #     remove_popup(self.driver)
    #     remove_alert(self.driver) # optional

    def reinitialize(self):
        self.driver.close()
        self.initialize()
        self.tries += 1

    def scroll(self):
        curr_scroll_position = -1
        curr_time = time.time()
        while True:
            # Define the scroll step size
            scroll_step = 50  # Adjust this value to control the scroll speed
            # Get the current scroll position
            scroll_position = self.driver.execute_script("return window.pageYOffset;")
            # Check if we've reached the bottom
            if curr_scroll_position == scroll_position:
                break
            else:
                curr_scroll_position = scroll_position

            # Scroll down by the step size
            self.driver.execute_script(f"window.scrollBy(0, {scroll_step});")

            # Wait for a bit (this controls the scroll speed indirectly)
            time.sleep(0.1)  # Adjust this value to control the scroll speed
            if time.time() - curr_time >= 45:
                break

    def take_ss(self, fname):
        try:
            # filepath = f'/home/mitch/work/pes/measurements/break/html_elements/page_ss/{self.html_obj}'
            if '//' in fname:
                fname = fname.split('//')[1]
            filepath = f'/home/mitch/work/pes/measurements/break/html_elements/test_ss'
            if not os.path.isdir(filepath):
                os.makedirs(filepath, exist_ok=True)
            if self.driver != None:
                self.driver.save_screenshot(f'{filepath}/{fname}')
        except Exception as e:
            error(self.url_key, self.html_obj, inspect.currentframe().f_code.co_name, e)

    def get_logs(self):
        if self.driver == None:
            error(self.url_key, self.html_obj, inspect.currentframe().f_code.co_name,
                  f"driver doesn't exist for {self.url_key}")
            return None
        return self.driver.get_log('browser')

    def close(self):
        print("closing driver...", self.adBlocker_name, self.html_obj, self.url)
        # print('*'*25)
        # print(self.html_obj)
        # print(self.excel[self.adBlocker_name][self.html_obj])
        if self.driver != None:
            self.driver.quit()
        # self.vdisplay.stop()

    def click_button(self, button):
        try:
            self.actions.move_to_element(button).perform()
            button.click()
        except Exception:
            self.driver.execute_script(
                "arguments[0].scrollIntoView({ behavior: 'auto', block: 'center', inline: 'center' });", button)
            sleep(2)
            button.click()

    def cursor_change(self, element):
        # print(element.get_attribute('outerHTML'))
        try:
            self.actions.move_to_element(element).perform()
            sleep(1)
            cursor_property = element.value_of_css_property('cursor')
            if cursor_property == 'pointer':
                return True
            else:
                return False
        except Exception as e:
            # error(self.url_key, self.html_obj, inspect.currentframe().f_code.co_name, e)
            return False

    def check_redirect(self, url):
        def are_urls_equal(url1, url2):
            path1 = url1.rstrip('/').strip('https://').strip('www.')
            path2 = url2.rstrip('/').strip('https://').strip('www.')
            return path1 == path2

        sleep(3)
        if not are_urls_equal(self.driver.current_url, url):
            return True, self.driver.current_url

        all_windows = self.driver.window_handles

        # tests for more windows and will close them
        if len(all_windows) > 1:
            for window in all_windows[1:]:
                self.driver.switch_to.window(window)
                self.driver.close()
            self.driver.switch_to.window(all_windows[0])
            return True, self.driver.current_url
        return False, self.driver.current_url

    def count_tags(self):
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        tags = soup.find_all()
        return len(tags)

    def get_local_DOM(self, elem, level=None):
        amt = self.DOM_traversal_amt
        if level:
            amt = level
        for i in range(amt):
            elem = elem.find_element(By.XPATH, '..')
        return elem.get_attribute('outerHTML')

    def generate_xpath(self, html_string):
        def parse_html_string(string):
            soup = BeautifulSoup(string, 'html.parser')
            if soup:
                tag = soup.find()
                if tag:
                    tag_info = {
                        'tag_name': tag.name,
                        'attributes': tag.attrs
                    }
                    return tag_info
            return None

        def format_attribute(attr, value):
            # if "'" in value:
            #     value_lst = value.split("'")
            #     return "[contains(@" + attr + ", " + "concat(" + value_lst[0] + ", \"'\", " + value_lst[1] + ", \"'\", " + value_lst[2] + "))]"

            if isinstance(value, list):
                return f'[contains(@{attr}, "{value[0]}")]'
            else:
                if "'" and '"' in value:
                    return ''  # this case is too weird. will just skip it.
                elif "'" in value:
                    return f"""[@{attr}="{value}"]"""
                return f"""[@{attr}='{value}']"""

        parsed_info = parse_html_string(str(html_string))
        if parsed_info:
            tag_name = parsed_info['tag_name']
            attributes = parsed_info['attributes']

            xpath = f'//{tag_name}'
            for attr, value in attributes.items():
                if attr == 'class':
                    if isinstance(value, list):
                        for class_value in value:
                            xpath += f'[contains(@{attr}, "{class_value}")]'
                    else:
                        xpath += f'[contains(@{attr}, "{value}")]'
                else:
                    xpath += format_attribute(attr, value)

            return xpath
        return None

    def get_correct_elem(self, xpath, outerHTML):
        counter = self.xpath_remover
        while "[" in xpath and counter:
            elements = self.driver.find_elements(By.XPATH, xpath)  # will return [] if none are found
            for i in elements:
                if i.get_attribute("outerHTML") == outerHTML:
                    return i
            try:  # sometimes the structure is the same.
                return self.driver.find_element(By.XPATH, xpath)
            except Exception:
                button_part = xpath.split("[")[0]
                xpath_list = re.findall(r'\[@.*?\]', xpath)
                rem_candidate = max(xpath_list, key=len)
                if "aria-label" in rem_candidate:
                    rem_candidate = min(xpath_list, key=len)
                xpath_list.remove(rem_candidate)
                xpath = ''.join([button_part] + xpath_list)
            counter -= 1
        try:
            return self.driver.find_element(By.XPATH, xpath)  # will error if none are found
        except Exception as e:
            print("Didn't find element")
        return None

    def check_opened(self, url, button, initial_tag):
        def check_HTML(initial, after):
            if initial != after:
                return "True"
            return "False"

        redirect, new_url = self.check_redirect(url)
        if redirect:
            return "True - Redirect"

        try:
            self.after_outer_html = button.get_attribute('outerHTML')
        except StaleElementReferenceException:
            # this is good, means that the button disappeared after clicking
            # could be things like "close", "search", "expand", "show more", etc.
            return "True - Stale Element"

        self.DOM_changed = check_HTML(self.initial_local_DOM, self.get_local_DOM(button))
        self.outer_HTML_changed = check_HTML(self.initial_outer_html, self.after_outer_html)

        if self.outer_HTML_changed:
            return "True - outerHTML change"

        if self.DOM_changed:
            return "True? - Local DOM Change"

        if self.count_tags() > initial_tag:
            return "True - More Tags"

        return "False"

    # @timeout(300)
    def test_button(self, tries):
        site = self.all_sites[self.curr_site]
        self.load_site(site)
        try:
            # outerHTML, refresh = self.dictionary[self.adBlocker_name][self.html_obj][site][self.curr_elem]
            outerHTML, refresh = self.dictionary[site][self.curr_elem]
            xpath = self.generate_xpath(outerHTML)
        except IndexError as e:
            self.excel_errors_list.append(['IndexError: list is empty', '', '', self.initial_outer_html, '', '', '',
                                           self.url_key, self.driver.current_url, tries])
            return

        except Exception as e:
            # print(e)
            error(self.url_key, self.html_obj, inspect.currentframe().f_code.co_name, e)
            self.excel_errors_list.append(["Unknown Exception", '', '', self.initial_outer_html, '', '', '',
                                           self.url_key, self.driver.current_url, tries])
            return

        if refresh:
            self.load_site(site)
        self.initial_outer_html = outerHTML
        element = self.get_correct_elem(xpath, outerHTML)
        if element == None:
            self.excel_errors_list.append(["Can't find element", '', '', self.initial_outer_html, '', '', '',
                                           self.url_key, self.driver.current_url, tries])
            return
        self.initial_local_DOM = self.get_local_DOM(element)

        initial_tag = self.count_tags()

        self.click_button(element)

        check = self.check_opened(self.url, element, initial_tag)

        if check == "True - Redirect":
            # outer_HTML_change = url
            # Dom_change = new_url
            self.excel_list.append([check, '', '', self.initial_outer_html, '', '', '',
                                    self.url, self.driver.current_url, tries])
        elif check == "True - outerHTML change" or check == "True - Stale Element":
            self.excel_list.append([check, self.outer_HTML_changed, self.DOM_changed, self.initial_outer_html,
                                    self.after_outer_html, '', '', '', '', tries])

        elif check == "True? - Local DOM Change":
            # need to figure out algo after find the difference
            self.excel_list.append([check, self.outer_HTML_changed, self.DOM_changed, self.initial_outer_html, '',
                                    self.initial_local_DOM, self.after_local_DOM, '', '', tries])

        elif check == "True - More Tags":
            # need to figure out algo after find the difference
            write_results([check, self.outer_HTML_changed, self.DOM_changed, self.initial_outer_html, '',
                           self.initial_local_DOM, self.after_local_DOM, '', '', tries])

        elif check == "False":
            # FALSE POSITIVE CHECKSSS
            if self.is_slideshow(self.initial_outer_html):
                check = 'True? - slideshow'
            elif self.is_required(self.initial_outer_html):
                check = 'True? - input is required'
            elif self.is_scrollpage(self.initial_outer_html):
                check = 'True? - page was scrolled'
            elif self.is_download_link(self.initial_outer_html):
                check = 'True? - download link'
            elif self.is_open_application(self.initial_outer_html):
                check = 'True? - opened application'
            else:
                self.dictionary[site][self.curr_elem][1] = 0
                lst = self.dictionary[self.all_sites[self.curr_site]]
                if self.curr_elem + 1 < len(lst):
                    lst[self.curr_elem], lst[self.curr_elem + 1] = lst[self.curr_elem + 1], lst[self.curr_elem]
                    self.curr_elem -= 1
                return
            self.excel_list.append([check, "False", "False", self.initial_outer_html, '',
                                    "", "", '', '', tries])

    # def click_on_elms(self, tries):
    #     while self.curr_site < len(self.all_sites):
    #         # print(f'curr_site: {self.curr_site}, all_sites: {self.all_sites}, curr_elem: {self.curr_elem}, xpaths: {self.dictionary[self.adBlocker_name][self.html_obj][self.all_sites[self.curr_site]]}')
    #         if self.curr_elem >= len(
    #                 self.dictionary[self.adBlocker_name][self.html_obj][self.all_sites[self.curr_site]]):
    #             self.curr_site += 1
    #             self.curr_elem = 0
    #         else:
    #             self.test_button(tries)
    #             self.curr_elem += 1
    #
    #     self.curr_site = -1
    #     self.excel[self.adBlocker_name][self.html_obj][self.url_key] = self.excel_list
    #     self.excel['errors'][self.adBlocker_name][self.html_obj][self.url_key] = self.excel_errors_list

    def click_on_elms(self, tries):

        while self.curr_site < len(self.all_sites):
            if self.curr_elem >= len(self.dictionary[self.all_sites[self.curr_site]]):
                self.curr_site += 1
                self.curr_elem = 0
            else:
                self.test_button(tries)
                self.curr_elem += 1

        self.curr_site = -1

    def hierarchy_change(self, tries):
        while self.curr_site < len(self.all_sites):
            if self.curr_elem >= len(
                    self.dictionary[self.adBlocker_name][self.html_obj][self.all_sites[self.curr_site]]):
                self.curr_site += 1
                self.curr_elem = 0
            else:
                outerhtml, counter = self.hierarchy_helper(tries)
                self.excel_list.append([outerhtml, counter])
                self.curr_elem += 1

        self.curr_site = -1
        self.excel[self.adBlocker_name][self.html_obj][self.url_key] = self.excel_list
        self.excel['errors'][self.adBlocker_name][self.html_obj][self.url_key] = self.excel_errors_list

    # @timeout(300)
    def hierarchy_helper(self, tries):
        # grab current site
        site = self.all_sites[self.curr_site]
        self.load_site(site)
        try:
            # get outer HTML and generate the Xpath for it
            outerHTML = self.dictionary[self.adBlocker_name][self.html_obj][site][self.curr_elem]
            xpath = self.generate_xpath(outerHTML)
            element = self.get_correct_elem(xpath, outerHTML)
            print(site, element.get_attribute("outerHTML"))
            self.take_ss(f"{self.url_key}.png")
            if element:
                print("ELEMENT FOUND")
            else:
                print("ELEMENT NOT FOUND", xpath)
                return outerHTML, "None"
            initial_outer, initial_DOM, initial_url = self.get_comparison_elms(element)

        except Exception as e:
            print("\n\n went in here \n\n", xpath, outerHTML, "\n\n")
            print(e)
            return None, None

        try:
            self.driver.execute_script(
                "arguments[0].scrollIntoView({ behavior: 'auto', block: 'center', inline: 'center' });", element)
            time.sleep(1)
            element.click()
            time.sleep(1)
            try:
                element.click()
                time.sleep(1)
                element.click()
            except Exception as e:
                # print("click button once!", site)
                pass

            if initial_url != self.driver.current_url:
                return outerHTML, "0"
            time.sleep(2)

        except Exception as e:
            print("1) can't click on element", initial_url)
            print(e)
            return outerHTML, "Can't click on element"

        all_windows = self.driver.window_handles

        # tests for more windows and will close them
        print("CLOSING THE ADDITONAL WINDOWS")
        if len(all_windows) > 1:
            for window in all_windows[1:]:
                self.driver.switch_to.window(window)
                self.driver.close()
                self.driver.switch_to.window(all_windows[0])
        print("GOING INTO TRY BLOCK")
        try:
            print(element.get_attribute('outerHTML'))
            after_outer, after_DOM, after_url = self.get_comparison_elms(element)
            print("\n\n\n\nTHIS FINISHED\n\n\n\n")

            tag_initial, attribute_initial = self.generate_path(initial_outer)
            tag_after, attribute_after = self.generate_path(after_outer)
            print("THIS RAN22222")

            control_code = BeautifulSoup(initial_DOM, 'html.parser')
            clicked_code = BeautifulSoup(after_DOM, 'html.parser')

            control = control_code.find(tag_initial, attribute_initial)
            clicked = clicked_code.find(tag_after, attribute_after)
            print("THIS RAN33333")
        except Exception as e:
            print(e)
            print("\n\n\n\nelement dissapeared\n\n\n\n")
            return outerHTML, "0"

            counter = None
        if control and clicked:
            print("\n\n\n WENT IN HERE \n\n\n")
            counter = 0
            while control.parent and clicked.parent and control == clicked:
                control = control.parent
                clicked = clicked.parent
                counter += 1
            # if for some reason I cannot detect a change with the entire DOM something wierd probably happened
            if control == clicked:
                counter = None
            # hierarchy_dict[self.html_obj].append([site, outerHTML, control, clicked, counter])
            print(initial_url, counter)
        return outerHTML, str(counter)

    ############################################################

    """            
            FINDING AND FILTERING THE HTML Elements
    """

    ############################################################
    # @timeout(300)
    def scan_page(self):
        self.load_site(self.url)  # extra refresh helps get rid of some false findings
        self.get_elements()
        self.dictionary[self.url] = self.chosen_elms
        # while self.curr_elem < len(self.dictionary[self.url]):
        #     try:
        #         xpath = self.generate_xpath(self.dictionary[self.url][self.curr_elem])
        #         elm = self.get_correct_elem(xpath, self.initial_outer_html)
        #         elm.click()
        #         sleep(1)
        #         self.load_site(self.url)
        #     except Exception:
        #         pass
        #     self.curr_elem += 1
        all_windows = self.driver.window_handles
        if len(all_windows) > 1:
            for window in all_windows[1:]:
                self.driver.switch_to.window(window)
                self.driver.close()
            self.driver.switch_to.window(all_windows[0])
        self.curr_elem = 0
        self.curr_site += 1

        storeDictionary(self.dictionary)



    def PSAL_scan_page(self):
        self.load_site(self.url)  # extra refresh helps get rid of some false findings
        self.get_elements()
        self.dictionary[self.adBlocker_name][self.html_obj][self.url_key] = self.chosen_elms

        print("*" * 50)
        print(self.url_key, self.dictionary[self.adBlocker_name][self.html_obj][self.url_key])
        print("*" * 50)
        while self.curr_elem < len(self.dictionary[self.adBlocker_name][self.html_obj][self.url_key]):
            try:
                xpath = self.generate_xpath(
                    self.dictionary[self.adBlocker_name][self.html_obj][self.url_key][self.curr_elem])
                elm = self.get_correct_elem(xpath)
                elm.click()
                sleep(1)
                self.load_site(self.url)
            except Exception as e:
                # print(e)
                # print("error in clicking element or generating xpath")
                pass
            all_windows = self.driver.window_handles

            # tests for more windows and will close them
            if len(all_windows) > 1:
                for window in all_windows[1:]:
                    self.driver.switch_to.window(window)
                    self.driver.close()
                self.driver.switch_to.window(all_windows[0])

            self.curr_elem += 1
        self.curr_elem = 0
        self.curr_site += 1

        # storeDictionary(self.dictionary[self.adBlocker_name][self.html_obj], self.html_obj, self.adBlocker_name)

    def write_num_elem_found(self, numb):
        file_path = f"replay_0/{self.html_obj}_{self.adBlocker_name}_ammt.txt"
        with open(file_path, 'a+') as file:
            file.write(self.url_key + " " + str(numb) + "\n")

    def get_elements(self):
        # returns the contents (will be selenium objs)
        ret = []
        if self.html_obj == "drop downs":
            ret = self.find_dropdown()
        elif self.html_obj == "buttons":
            ret = self.find_buttons()
        elif self.html_obj == "links":
            ret = self.find_links()
        elif self.html_obj == "login":
            ret = self.find_login()
        elif self.html_obj == "input":
            ret = self.find_forms()
        else:
            print("Invalid Element type to retrieve")

        if self.html_obj == "login":
            final_lst = []
            for index in range(len(ret)):
                try:
                    if self.filter(ret[index]):
                        final_lst.append(ret[index])
                except Exception as e:
                    continue
        else:
            # random.shuffle(ret)   No random shuffle so that the slideshows are better to click on
            unique = []
            limit = min(15, len(ret))
            total_valid_elems = 0
            for elem in ret:
                # print(len(unique), elem.get_attribute("outerHTML"))
                if len(unique) < limit and elem.get_attribute("outerHTML") not in unique:
                    if self.html_obj != "input":
                        if not self.filter(elem):
                            continue
                    unique.append(elem.get_attribute("outerHTML"))
                    total_valid_elems += 1

            self.chosen_elms = [[elem, 1] for elem in unique]

            self.write_num_elem_found(total_valid_elems)  # unique by looking at the outerHTML

        # the chosen_elms will be the unique outerHTML
        # if len(self.chosen_elms) <= self.no_elms:
        #     write_results(f"testing {len(self.chosen_elms)} / {len(self.chosen_elms)}")
        # else:
        #     write_results(f"testing {len(self.chosen_elms)} / {self.no_elms}")

    def filter(self, element):

        if self.html_obj == "login":
            if any(keyword.lower() in element.text.lower() for keyword in self.keywords):
                if self.cursor_change(element):
                    print(f"{self.url} \t {element.text}")
                    return True
        elif self.cursor_change(element):  # and element.is_displayed()   not always working correctly :(
            return True
        else:
            return False

    def specific_element_finder(self, found_elements=None):
        # will just add on to the current found_elements list.
        if not found_elements:
            found_elements = []
        for attribute in self.attributes:
            for path in self.xPaths:
                xpath = (f'//*[translate({path}, "ABCDEFGHIJKLMNOPQRSTUVWXYZ", '
                         f'"abcdefghijklmnopqrstuvwxyz")="{attribute.lower()}"]')
                try:
                    elements = self.driver.find_elements(By.XPATH, xpath)
                    for element in elements:
                        if element not in found_elements:
                            if self.html_obj == "buttons" and "href" not in element.get_attribute("outerHTML"):
                                found_elements.append(element)
                            else:
                                found_elements.append(element)
                except Exception as e:
                    self.dictionary['errors'][self.adBlocker_name][self.url_key] = str(e)
                    # print(2, e)
                    error(self.url_key, self.html_obj, inspect.currentframe().f_code.co_name, e)
        return found_elements

    def find_buttons(self):
        def collect():
            found_elements = self.driver.find_elements(By.TAG_NAME, 'button')
            for anchor in self.driver.find_elements(By.TAG_NAME, 'a'):
                if anchor.get_attribute("href") is None:
                    found_elements.append(anchor)

            final = self.specific_element_finder(found_elements)
            return final

        try:
            ret = collect()
            return ret
        except Exception as e:  # not tested
            try:
                sleep(5)
                return collect()
            except Exception as e:
                error_message = [str(e).split('\n')[0], "Failed to scrape Site", "", "", ""]
                self.excel_errors_list.append(error_message)

    def find_dropdown(self):
        try:
            ret = self.specific_element_finder()
            return ret
        except Exception as e:
            try:
                sleep(5)
                return self.specific_element_finder()
            except Exception as e:
                error_message = [str(e).split('\n')[0], "Failed to scrape Site", "", "", ""]
                self.excel_errors_list.append(error_message)

    def find_links(self):
        def collect():
            final = []
            for anchor in self.driver.find_elements(By.TAG_NAME, 'a'):
                if anchor.get_attribute("href"):
                    final.append(anchor)

            return final

        try:
            ret = collect()
            return ret
        except Exception as e:  # not tested
            try:
                sleep(5)
                return collect()
            except Exception as e:
                error_message = [str(e).split('\n')[0], "Failed to scrape Site", "", "", ""]
                self.excel_errors_list.append(error_message)

    def find_login(self):
        def collect():
            found_elements = self.driver.find_elements(By.TAG_NAME, 'button')
            found_elements += self.driver.find_elements(By.TAG_NAME, 'a')
            final = self.specific_element_finder(found_elements)
            return final

        try:
            ret = collect()
            # for i in ret:
            #     print(i.get_attribute("outerHTML"))
            return ret
        except Exception as e:  # not tested
            try:
                sleep(5)
                return collect()
            except Exception as e:
                error_message = [str(e).split('\n')[0], "Failed to scrape Site", "", "", ""]
                self.excel_errors_list.append(error_message)


    def find_forms(self):
        try:
            ret = self.driver.find_elements(By.TAG_NAME, 'form')
            # ret += self.specific_element_finder()
            return ret
        except Exception as e:
            try:
                sleep(5)
                return self.specific_element_finder()
            except Exception as e:
                error_message = [str(e).split('\n')[0], "Failed to scrape Site", "", "", ""]
                self.excel_errors_list.append(error_message)

    # ******************************************************
    #         FALSE POSITIVE
    # ******************************************************

    def is_slideshow(self, html):
        html = html.lower()
        possible = ['active', 'aria-pressed="true"', 'aria-selected="true"']
        for attribute in possible:
            if attribute in html:
                return None
        return False

    def is_required(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        tag = soup
        if soup.find() == 'input':
            return True
        keywords = ['aria-disabled="true"', ' disabled ', 'disabled=""']
        if any(keyword in html.lower() for keyword in keywords):
            return True
        return False

    def is_scrollpage(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        # Find all <a> tags with href starting with "#"
        scroll_links = soup.find_all('a', href=lambda href: href and href.startswith('#') and len(href) > 1)
        if scroll_links:
            return True

        keywords = ['scrollintoview', 'scroll-down']
        if any(keyword in html.lower() for keyword in keywords):
            return True
        return False

    def is_download_link(self, html):
        file_extensions = [
            '.aac', '.aif', '.aifc', '.aiff', '.au', '.avi', '.bat', '.bin', '.bmp', '.bz2',
            '.c', '.class', '.com', '.cpp', '.css', '.csv', '.dat', '.dmg', '.doc', '.docx',
            '.dot', '.dotx', '.eps', '.exe', '.flac', '.flv', '.gif', '.gzip', '.h', '.htm',
            '.html', '.ico', '.iso', '.java', '.jpeg', '.jpg', '.js', '.replay_0', '.log', '.m4a',
            '.m4v', '.mid', '.midi', '.mov', '.mp3', '.mp4', '.mpa', '.mpeg', '.mpg', '.odp',
            '.ods', '.odt', '.ogg', '.otf', '.pdf', '.php', '.pl', '.png', '.ppt', '.pptx',
            '.ps', '.psd', '.py', '.qt', '.rar', '.rb', '.rtf', '.s', '.sh', '.svg', '.swf',
            '.tar', '.tar.gz', '.tex', '.tif', '.tiff', '.ttf', '.txt', '.wav', '.webm', '.wma',
            '.wmv', '.woff', '.woff2', '.xls', '.xlsx', '.xml', '.yml', '.zip', '.apk'
        ]
        if any(html.endswith(ext) for ext in file_extensions):
            return True

        # Check if URL contains certain keywords
        if 'download' in html.lower() or 'file' in html.lower():
            return True
        return False

    def is_open_application(self, html):
        potential = ['mailto', 'tel', 'sms']
        for attribute in potential:
            if attribute in html.lower():
                return True
        return False

    def get_comparison_elms(self, element):
        outerHTML = element.get_attribute('outerHTML')
        print("OUTERHTML:", outerHTML)
        DOM = self.driver.page_source
        URL = self.driver.current_url
        print("current_url:", URL)
        return outerHTML, DOM, URL

    def generate_path(self, html_code):
        soup = BeautifulSoup(html_code, 'html.parser')
        tag = soup.find()
        tag_name = tag.name
        attributes = tag.attrs
        return tag_name, attributes

    # def write_results_DOM(self, hierarchy_dict):
    #     with open(f"hierarchy/final_hierarchy_results.replay_0", 'w') as json_file:
    #         replay_0.dump(hierarchy_dict, json_file)
    #     json_file.close()

