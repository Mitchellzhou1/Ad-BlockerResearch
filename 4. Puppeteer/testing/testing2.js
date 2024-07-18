const puppeteer = require('puppeteer');


function parseOuterHTMLAttributes(outerHTML) {
    const tagRegex = /^<(\w+)\s+/; // Regex to match the tag name
    const attributeRegex = /(\w+)\s*=\s*["']([^"']*)["']/g; // Regex to match attributes and their values
    const attributes = {}; // Dictionary to store attribute key-value pairs

    // Extract tag name
    const tagMatch = outerHTML.match(tagRegex);
    if (tagMatch) {
        attributes['tag'] = tagMatch[1].trim(); // Store the tag name (trimmed)
    }

    // Extract attributes
    let match;
    while ((match = attributeRegex.exec(outerHTML)) !== null) {
        const attributeName = match[1].trim(); // Attribute name (trimmed)
        const attributeValue = match[2].trim(); // Attribute value (trimmed)
        attributes[attributeName] = attributeValue;
    }

    return attributes;
}

function compareAttributeObjects(obj1, obj2) {
    // Check if both objects are defined and have the same number of keys
    if (!obj1 || !obj2 || Object.keys(obj1).length !== Object.keys(obj2).length) {
        return false;
    }
    // Iterate through keys of obj1 and compare values with obj2
    for (let key in obj1) {
        if (!(key in obj2) || obj1[key] !== obj2[key]) {
            return false;
        }
    }
    // Iterate through keys of obj2 to check for any extra keys not in obj1 (though they should be same length)
    for (let key in obj2) {
        if (!(key in obj1)) {
            return false;
        }
    }
    return true;
}

(async () => {
    // Launch Puppeteer with headless:false and defaultViewport set to null for full screen
    const browser = await puppeteer.launch({ headless: false, defaultViewport: null });
    
    try {
        const page = await browser.newPage();

        // Navigate to the Wikipedia Main Page
        await page.goto('https://en.wikipedia.org/wiki/Main_Page');

        // Define the target outerHTML you are looking for
        const targetOuterHTML = '<input type="checkbox" id="vector-main-menu-dropdown-checkbox" role="button" aria-haspopup="true" data-event-name="ui.dropdown-vector-main-menu-dropdown" class="vector-dropdown-checkbox" aria-label="Main menu">';
        const targetValues = parseOuterHTMLAttributes(targetOuterHTML);

        // Wait for the element to appear on the page
        await page.waitForSelector('input[type="checkbox"]');

        // Get all input elements of type checkbox on the page
        const checkboxes = await page.$$('input[type="checkbox"]');

        let elementToClick = null;

        // Iterate through each checkbox and compare outerHTML
        for (let checkbox of checkboxes) {
            const outerHTML = await page.evaluate(el => el.outerHTML, checkbox);
            const testValues = parseOuterHTMLAttributes(outerHTML);
            // Compare outerHTML
            if (compareAttributeObjects(targetValues, testValues)){
                elementToClick = checkbox;
                break;
            }

        }

        // If elementToClick is found, click on it
        if (elementToClick) {
            await elementToClick.click();
            console.log('Clicked on the checkbox');
        } else {
            console.log('Checkbox element not found');
        }
    } catch (error) {
        console.error('Error:', error);
    } finally {
        // Close the browser
        await browser.close();
    }
})();
