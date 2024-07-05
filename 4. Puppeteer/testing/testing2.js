const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  
  // Replace with the URL of the website you want to visit
  await page.goto('https://www.programiz.com/python-programming/online-compiler/');

  // Extract the relevant elements
  const elements = await page.evaluate(() => {
    const results = [];
    
    // Select elements with the specified attributes
    const buttons = document.querySelectorAll('[role="button"], [role="submit"], [role="#"], [type="button"], [type="submit"]');
    buttons.forEach(button => {
      results.push({
        tagName: button.tagName,
        role: button.getAttribute('role'),
        type: button.getAttribute('type'),
        id: button.id,
        outerHTML: button.outerHTML
      });
    });
    
    return results;
  });

  console.log(elements);

  await browser.close();
})();
