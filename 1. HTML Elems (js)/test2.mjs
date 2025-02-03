import puppeteer from 'puppeteer';

(async () => {
    // Launch a headless browser
    const browser = await puppeteer.launch();
    const page = await browser.newPage();

    // Navigate to the website
    const websiteUrl = 'https://www.uxmatters.com/'; // Replace with the URL of the website you want to capture
    await page.goto(websiteUrl, { waitUntil: 'networkidle2' }); // Wait until the page is fully loaded

    // Take a screenshot of the entire page
    await page.screenshot({
        path: 'screenshot.png', // Save the screenshot as a file
        fullPage: true, // Capture the entire page, not just the viewport
    });

    console.log('Screenshot saved as screenshot.png');

    // Close the browser
    await browser.close();
})();