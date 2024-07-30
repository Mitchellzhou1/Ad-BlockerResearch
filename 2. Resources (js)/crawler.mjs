import puppeteer from 'puppeteer';
import { spawn, exec } from 'child_process';
import path from 'path';


async function sleep(ms) {
  const seconds = ms * 1000;
  return new Promise(resolve => setTimeout(resolve, seconds));
}

class Driver{
  constructor(adB){
    this.page;
    this.browser;
    this.server;

    this.extn = adB;
    this.values = {};

    this.requests = new Set();
    this.responses = new Set();
  }

}

Driver.prototype.initialize = async function() {
  try {
    let args = ['--start-maximized'];
    if (EXTENSION_NAME !== 'control') {
      const extensionPath = `../../Extensions/puppeteer_extn/${EXTENSION_NAME}`;
      const absolutePath = resolve(__path, extensionPath);
      args.push(`--disable-extensions-except=${absolutePath}`);
      args.push(`--load-extension=${absolutePath}`);
    }

    const browser = await puppeteer.launch({
      headless: false,
      args: args,
      ignoreHTTPSErrors: true // Ignore HTTPS errors
    });

    if (EXTENSION_NAME !== 'control') 
      await sleep(10);
    const pages = await browser.pages();
    for (let i = 1; i < pages.length; i++) {
      const title = await pages[i].title();
      console.log(`Closing page: ${title}`);
      await pages[i].close();
    }
    const page = pages[0];
  
    const { width, height } = await page.evaluate(() => {
      return {
        width: window.outerWidth,
        height: window.outerHeight
      };
    });
  
    await page.setViewport({ width, height });  
    this.page = page;
    this.browser = browser;


    // Capture request details
    page.on('request', request => {
    const requestData = {
      url: request.url(),
      method: request.method(),
      headers: request.headers()
    };
    this.requests.add(requestData);
    });

    // Capture response details
    page.on('response', async response => {
    const responseData = {
      url: response.url(),
      responseCode: response.status(),
      referer: response.referer(),
      statusText: response.statusText() || 'N/A',
      contentLength: response.headers.get('Content-Length') || 'N/A',
      contentType: response.headers.get('Content-Type') || 'N/A',
      referrer: response.headers.get('Referrer') || 'N/A',
    };
    this.responses.add(responseData);

    });

    this.start_server();

  } catch (error) {
    console.error('Error in script:', error.message);
  }

};

Driver.prototype.navigateToWebsite = async function(page, url) {
  await page.goto(url);

  await sleep(5);

}


(async () => {
  const driver = new Driver();




})();
