import puppeteer from 'puppeteer';
import { spawn, exec } from 'child_process';
import fs from 'fs';
import { initializeBlacklists, FilteringContext } from './blacklist_parser/blacklistparser.js';
import { Url } from '../1. HTML Elems (js)/url.mjs';
import { take_ss } from './screenshot.mjs';
import { fileURLToPath } from 'url';
import { dirname, join, resolve } from 'path';



var __filename = fileURLToPath(import.meta.url);
var __dirname = dirname(__filename);

let EXTENSION_NAME = process.argv[2]

var snfe = await initializeBlacklists();

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
      const absolutePath = resolve(__dirname, extensionPath);
      // console.log(absolutePath);
      args.push(`--disable-extensions-except=${absolutePath}`);
      args.push(`--load-extension=${absolutePath}`);
    }

    const browser = await puppeteer.launch({
      headless: true,
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

        if (snfe && (snfe.matchRequest(this.fctxt) !== 0)) {
          responseData.blacklistRule = snfe.toLogData()['raw'];
          this.blacklistedItems.set(requestUrl, responseData); // Checks if the url is blacklisted
        }
        else{
          this.responsesMap.set(requestUrl, responseData);
        }
        
      }
    });

  } catch (error) {
    console.error('Error in script:', error.message);
  }

  return this.page;
};

Driver.prototype.navigateToWebsite = async function(key) {
  try{
    await this.page.goto(this.site);
  } catch{
    // await this.page.screenshot({ path: `sfailed_sites/${key}.png`, fullPage: true });
    process.exit(0);
  }
  

  await this.page.evaluate(async () => {
    const scrollToBottomSlowly = async (timeout = 10000) => {
      const distance = 200;
      const startTime = Date.now();
  
      while (Date.now() - startTime < timeout) {
        const { scrollTop, scrollHeight, clientHeight } = document.documentElement;
        
        if (scrollTop + clientHeight >= scrollHeight) {
          break;
        }
  
        window.scrollBy(0, distance);
        await new Promise(resolve => setTimeout(resolve, 500));
      }
    };
  
    await scrollToBottomSlowly(10000); 
  });

  let allPages = await this.browser.pages();
  if (allPages.length > 1) {
    for (let i = 1; i < allPages.length; i++) {
      await allPages[i].close();
    }
  }

  await sleep(1.5);
  this.source = await this.page.content();
};

Driver.prototype.store_blacklist = async function(website) {
  let finalData = Object.fromEntries(this.blacklistedItems);
  finalData = {[website]: finalData};
  
  const filePath = join(`./Results/blacklist/blacklist.json`);

  if (fs.existsSync(filePath)) {
      const existingData = fs.readFileSync(filePath, 'utf8');
      if (existingData) {
        // If file exists, parse the existing data and combine it with new data
        const existingJson = JSON.parse(existingData);
        finalData = { ...existingJson, ...finalData };
      } 
  }

  finalData = JSON.stringify(finalData, null, 2);

  // Write the combined data back to the file
  fs.writeFileSync(filePath, finalData, 'utf8', (err) => {
    if (err) {
      console.error('Error writing file:', err);
      return;
    }
    console.log('Data has been written to', filePath);
  });
};

Driver.prototype.find_missing_resources = async function(control_rr, extn_rr){

  const missing = Object.keys(control_rr)
    .filter(key => !(key in extn_rr))
    .map(key => {
      const contentType = control_rr[key] ? control_rr[key].contentType : undefined;
      let type = '';
      if (contentType.includes('image')) {
        type = 'images';
      } else if (contentType.includes('video')) {
        type = 'videos';
      }
      return {
        url: key,
        type: type
      };
    });
  return missing;
};

Driver.prototype.click_on_videos = async function(){
  const browser = this.browser;
  const page = this.page
  
  // Listen for new pages (tabs) being created
  browser.on('targetcreated', async (target) => {
    const newPage = await target.page();
    if (newPage) {
      await newPage.close();
    }
  });
  
  // Get all video elements
  const videoElements = await page.$$('video');


  for (const video of videoElements) {
    try {
      await page.evaluate(video => {
          const anchor = video.closest("a"); 
          if (anchor) {
              anchor.setAttribute("target", "_blank");
          }
      }, video);
      await video.click();
      await sleep(4); // Small delay between clicks
    }
      catch (error) {

        console.error(`Error interacting with video: ${error.message}`);
    }
  }
};

Driver.prototype.control_ss = async function(path){

  const filePath = `${path}/control.png`;

  if (!fs.existsSync(path)){
        fs.mkdirSync(path, { recursive: true });
        console.log(`Folder created successfully!: ${path}`);    
    }
        

  try {
    // Check if the file exists
    fs.access(filePath);
    return;
  } catch (error) {
    await this.page.screenshot({
      path: filePath,
      fullPage: true,
    });
  }
};

