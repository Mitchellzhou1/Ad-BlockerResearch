from base_code import *
# Get browser logs

shared_driver.adBlocker_name = 'uBlock'
shared_driver.initialize()
shared_driver.load_site("https://www.youtube.com/watch?v=KFNrWW9R0_8")

shared_driver.collect_failed_resources()

print("Done")
while 1:
    1
