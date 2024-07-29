import puppeteer from 'puppeteer';
import { spawn, exec } from 'child_process';
import path from 'path';
import { startupSnapshot } from 'v8';


class Driver{
  constructor(adB){
    this.page;
    this.browser;
    this.server;

    this.proxyPort = 8081; // Ensure this matches your BrowserMob Proxy port
    this.proxyUrl = `http://localhost:${this.proxyPort}`;

    this.extn = adB;
    this.values = {};
  }

}


Driver.prototype.start_server = async function() {
  try {
    const command = path.resolve('/home/character/Desktop/Ad-BlockerResearch/browsermob-proxy/bin/browsermob-proxy');
    const args = ['--port', '8080'];
  
    this.server = spawn(command, args, {
      stdio: 'ignore'  // This will hide stdout and stderr
    });
  
    this.server.on('error', (err) => {
      console.error(`Failed to start server: ${err}`);
    });
  
    console.log(`Server started with PID: ${this.server.pid}`);
  } catch (error) {
    console.error(`Error starting server: ${error.message}`);
  }
};

Driver.prototype.stop_server = async function() {
    exec('pkill -f browsermob');
    console.log("closed proxy");
};

Driver.prototype.initialize = async function() {
  try {
    let args = ['--start-maximized'];
    args.push(`--proxy-server=${proxyUrl}`);
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

    this.page = page;
    this.browser = browser;
    this.start_server();

  } catch (error) {
    console.error('Error in script:', error.message);
  }

}




(async () => {
  const driver = new Driver();
  await driver.start_server();

  setTimeout(() => {
    this.stop_server();
  }, 10000);
})();
