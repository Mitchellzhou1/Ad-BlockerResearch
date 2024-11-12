import puppeteer from 'puppeteer';
import { spawn, exec } from 'child_process';
import fs from 'fs';
import { initializeBlacklists, FilteringContext } from './blacklist_parser/blacklistparser.js';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';


const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);



const snfe = await initializeBlacklists();

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

    this.requestsMap = new Map();
    this.responsesMap = new Map();
    this.fctxt = new FilteringContext();
    this.blacklistedItems = new Map();


    this.source;
    
  }


}

Driver.prototype.initialize = async function() {
  try {
    let args = ['--start-maximized'];
    if (EXTENSION_NAME !== 'control') {
      const extensionPath = `../Extensions/puppeteer_extn/${EXTENSION_NAME}`;
      const absolutePath = resolve(__path, extensionPath);
      // console.log(absolutePath);
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

    // Black list parser
    this.fctxt.setDocOriginFromURL(this.site);

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
    });


    // Capture response details
    
    page.on('response', async response => {
      const requestUrl = response.url();  // Get the response URL
      const referer = this.requestsMap.get(requestUrl)   // Find the associated referer from the request map
      const contentType = response.headers()['content-type'] || 'N/A';  // Get the content type


      if ((contentType.includes('image') || contentType.includes('video'))) {
        const responseData = {
          responseCode: response.status(),
          statusText: response.statusText() || 'N/A',
          contentLength: response.headers()['content-length'] || 'N/A',
          contentType: response.headers()['content-type'] || 'N/A',
          referrer: referer,
        };
        this.fctxt.setURL(requestUrl);
        if (snfe.matchRequest(this.fctxt) !== 0) {
          responseData.blacklistRule = snfe.toLogData()['raw'];
          this.blacklistedItems.set(response.url(), responseData);
        }
        this.responsesMap.set(response.url(), responseData);

      }
    });

  } catch (error) {
    console.error('Error in script:', error.message);
  }

  return this.page;
};

Driver.prototype.navigateToWebsite = async function() {
  await this.page.goto(this.site);
  await this.page.evaluate(async () => {
    const scrollToBottomSlowly = async () => {
      const distance = 200;  // Scroll by 100 pixels each time
      while (document.documentElement.scrollTop + window.innerHeight < document.body.scrollHeight) {
        window.scrollBy(0, distance);  // Scroll down by 'distance'
        await new Promise(resolve => setTimeout(resolve, 500));  // Wait 500ms between each scroll
      }
    };

    await scrollToBottomSlowly();  // Start slow scrolling

    // Optional: Wait for a bit before considering the scroll complete
    await new Promise(resolve => setTimeout(resolve, 2000));
  });
  await sleep(5);
  this.source = await this.page.content();
};

Driver.prototype.store_blacklist = async function(key){
  const blacklist = Object.fromEntries(this.blacklistedItems);
  const blacklistString = JSON.stringify(blacklist, null, 4);  // Adds indentation for readability
  console.log("UPO THE")
  fs.writeFile(`${key}.json`, blacklistString, (err) => {
      if (err) {
          console.error('Error writing file:', err);
      } else {
          console.log('File successfully written!');
      }
  });
};


(async (adblocker, website, key)  => {

  const driver = new Driver(adblocker, website);
  await driver.initialize();
  await driver.navigateToWebsite()
  
  // await driver.store_results(key);
  // console.log(driver.responsesMap);

  const responsesObject = Object.fromEntries(driver.responsesMap);
  const jsonData = JSON.stringify(responsesObject, null, 2);
  process.send(jsonData);

  driver.browser.close();
  await driver.store_blacklist(key);

  process.exit(0);

})(process.argv[2], process.argv[3], process.argv[4]);
