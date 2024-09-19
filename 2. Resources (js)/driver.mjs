import puppeteer from 'puppeteer';
import { spawn, exec } from 'child_process';
import fs from 'fs';
// import './blacklist.mjs';
// import { initialize_blacklist } from './blacklist.mjs';

let EXTENSION_NAME = 'control'





async function sleep(ms) {
  const seconds = ms * 1000;
  return new Promise(resolve => setTimeout(resolve, seconds));
}

function run_cmd(cmd) {
  return new Promise((resolve, reject) => {
    const full_cmd = ['wrapper.py'].concat(cmd);
    const pythonProcess = spawn('python3', full_cmd);

    let result = '';

    pythonProcess.stdout.on('data', (data) => {
        result += data.toString(); // Accumulate output data
    });

    pythonProcess.stderr.on('data', (data) => {
        console.error(`Stderr: ${data}`);
    });

    pythonProcess.on('error', (error) => {
        reject(`Error: ${error.message}`);
    });

    pythonProcess.on('close', (code) => {
        console.log(`Process exited with code ${code}`);
        if (code === 0) {
            resolve(result); // Resolve with the accumulated result
        } else {
            reject(`Process exited with code ${code}`);
        }
    });
  });
}


class Driver{
  constructor(adB, website){
    this.page;
    this.browser;

    this.extn = adB;
    this.site = website;


    this.requests = new Set();
    this.responses = new Set();
    this.requestsMap = new Map();
    this.responsesMap = new Map();
    
    this.source;
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

    page.on('request', (request) => {
      const requestData = {
        url: request.url(),
        method: request.method(),
        headers: request.headers()
      };
      const requestUrl = request.url();
      const referer = request.headers()['referer'] || 'N/A';  // Capture referrer from the request headers
      this.requestsMap.set(requestUrl, referer);  // Store request URL and its referrer in the map
      this.requests.add(requestData);
    });


    // Capture response details

    page.on('response', async response => {
      const requestUrl = response.url();  // Get the response URL
      const referer = this.requestsMap.get(requestUrl)   // Find the associated referer from the request map
      const contentType = response.headers()['content-type'] || 'N/A';  // Get the content type


      if (contentType.includes('image') || contentType.includes('video') && this.source.includes(requestUrl)) {
        const responseData = {
          responseCode: response.status(),
          statusText: response.statusText() || 'N/A',
          contentLength: response.headers()['content-length'] || 'N/A',
          contentType: response.headers()['content-type'] || 'N/A',
          referrer: referer,
        };
        this.responsesMap.set(response.url(), responseData);
        this.responses.add(responseData);
      }
    });

  } catch (error) {
    console.error('Error in script:', error.message);
  }

  return this.page;
};

Driver.prototype.navigateToWebsite = async function() {
  await this.page.goto(this.site);
  await sleep(5);
  this.source = this.page.content;
};




Driver.prototype.store_results = async function(){

  const myMap = new Map();
  const responsesObject = Object.fromEntries(this.responsesMap);

  myMap.set(this.site, responsesObject);
  const jsonObject = Object.fromEntries(myMap);
  const jsonData = JSON.stringify(jsonObject, null, 2);  // Convert results to a formatted JSON string

  // Write to a file (asynchronously)

  const filepath = `temp/${this.extn}_${this.adB}.json`;
  fs.writeFile(filepath, jsonData, 'utf8', (err) => {
    if (err) {
      console.error('Error writing file:', err);
    } else {
      console.log('Results saved to results.json');
    }
  });
};

(async (adblocker, website)  => {



  const driver = new Driver(adblocker, website);
  await driver.initialize();
  await driver.navigateToWebsite()
  
  await driver.store_results();

  driver.browser.close();

})(process.argv[2], process.argv[3]);
