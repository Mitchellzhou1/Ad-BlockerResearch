import puppeteer from "puppeteer";

(async () => {
  // Launch the browser in headless mode
  const browser = await puppeteer.launch({ headless: false });
  const page = await browser.newPage();

  // Navigate to the keyboard tester website
  await page.goto('https://keyboardchecker.com/', {
    waitUntil: 'networkidle2', // Wait for the page to fully load
  });

  console.log('Page loaded. Simulating "Escape" key press...');

  // Simulate pressing the "Escape" key
  await page.keyboard.press('Escape');

  await browser.close();
})();