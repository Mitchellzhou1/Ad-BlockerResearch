const puppeteer = require('puppeteer');

(async () => {
  // Function to sleep for a given amount of milliseconds
  function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  // Launch the browser
  const browser = await puppeteer.launch({ headless: false });
  const page = await browser.newPage();

  try {
    // Navigate to Wikipedia's main page
    await page.goto('https://en.wikipedia.org/wiki/Main_Page');

    // Optional: Sleep to simulate delay or ensure elements are rendered
    await sleep(2000); // Sleep for 2000 ms (2 seconds)

    // Selector for the "Talk" link
    const talkLinkSelector = 'a[title="Discuss improvements to the content page [alt-shift-t]"]';

    // Wait for the "Talk" link to be visible
    await page.waitForSelector(talkLinkSelector, { visible: true, timeout: 10000 });

    // Click the "Talk" link
    await page.click(talkLinkSelector);

    // Optional: Sleep to allow the navigation to complete
    await sleep(2000); // Sleep for 2000 ms (2 seconds)

    // Retrieve the current URL after clicking
    const currentUrl = await page.evaluate(() => window.location.href);
    console.log('Current URL:', currentUrl);

  } catch (error) {
    console.error('Error:', error);
  } finally {
    // Close the browser
    await browser.close();
  }
})();
