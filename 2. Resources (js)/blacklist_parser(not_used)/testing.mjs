import puppeteer from "puppeteer";

const requests = [];
const responses = [];

async function sleep(ms) {
    const seconds = ms * 1000;
    return new Promise(resolve => setTimeout(resolve, seconds));
  }

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
    requests.push(request.url());
  });

  // Capture response details
  page.on('response', async response => {
    responses.push(response.url());
  });

  return { browser, page };
}

async function navigateToWebsite(page, url) {
  await page.goto(url);

  await sleep(5);
  // Wait for a specific element or a certain amount of time if needed
  // For example, wait for the page to fully load
}

(async () => {
  const { browser, page } = await setupPuppeteer();

  await navigateToWebsite(page, 'https://www.microsoft.com/store/cart?rtc=1');
  // await navigateToWebsite(page, 'https://en.wikipedia.org/wiki/Main_Page');

  console.log('All Requests:', requests.length);
  console.log('All Responses:', responses.length);

  console.log(responses);


    // Elements in array1 but not in array2
    const uniqueToArr1 = requests.filter(element => !responses.includes(element));

    // Elements in array2 but not in array1
    const uniqueToArr2 = responses.filter(element => !requests.includes(element));

    console.log('Unique to array1:', uniqueToArr1); // Output: [1, 2, 3]
    console.log('Unique to array2:', uniqueToArr2); // Output: [6, 7, 8]

})();