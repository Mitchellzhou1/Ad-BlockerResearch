from selenium import webdriver

# Launch the browser
driver = webdriver.Chrome()

# Open the webpage
driver.get('https://portswigger.net/web-security/all-labs')

# Define the background image URL you're looking for
url_to_find = "/content/images/logos/portswigger-logo.svg"

# Define a JavaScript function to find elements with a specific background image URL
js_script = f"""
function findElementWithBackgroundImage(selector, imageUrl) {{
    var elements = document.querySelectorAll(selector);
    for (var i = 0; i < elements.length; i++) {{
        var style = window.getComputedStyle(elements[i]);
        var backgroundImage = style.getPropertyValue('background-image');
        if (backgroundImage.includes(imageUrl)) {{
            return elements[i];
        }}
    }}
    return null;
}}

return findElementWithBackgroundImage('.logo', '{url_to_find}');
"""

# Execute the JavaScript function and get the element
logo_element = driver.execute_script(js_script)

# Print the outerHTML of the found element
if logo_element:
    print("Found Logo Element:")
    print(logo_element.get_attribute("outerHTML"))
else:
    print("Logo Element not found")

# Close the browser
driver.quit()
