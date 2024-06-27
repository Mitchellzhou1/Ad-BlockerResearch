const puppeteer = require('puppeteer');

async function initialize(url) {
  const browser = await puppeteer.launch({
    headless: false,
    args: ['--start-maximized']
  });

  const pages = await browser.pages();
  const page = pages[0];

  const { width, height } = await page.evaluate(() => {
    return {
      width: window.outerWidth,
      height: window.outerHeight
    };
  });

  await page.setViewport({ width, height });
  await page.goto(url);

  return { browser, page }; // Return both browser and page objects
}

async function findAllButtons(browser, page) {
    await page.waitForSelector('button');  
    const uniqueOuterHTML = await page.evaluate(() => {
      const buttonElements = document.querySelectorAll('button');
      const uniqueSet = new Set(); // Create the Set before the loop
  
      buttonElements.forEach(button => {
        uniqueSet.add(button.outerHTML);
      });
        
      return Array.from(uniqueSet);
    });
    
    return uniqueOuterHTML;
  }

(async () => {
  const url = 'https://en.wikipedia.org/wiki/Main_Page';
  const { browser, page } = await initialize(url);
  const uniqueOuterHTML = await findAllButtons(browser, page); 

  console.log(uniqueOuterHTML);

//   setTimeout(async () => {
//     await browser.close();
//   }, 10000); 
})();
