const puppeteer = require('puppeteer');

(async () => {
  // Launch the browser
  const browser = await puppeteer.launch({ headless: false }); // Set headless: false to see the browser window
  const page = await browser.newPage();

  // Go to Google
  await page.goto('https://www.google.com', { waitUntil: 'networkidle2' });

  // Click the voice search button
  const voiceSearchSelector = "div.XDyW0e[jscontroller=\"unV4T\"][jsname=\"F7uqIe\"][aria-label=\"Search by voice\"][role=\"button\"][tabindex=\"0\"][jsaction=\"h5M12e;rcuQ6b:npT2md\"][data-ved=\"0ahUKEwjAhPbu1f6GAxUDEFkFHRugAwoQvs8DCAg\"]";
  await page.waitForSelector(voiceSearchSelector);
  await page.click(voiceSearchSelector);

  // Wait for any potential page changes (optional)
  // await page.waitForNavigation({ waitUntil: 'networkidle2' });

  // Close the browser
  await browser.close();
})();

