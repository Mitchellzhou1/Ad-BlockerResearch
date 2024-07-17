const puppeteer = require('puppeteer');

(async () => {
    const browser = await puppeteer.launch({
      headless: false,
      args: ['--start-maximized'] // This argument starts the browser maximized
    });
    const page = await browser.newPage();
    await page.setViewport({ width: 1920, height: 1080 }); // Set the viewport size to match a maximized window

    await page.goto('https://en.wikipedia.org/wiki/Main_Page');

    // The outerHTML of the target button
    const targetOuterHTML = `<input type=\"checkbox\" id=\"vector-main-menu-dropdown-checkbox\" role=\"button\" aria-haspopup=\"true\" data-event-name=\"ui.dropdown-vector-main-menu-dropdown\" class=\"vector-dropdown-checkbox \" aria-label=\"Main menu\">"`; // Replace with the actual outerHTML

    // Function to extract the tag name from outerHTML
    function getTagName(outerHTML) {
        const match = outerHTML.trim().match(/^<([a-zA-Z0-9-]+)/);
        return match ? match[1] : null;
    }

    // Extract the tag name from the target outerHTML
    const tagName = getTagName(targetOuterHTML);
    if (!tagName) {
        console.log("Invalid outerHTML: Unable to extract tag name");
        await browser.close();
        return;
    }

    // Find and click the element with the matching outerHTML
    const clicked = await page.evaluate((targetOuterHTML, tagName) => {
        const elements = document.querySelectorAll(tagName);
        for (let element of elements) {
            if (element.outerHTML.trim() === targetOuterHTML.trim()) {
                element.click();
                return true;
            }
        }
        return false;
    }, targetOuterHTML, tagName);

    if (clicked) {
        console.log("Button clicked successfully");
    } else {
        console.log("Button not found");
    }

    // Optional: Perform additional actions or wait for navigation
    await page.waitForNavigation();

    await browser.close();
})();
