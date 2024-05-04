import multiprocessing
import sys
import time

from selenium import webdriver

class testing:
    def __init__(self):
        self.driver = None
        self.testing = False

    def initialize(self):
        self.driver = webdriver.Chrome()
        self.driver.get("https://brightspace.nyu.edu/d2l/le/lessons/315188/units/9142859")
        self.testing = True
        return "Done"


def run(obj):
    ret = obj.initialize()
    print(ret)
    print(obj.testing)


dict = {}
for i in range(3):
    dict[i] = testing()


process_list = []
for i in range(3):
    process_list.append(multiprocessing.Process(target=run, args=(dict[i],)))
    process_list[i].start()
for i in range(3):
    process_list[i].join()


print("DONE")
