import puppeteer from 'puppeteer';

const proxyPort = 8081; // Ensure this matches your BrowserMob Proxy port
const proxyUrl = `http://localhost:${proxyPort}`;

async function setupPuppeteerWithProxy(proxyUrl) {
  try {
    const browser = await puppeteer.launch({
      headless: false,
      args: [`--proxy-server=${proxyUrl}`],
      ignoreHTTPSErrors: true // Ignore HTTPS errors
    });

    const page = await browser.newPage();

    page.on('request', request => {
      console.log('Request:', request.url(), request.method(), request.headers());
    });

    page.on('response', async response => {
      try {
        const responseBody = await response.buffer();
        console.log('Response:', response.url(), response.status(), response.headers(), responseBody.toString());
      } catch (error) {
        console.error('Error handling response:', error.message);
      }
    });

    await page.goto('https://google.com'); // Test a simple URL
    await page.waitForTimeout(10000); // Adjust the time as needed
    await browser.close();
  } catch (error) {
    console.error('Error in script:', error.message);
  }
}

(async () => {
  try {
    await setupPuppeteerWithProxy(proxyUrl);
  } catch (error) {
    console.error('Error in script:', error.message);
  }
})();
