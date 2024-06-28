const { JSDOM } = require('jsdom');

function outerHTMLToSelector(outerHTML) {
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
    if (!arr || !arr.length) {
      return arr; // Return the original empty array
    }
  
    // Find the index of the longest element (starting from index 0)
    let longestIndex = 0;
    let maxLength = arr[0].length;
    for (let i = 1; i < arr.length; i++) {
      if (arr[i].length > maxLength) {
        maxLength = arr[i].length;
        longestIndex = i;
      }
    }
  
    // Remove the element at the longest index using splice
    arr.splice(longestIndex, 1);
  
    return arr;
  }

const puppeteer = require('puppeteer');

(async () => {
    // Launch the browser
    const browser = await puppeteer.launch({ headless: false }); // Set headless: false to see the browser window
    const page = await browser.newPage();
  
    // Go to Google
    await page.goto('https://www.google.com', { waitUntil: 'networkidle2' });
  
    const entire = '<div jscontroller="unV4T" jsname="F7uqIe" class="XDyW0e" aria-label="Search by voice" role="button" tabindex="0" jsaction="h5M12e;rcuQ6b:npT2md" data-ved="0ahUKEwjAhPbu1f6GAxUDEFkFHRugAwoQvs8DCAg"><svg class="goxjub" focusable="false" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path fill="#4285f4" d="m12 15c1.66 0 3-1.31 3-2.97v-7.02c0-1.66-1.34-3.01-3-3.01s-3 1.34-3 3.01v7.02c0 1.66 1.34 2.97 3 2.97z"></path><path fill="#34a853" d="m11 18.08h2v3.92h-2z"></path><path fill="#fbbc04" d="m7.05 16.87c-1.27-1.33-2.05-2.83-2.05-4.87h2c0 1.45 0.56 2.42 1.47 3.38v0.32l-1.15 1.18z"></path><path fill="#ea4335" d="m12 16.93a4.97 5.25 0 0 1 -3.54 -1.55l-1.41 1.49c1.26 1.34 3.02 2.13 4.95 2.13 3.87 0 6.99-2.92 6.99-7h-1.99c0 2.92-2.24 4.93-5 4.93z"></path></svg></div>'
    
    // const voiceSearchSelector = 'div[jsaction="h5M12e;rcuQ6b:npT2md"]'; // Using jsaction attribute for uniqueness
    voiceSearchSelector = outerHTMLToSelector(entire);
    for (let i = 0; i < 3; i++){
        
        try {
            await page.waitForSelector(voiceSearchSelector);
            await page.click(voiceSearchSelector);
            break;
        }
        catch (error) {
            const selectorArray = voiceSearchSelector.split('[');
            removeLongestElement(selectorArray);
            voiceSearchSelector = selectorArray.join('[');
        }



    };
  
    // Wait for any potential page changes (optional)
    // await page.waitForNavigation({ waitUntil: 'networkidle2' });
  
    // Close the browser
    await browser.close();
  })();
