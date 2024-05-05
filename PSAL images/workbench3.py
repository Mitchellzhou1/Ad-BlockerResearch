from selenium import webdriver
import time

# Global dictionary to store browser instances
browser_dict = {}

def initialize_browser():
    options = webdriver.ChromeOptions()
    # Add any options you need
    browser = webdriver.Chrome(options=options)
    session_id = browser.session_id
    browser_dict[session_id] = browser
    return session_id

def get_browser_from_session(session_id):
    return browser_dict.get(session_id)

if __name__ == "__main__":
    # Initialize a browser and keep it running in the background
    session_id = initialize_browser()

    # Wait for a while to simulate keeping the browser alive
    time.sleep(3)

    # Retrieve the browser using the session ID
    retrieved_browser = get_browser_from_session(session_id)
    if retrieved_browser:
        retrieved_browser.get("https://www.example.com")
        # Perform actions with the retrieved browser as needed
        # Don't forget to close the retrieved browser when done
        time.sleep(19)
        retrieved_browser.quit()
    else:
        print("Browser session not found.")