function write_results(data, adblocker, key) {
  let finalData = {[adblocker]: data};
  const filePath = join(`./screenshots/${key}/ad_resources.json`);

  if (fs.existsSync(filePath)) {
      const existingData = fs.readFileSync(filePath, 'utf8');
      if (existingData) {
        // If file exists, parse the existing data and combine it with new data
        const existingJson = JSON.parse(existingData);
        finalData = { ...existingJson, ...finalData };
      } 
  }
  
  finalData = JSON.stringify(finalData, null, 2);

  // Write the combined data back to the file
  fs.writeFileSync(filePath, finalData, 'utf8', (err) => {
    if (err) {
      console.error('Error writing file:', err);
      return;
    }
    console.log('Data has been written to', filePath);
  });
};


Driver.prototype.control_filter = async function(key, extn_lst, control_resources) {
  /**
   * Waits until all keys in extn_lst are present in the JSON file at ./screenshots/${key}/missing.json.
   *
   * @param {string} key - The key used to construct the file path.
   * @param {string[]} extn_lst - A list of keys that must be present in the JSON file.
   * @param {number} check_interval - The time interval (in milliseconds) between checks. Default is 1000ms (1 second).
   */
  const filepath = `./screenshots/${key}/ad_resources.json`;
  const sleep_interval = 5;

  if (typeof extn_lst === 'string') {
    extn_lst = extn_lst.split(','); // Split the string by commas
  }
  extn_lst = extn_lst.filter(item => item !== 'control');

  const max_wait_time = 5 * 60 * 1000;
  const start_time = Date.now();
  
  while (Date.now() - start_time < max_wait_time) {
      try {
          // Check if the file exists
          if (!fs.existsSync(filepath)) {
              // console.log(`File ${filepath} does not exist yet. Waiting...`);
              await sleep(sleep_interval);
              continue;
          }
  
          // Read the file
          var data = JSON.parse(fs.readFileSync(filepath, 'utf8'));
  
          // Check if all keys in extn_lst are present in the JSON data
          if (extn_lst.every(key => data.hasOwnProperty(key))) {
              console.log("All required keys are present. Proceeding...");
              break;
          }
      } catch (error) {
          // Handle errors (e.g., empty file, invalid JSON, or file being written to)
          console.log(`An error occurred: ${error.message}. Waiting...`);
          await sleep(sleep_interval);
          console.log("running again");
      }
  }

  const ret = [];
  const final_subset = findSubset(JSON.parse(control_resources), Object.fromEntries(this.responsesMap));
  for(const extn of extn_lst){
    var extn_resources = data[extn];
    var extn_missing = await this.find_missing_resources(final_subset, extn_resources);
    await take_ss(extn_missing, extn, this.page, key);

  }  

};


function findSubset(obj1, obj2) {
  let subset = {};
  
  for (let key in obj1) {
      if (obj2.hasOwnProperty(key)) {
          subset[key] = obj1[key];
      }
  }
  
  return subset;
}



(async (adblocker, website, key, extn_lst, control_resources)  => {

  const driver = new Driver(adblocker, website);    //extensions are not working?
  const path  = 'screenshots' + '/' + key;

  await driver.initialize();
  await driver.navigateToWebsite(key)

  await driver.click_on_videos();

  const responsesObject = Object.fromEntries(driver.responsesMap);
  
  if (control_resources!=='false'){ //we are in second round
    // write_results(website, responsesObject)
    if (adblocker == 'control'){
      await driver.control_filter(key, extn_lst, control_resources);

    }
    else{
      const file_path = path + '/' + adblocker
      if (!fs.existsSync(file_path)){
          fs.mkdirSync(file_path, { recursive: true });
      }
      write_results(responsesObject, adblocker, key)
      console.log(`Done writting results\n${file_path}\n`);
      try{
        await driver.page.screenshot({
          path: `${file_path}/entire_page.png`, 
          fullPage: true,
        });
        console.log(`Done Screenshots ${file_path} results\n\n`);
      } catch{
        // console.log("Delete Director call was made")
      }
    }
  }
  else{
    const jsonData = JSON.stringify(responsesObject, null, 2);
    process.send(jsonData);
    await driver.control_ss(path);  // take SS of the control
  }
  

  // await driver.store_blacklist(key);

  driver.browser.close();
  
  process.exit(0);

})(process.argv[2], process.argv[3], process.argv[4], process.argv[5], process.argv[6]);
