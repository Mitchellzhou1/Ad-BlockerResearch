const puppeteer = require('puppeteer');
const path = require('path');

(async () => {
  // Define the extension name
  const EXTENSION_NAME = 'adblock'; // Change this to the name of your extension folder

  // Set the path to the extension
  const extensionPath = `../Extensions/puppeteer_extn/${EXTENSION_NAME}`;
  const absolutePath = path.resolve(__dirname, extensionPath);
  console.log(absolutePath);

  // Launch browser with the extension
  const browser = await puppeteer.launch({
    headless: false, // Extensions only work in non-headless mode
    args: [
      `--disable-extensions-except=${absolutePath}`, // Load only this extension
      `--load-extension=${absolutePath}` // Load the extension
    ]
  });

  // Create a new page
  const page = await browser.newPage();

  // Navigate to a page (e.g., Google)
  await page.goto('https://www.google.com');

  // Close the browser when done
  // await browser.close();
})();
