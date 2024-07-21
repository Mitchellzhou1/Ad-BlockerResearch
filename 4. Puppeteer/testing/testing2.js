const puppeteer = require('puppeteer');
const path = require('path');

(async () => {
  // Path to your Chrome extension
  const extensionPath = path.resolve('C:/Users/17579/Desktop/Ad-BlockerResearch/Extensions/puppeteer_extn/privacy-badger');

  const browser = await puppeteer.launch({
    headless: false, // Extensions only work in non-headless mode
    args: [
      `--disable-extensions-except=${extensionPath}`,
      `--load-extension=${extensionPath}`
    ]
  });

  const page = await browser.newPage();
  await page.goto('https://example.com'); // Navigate to a URL

})();
