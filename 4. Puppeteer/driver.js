const puppeteer = require('puppeteer');
const { JSDOM } = require('jsdom');

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

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


function getCSSselector(outerHTML) {
    const dom = new JSDOM();
    const document = dom.window.document;
  
    // Create a temporary element to parse the outerHTML
    const tempElement = document.createElement('div');
    tempElement.innerHTML = outerHTML.trim();
    const element = tempElement.firstChild;
  
    // Get the tag name
    let selector = element.tagName.toLowerCase();
  
    // Get the class names
    if (element.classList.length > 0) {
      selector += '.' + Array.from(element.classList).join('.');
    }
  
    // Get other attributes
    Array.from(element.attributes).forEach(attr => {
      if (attr.name !== 'class') {
        selector += `[${attr.name}="${attr.value}"]`;
      }
    });
  
    return selector;
  }


function removeLongestElement(arr) {
// Check for empty array and return early
if (!arr || arr.length < 3) {
    return arr; // Return the original empty array
}

// Find the index of the longest element (starting from index 0)
let longestIndex = 1;
let maxLength = arr[1].length;
for (let i = 2; i < arr.length; i++) {
    if (arr[i].length > maxLength) {
    maxLength = arr[i].length;
    longestIndex = i;
    }
}

// Remove the element at the longest index using splice
arr.splice(longestIndex, 1);

return arr;
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
  
    try {
      const { browser, page } = await initialize(url);
      const uniqueOuterHTML = await findAllButtons(browser, page);
        
      // Loop through uniqueOuterHTML with async/await
      for (const html of uniqueOuterHTML) {

        selector = await getCSSselector(html);
        for (let i = 0; i < 2; i++){
        
            try {
                await page.waitForSelector(selector);
                await page.click(selector);
                //record results
                await sleep(2000);
                console.log("It worked");

                await page.goto(url);
                break;
            }
            catch (error) {
                const selectorArray = selector.split('[');
                removeLongestElement(selectorArray);
                selector = selectorArray.join('[');
            }

    
    
    
        };
      };
    
  
      // Close the browser when done
      await browser.close();
  
    } catch (error) {
      console.error('Error:', error);
    }

  })();
  
