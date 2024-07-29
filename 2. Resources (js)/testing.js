import puppeteer from "puppeteer";

const requests = [];
const responses = [];

async function setupPuppeteer() {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();

  // Capture request details
  page.on('request', request => {
    const requestData = {
      url: request.url(),
      method: request.method(),
      headers: request.headers()
    };
    requests.push(requestData);
  });

  // Capture response details
  page.on('response', async response => {
    try {
      const responseBody = await response.buffer();
      const responseData = {
        url: response.url(),
        status: response.status(),
        headers: response.headers()
      };
      responses.push(responseData);
    } catch (error) {
      console.error('Error handling response:', error.message);
    }
  });

  return { browser, page };
}

async function navigateToWebsite(page, url) {
  await page.goto(url);

  // Wait for a specific element or a certain amount of time if needed
  // For example, wait for the page to fully load
}

(async () => {
  const { browser, page } = await setupPuppeteer();

  await navigateToWebsite(page, 'https://www.uxmatters.com/');

//   // Close the browser
//   await browser.close();

  // Access the captured requests and responses
  console.log('All Requests:', requests);
  console.log('All Responses:', responses);
})();
