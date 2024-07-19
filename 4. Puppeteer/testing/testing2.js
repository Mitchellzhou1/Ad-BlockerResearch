const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({ headless: false });
  const page = await browser.newPage();

  // Navigate to the target page
  await page.goto('https://duckduckgo.com/'); // Update with your URL
  console.log('Navigated to the page');

  // Wait for the form element to be available
  await page.waitForSelector('form');
  console.log('Form element is available');

  // Handle text inputs individually
  const textInputs = await page.evaluate(() => {
    const elements = document.querySelectorAll('input[type="text"]');
    console.log('Text Inputs found:', elements.length);
    return Array.from(elements).map(element => element.outerHTML); // Return HTML strings for easier debugging
  });

  // Handle search inputs individually
  const searchInputs = await page.evaluate(() => {
    const elements = document.querySelectorAll('input[type="search"]');
    console.log('Search Inputs found:', elements.length);
    return Array.from(elements).map(element => element.outerHTML); // Return HTML strings for easier debugging
  });

  // Handle password inputs individually
  const passwordInputs = await page.evaluate(() => {
    const elements = document.querySelectorAll('input[type="password"]');
    console.log('Password Inputs found:', elements.length);
    return Array.from(elements).map(element => element.outerHTML); // Return HTML strings for easier debugging
  });

  // Handle textareas individually
  const textareas = await page.evaluate(() => {
    const elements = document.querySelectorAll('textarea');
    console.log('Textareas found:', elements.length);
    return Array.from(elements).map(element => element.outerHTML); // Return HTML strings for easier debugging
  });

  // Handle email inputs individually
  const emailInputs = await page.evaluate(() => {
    const elements = document.querySelectorAll('input[type="email"]');
    console.log('Email Inputs found:', elements.length);
    return Array.from(elements).map(element => element.outerHTML); // Return HTML strings for easier debugging
  });

  // Handle number inputs individually
  const numberInputs = await page.evaluate(() => {
    const elements = document.querySelectorAll('input[type="tel"]');
    console.log('Number Inputs found:', elements.length);
    return Array.from(elements).map(element => element.outerHTML); // Return HTML strings for easier debugging
  });

  // Log the results outside of page.evaluate
  console.log('Text Inputs:', textInputs);
  console.log('Search Inputs:', searchInputs);
  console.log('Password Inputs:', passwordInputs);
  console.log('Textareas:', textareas);
  console.log('Email Inputs:', emailInputs);
  console.log('Number Inputs:', numberInputs);

  // Optionally, set values for the inputs if found
  await page.evaluate(() => {
    document.querySelectorAll('input[type="text"]').forEach(input => input.value = 'SampleText');
    document.querySelectorAll('input[type="search"]').forEach(input => input.value = 'SampleSearch');
    document.querySelectorAll('input[type="password"]').forEach(input => input.value = 'SamplePassword');
    document.querySelectorAll('textarea').forEach(textarea => textarea.value = 'SampleTextarea');
    document.querySelectorAll('input[type="email"]').forEach(input => input.value = 'sample@example.com');
    document.querySelectorAll('input[type="tel"]').forEach(input => input.value = '1234567890');
  });

  // Optionally, submit the form
  await page.click('button[type="submit"]'); // Adjust the selector as needed
  await page.waitForNavigation();

  await browser.close();
})();
