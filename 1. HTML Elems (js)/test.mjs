import puppeteer from 'puppeteer';

const requestsMap = new Map();

async function sleep(ms) {
    const seconds = ms * 1000;
    return new Promise(resolve => setTimeout(resolve, seconds));
}

async function captureVideoTraffic() {
    let args = ['--start-maximized'];
    const browser = await puppeteer.launch({
        headless: false,
        args: args,
        ignoreHTTPSErrors: true 
      }); 

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
  
    // Map requests to their referrers
    await page.setRequestInterception(true);
    page.on('request', request => {
        requestsMap.set(request.url(), request.headers().referer || 'N/A');
        request.continue();
    });

    // Capture responses
    page.on('response', async response => {
        const requestUrl = response.url();
        const referer = requestsMap.get(requestUrl) || 'N/A';
        const contentType = response.headers()['content-type'] || 'N/A';

        if (contentType.includes('video') && contentType=='video/MP2T') {
            console.log(`Video URL: ${requestUrl}`);
            // console.log(`Referer: ${referer}`);
            // console.log(`Content-Type: ${contentType}`);
            console.log('---');
        }
    });

    // Navigate to NBC News
    await page.goto('https://www.nbcnews.com/');

    // Click on all video elements
    const videoElements = await page.$$('video');
    for (const videoElement of videoElements) {
        await videoElement.click();
    }

    // Wait for a few seconds to capture all video traffic
    await browser.close();
    console.log()
}

captureVideoTraffic();