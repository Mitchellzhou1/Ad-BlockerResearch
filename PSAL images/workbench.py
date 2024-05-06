import multiprocessing
import sys

from selenium.webdriver.chrome import webdriver


class testing:
    def __init__(self):
        self.driver = None
        self.testing = False

    def initialize(self):
        self.driver = webdriver.Chrome()
        self.testing = True



for i in range(3):
