from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By


def perform_click_actions(url):

    # Create a new instance of the webdriver
    driver = webdriver.Chrome()  # Use Chrome, or choose another browser

    # Navigate to the specified URL
    driver.get(url)

    window_width = driver.execute_script("return window.innerWidth;")
    window_height = driver.execute_script("return window.innerHeight;")

    x_coordinate_left = 0
    y_coordinate = window_height

    x_coordinate_right = window_width

    action = ActionChains(driver)

    user_input = input("Do you want to perform the click actions? (yes/no): ").strip().lower()

    if user_input == "yes":
        action.move_to_element_with_offset(driver.find_element(By.TAG_NAME, 'body'), x_coordinate_left,
                                           y_coordinate).click().perform()



    while 1:
        1


# Example usage
url_to_load = 'https://www.amazon.com/'
perform_click_actions(url_to_load)


