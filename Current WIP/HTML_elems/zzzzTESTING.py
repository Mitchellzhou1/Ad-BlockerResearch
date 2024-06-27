from base_code import *

shared_driver = Driver()

shared_driver.initialize()
shared_driver.load_site("https://www.hidraulicart.pt/")

try:
    # Execute JavaScript to get the CSS content of the webpage
    css_content = shared_driver.driver.execute_script("return document.querySelector('style').innerText")

    if css_content:
        print("CSS content:")
        print(css_content)

except Exception as e:
    print(f"Error: {e}")

finally:
    shared_driver.driver.quit()  # Close the WebDriver after finishing




while 1:
    1