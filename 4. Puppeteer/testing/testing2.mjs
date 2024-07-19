import puppeteer from 'puppeteer';
import fs from 'fs';
import { JSDOM } from 'jsdom';
import { Result } from './result.mjs';
import { Url } from './url.mjs';



async function sleep(ms) {
  const seconds = ms * 1000;
  return new Promise(resolve => setTimeout(resolve, seconds));
}


class Driver{
  constructor(html_elem, adB, replay, data_dict){
    this.adBlocker = adB;
    this.page = null;       // current page
    this.browser = null;     // browser instance
    this.debug = true;
    this.tries = 2;
    this.html_elem = html_elem;

    // used for optimization
    this.keywords = [
        'login', 'my account', 'sign in', 'sign-in', 'signin', 'log in',  // English
        '登录', '我的帐户',  // Chinese (Simplified)
        'вход', 'войти', 'мой аккаунт',  // Russian
        'iniciar sesión', 'mi cuenta'  // Spanish
    ]
    this.website_sleep_time = 3             // longer this value, more consistent the results
    this.DOM_traversal_amt = 3
    this.scan_timeout = 180
    this.elem_timeout = 300

    // used for checking and storing the final results
    this.elem_indx = 0
    this.RESULT = new Result()
    this.URL = new Url()                    // Correct instantiation of Url class
    this.temp_result = ''                   // used to temporarily hold the result
    this.final_result = data_dict
    this.chosen_elms = []                   // used to store the pre-selected elems

    /* RITIK */ 
    this.options = ''
    this.replay = replay
  }

}

Driver.prototype.initialize = async function(url){
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
  this.page = page;
  this.browser = browser;

  this.URL.initialize(url);
  await this.goto(url);
};

Driver.prototype.reinitialize = async function(){
  await this.browser.close();
  await this.initialize(this.URL.full_address);
}

Driver.prototype.goto = async function(url) {
  await this.page.goto(url);
  await this.scroll_to_bottom();
  this.URL.current_url = this.page.url();
  await this.page.screenshot({ path: 'screenshot.png' });
};

Driver.prototype.scroll_to_bottom = async function() {
  // Define a timeout period in milliseconds
  const TIMEOUT_MS = 30000;

  // Define the scrolling operation
  const scrollOperation = this.page.evaluate(async () => {
    await new Promise((resolve) => {
      const distance = 100; // Scroll distance
      const delay = 200;    // Delay between scrolls

      const scrollDown = () => {
        const totalHeight = document.body.scrollHeight;
        const currentPosition = window.scrollY + window.innerHeight;

        window.scrollBy(0, distance);

        if (currentPosition >= totalHeight) {
          resolve();
        } else {
          setTimeout(scrollDown, delay);
        }
      };

      scrollDown();
    });
  });

  // Define the timeout promise
  const timeoutPromise = new Promise((_, reject) => 
    setTimeout(() => reject(new Error('Scroll operation timed out')), TIMEOUT_MS)
  );

  // Race the scrolling operation against the timeout
  try {
    await Promise.race([scrollOperation, timeoutPromise]);
  } catch (error) {
    console.error(error.message);
    // Handle timeout case or perform other actions
    await sleep(3);
    await this.page.evaluate(() => window.scrollTo(0, 0));
    return;
  }

  await sleep(2);
  await this.page.evaluate(() => window.scrollTo(0, 0));
};

Driver.prototype.write_results = async function(){
  const data = {};
  let folder;
  if (this.replay === 0){
    folder = 'replay_0';
    data[this.URL.full_address] = this.chosen_elms;
  }
  else{
    folder = 'replay_1';
    data[this.URL.full_address] = this.results;
  }

  const jsonData = JSON.stringify(data, null, 2);
  const filePath = `./Results/${folder}/${this.html_elem}_${this.adBlocker}.json`;

  fs.writeFile(filePath, jsonData, 'utf8', (err) => {
    if (err) {
      console.error('Error writing file:', err);
      return;
    }
    console.log('Data has been written to', filePath);
  });
};

Driver.prototype.getCSSselector = async function(outerHTML) {
  function escapeSpecialChars(str) {
    return str.replace(/([:.\[\],=@])/g, '\\$1');
    }
  const dom = new JSDOM();
  const document = dom.window.document;

  // Create a temporary element to parse the outerHTML
  const tempElement = document.createElement('div');
  tempElement.innerHTML = outerHTML.trim();
  const element = tempElement.firstChild;

  if (!element) {
  throw new Error('Invalid outerHTML provided.');
  }

  // Start building the selector with the tag name
  let selector = element.tagName.toLowerCase();

  // Get the ID attribute
  if (element.id) {
  selector += `#${escapeSpecialChars(element.id)}`;
  }

  // Get the class names
  if (element.classList.length > 0) {
  selector += '.' + Array.from(element.classList).map(cls => escapeSpecialChars(cls)).join('.');
  }

  // Get other attributes, excluding 'id' and 'class'
  Array.from(element.attributes).forEach(attr => {
  if (attr.name !== 'id' && attr.name !== 'class' && attr.value) {
    selector += `[${escapeSpecialChars(attr.name)}="${escapeSpecialChars(attr.value)}"]`;
  }
  });

  return selector;
};

Driver.prototype.checkCursorStyle = async function(cssSelector) {
  try {
      await this.page.waitForSelector(cssSelector);
      const element = await this.page.$(cssSelector);
      await element.hover();
      // await sleep(1);

      // Evaluate the cursor style
      const cursorStyle = await this.page.evaluate((selector, elem) => {
          const element = document.querySelector(selector);
          return window.getComputedStyle(elem).cursor;
      }, cssSelector, element);
      return cursorStyle;
  } catch (error) {
    return '';
  }
};

Driver.prototype.filter = async function(cssSelector) {
  if (this.html_elem == 'inputs') 
    return true;
  const cursor = await this.checkCursorStyle(cssSelector);
  if (cursor && cursor != 'default') 
    return true;
  return false;
};

/*

  Methods for Replay 0 (finding elements)

*/


Driver.prototype.find_elems = async function() {
  const methodMap = {
    'drop_downs': this.find_dropdowns.bind(this),
    'buttons': this.find_buttons.bind(this),
    'links': this.find_links.bind(this),
    'logins': this.find_logins.bind(this),
    'inputs': this.find_forms.bind(this)
  };
  
  const method = methodMap[this.html_elem];
  
  if (method) {
    var ret = await method();
  } else {
    console.error("You have entered an unsupported HTML type");
  }

  const unique = new Set();
  for (let html of ret){
    const cssSelector = await this.getCSSselector(html)
    const clickable = await this.filter(cssSelector);
    
    if (unique.size >= 15 && this.html_elem == 'links') 
      break;

    if (this.html_elem == 'inputs')
      unique.add(html);
    else if (clickable && !unique.has(cssSelector))
      unique.add(html);
  }

  this.chosen_elms = Array.from(unique);
  console.log('*'.repeat(100));
  await this.write_results();
  console.log(this.URL.full_address);
  console.log(this.chosen_elms);
  console.log('*'.repeat(100));
};

Driver.prototype.specificElementFinder = async function(elems) {
  try{
    const attributesDict = {
      'buttons': {
          'attributes': ['button', 'submit', '#'],
          'values': ['role', 'type']
      },
      'drop_downs': {
          'attributes': ['false', 'true', 'main menu', 'open menu', 'all microsoft menu', 'menu', 'navigation',
                      'primary navigation', 'hamburger', 'settings and quick links', 'dropdown', 'dialog',
                      'js-menu-toggle', 'searchDropdownDescription', 'ctabutton', 'toggle',
                      'legacy-homepage_legacyButton__oUMB9 legacy-homepage_hamburgerButton__VsG7q',
                      'Toggle language selector', 'Open Navigation Drawer', 'guide', 'Expand Your Library',
                      'Collapse Your Library'],
          'values': ['aria-expanded', 'aria-label', 'class', 'aria-haspopup', 'aria-describedby', 'data-testid']
      },
      'links': {
          'attributes': [],
          'values': ['href']
      },
      'inputs': {
          'attributes': ['text'],
          'values': ['type']
      },
      'submit': {
          'attributes': ['submit'],
          'values': ['type']
      }
    };
    const { attributes, values } = attributesDict[this.html_elem];
    const { debug, final } = await this.page.evaluate((attributes, values) => {
      const debug = [];
      const final = [];
      for (const value of values) {
        for (const attr of attributes) {
          const query = `[${value}='${attr}']`;
          const elements = document.querySelectorAll(query);

          elements.forEach(elem => {
            debug.push({
              tagName: elem.tagName,
              foundBy: query,
              outerHTML: elem.outerHTML
            });

            final.push(elem.outerHTML);  // elems is a set
          });
        }
      }
      return {debug, final};
    }, attributes, values);

    // console.log("Printing Debugging");
    // console.log(debug); // For debugging
    return final
  }catch(error){
    console.log("Crashed in specificElementFinder()", error.toString().split('\n')[0]);
    return new Array();
  }
};

Driver.prototype.find_dropdowns = async function(){
  /*
    Dropdowns are defined in this study if having specific HTML attributes
  */
  try{
    const elements_specific = await this.specificElementFinder();
    const final = new Set(elements_specific);
    
    return final;
  }
  catch(error){
    console.log("Crashed in find_dropdowns()", error.toString().split('\n')[0]);
    return new Set();
  }
};

Driver.prototype.find_buttons = async function(){
  /*
    Buttons are defined in this study as any element with 
    <button> tag, <a> tag with no href attribute, or having
    specific HTML attributes
  */
  try{
    await this.page.waitForSelector('button, a');
    const elements_general = await this.page.evaluate(() => {
      const buttonElements = document.querySelectorAll('button');
      const anchorElements = document.querySelectorAll('a');

      const uniqueSet = new Set();
      buttonElements.forEach(button => {
        uniqueSet.add(button.outerHTML);
      });

      anchorElements.forEach(anchor => {
        if (!anchor.hasAttribute('href')) { // Check if the anchor doesn't hvae 'href' attribute
          uniqueSet.add(anchor.outerHTML);
        }
      });

      return Array.from(uniqueSet);
    });

    const elements_specific = await this.specificElementFinder();
    const final = new Set([...elements_specific, ...elements_general]);
    
    return final;
  }catch(error){
    console.log("Crashed in find_buttons()", error.toString().split('\n')[0]);
    return new Set();
  }
};

Driver.prototype.find_links = async function(){
  /*
    Links are defined in this study as <a> tag  with href attribute
  */
  try{
    await this.page.waitForSelector('a');

    const elements_general = await this.page.evaluate((currentURL, fullAddress) => {
      const anchorElements = document.querySelectorAll('a');
      const blacklist = ['#', '/', currentURL, fullAddress];
    
      const uniqueSet = new Set();
      
      anchorElements.forEach(anchor => {
        if (anchor.hasAttribute('href')) {
          const href = anchor.getAttribute('href');
          if (!blacklist.includes(href)) {
            uniqueSet.add(anchor.outerHTML);
          }
        }
      });
    
      return Array.from(uniqueSet);
    }, this.URL.current_url, this.URL.full_address);

    const final = new Set(elements_general);
    
    return final;
  }catch(error){
    console.log("Crashed in find_links()", error.toString().split('\n')[0]);
    return new Set();
  }
};

Driver.prototype.find_logins = async function(){
  /*
    Logins are defined in this study as any element with 
    <button> tag, <a> tag, or HTML elements having specific predefined attributes.
    These elements then go through a filter that checks for keywords such as 
    'login', 'signin', 'my account', etc.
  */
  try{
    const keywords = [
      'login', 'account', 'sign in', 'sign-in', 'signin', 'log in',  // English
      '登录', '我的帐户',  // Chinese (Simplified)
      'вход', 'войти', 'мой аккаунт',  // Russian
      'iniciar sesión', 'mi cuenta'  // Spanish
    ];
    await this.page.waitForSelector('button, a');
    const elements_general = await this.page.evaluate((keywords) => {
      const buttonElements = document.querySelectorAll('button');
      const anchorElements = document.querySelectorAll('a');
    
      const uniqueSet = new Set();
    
      buttonElements.forEach(button => {
        if (keywords.some(keyword => button.outerHTML.toLowerCase().includes(keyword.toLowerCase()))) {
          uniqueSet.add(button.outerHTML);
        }
      });
    
      anchorElements.forEach(anchor => {
        if (anchor.hasAttribute('href') && keywords.some(keyword => anchor.outerHTML.toLowerCase().includes(keyword.toLowerCase()))) {
          uniqueSet.add(anchor.outerHTML);
        }
      });
    
      return Array.from(uniqueSet);
    }, keywords);

 
    return elements_general;
  }catch(error){
    console.log("Crashed in find_logins()", error.toString().split('\n')[0]);
    return new Set();
  }
};

Driver.prototype.find_forms = async function(){
  /*
    Forms are defined in this study as any element that has a <form> tag.
  */
 try{
    await this.page.waitForSelector('form');

    const elements_general = await this.page.evaluate(() => {
      const formElements = document.querySelectorAll('form');
    
      const uniqueSet = new Set();
      
      formElements.forEach(form => {
        uniqueSet.add(form.outerHTML);
        }
      );
    
      return Array.from(uniqueSet);
    });
  
    const final = new Set(elements_general);
    
    return final;
  }
  catch(error){
    console.log("Crashed in find_forms()", error.toString().split('\n')[0]);
    return new Set();
  }
};

/*

  Methods for Replay 1 (interacting with elements)

*/

Driver.prototype.replay_initialize = async function(){

  const filePath = `./Results/replay_0/${this.html_elem}_${this.adBlocker}.json`;
  try {
    if (fs.existsSync(filePath)) {
      const data = fs.readFileSync(filePath, 'utf8');
      const jsonData = JSON.parse(data);
      if (jsonData.hasOwnProperty(this.URL.full_address)) {
        this.chosen_elms = jsonData[this.URL.full_address];
        return true;
      } else {
        throw new Error(`site not found in json --- site:${this.URL.full_address}, extn:${this.adBlocker}, html: ${this.html}`);
      }
    } else {
      throw new Error("The control file was not found. Please run the replay 0 option.");
    }
  } catch (err) {
    if (err.message.startsWith("site not found in json")) {
      console.error(err.message);
    } else {
      console.error(`Failed Replay-initialization for ${this.URL.full_address}`);
      console.error(err);
    }
  }
  return false;
};

Driver.prototype.test_all_elements = async function(){
  this.final_result[this.URL.full_address] = new Array();
  while (this.elem_indx < this.chosen_elms.length){
    this.reset_result();                // reset the result between elements
    await this.test_element();
    await this.goto(this.URL.full_address);   // resets the page by refreshing it
    this.elem_indx += 1;
  }
};

Driver.prototype.test_element = async function(){
  for (let i = 0; i < this.tries; i++){
    let cssSelector;
    try{
      try{
        this.RESULT.initial_outer_html = this.chosen_elms[this.elem_indx];
        cssSelector = await this.getCSSselector(this.RESULT.initial_outer_html);
      }
      catch(error){
        console.log(`Error while loading outerHTML for ${this.URL.full_address}`, error.toString().split('\n')[0]);
        return;
      }

      const element = await this.get_element(cssSelector);
      if (!element)
        return;

      element, this.RESULT.initial_local_DOM = await this.get_local_DOM(element);
      this.RESULT.initial_tags = await this.get_total_tags();

      if (this.html_elem == "inputs"){
        this.RESULT.initial_manual = await this.page.content();
        await this.find_and_submit_forms(element);
      }
      else{
        element, this.RESULT.initial_manual = await this.get_local_DOM(element, 13);
        await this.click(element, 5);
        await this.check_opened(element);
      }
      console.log(this.temp_result);

      return;
    }
    catch(error){
      console.log(error);
      if (i !== this.tries - 1){
        await this.reinitialize();
      }
      else{
        return;
      }
    }

  }

};

Driver.prototype.find_and_submit_forms = async function(formElem) {
  if (!formElem) return;

  // Use `evaluate` to work with the browser context
  const inputFlag = await this.page.evaluate((formElem) => {
    let flag = false;
    const textValue = 'textvalue123';
    const emailValue = 'test@gmail.com';
    const numberValue = '1234567890';

    const form = document.querySelector(formElem); // Use the formElem selector to find the form
    if (!form) return flag; // Return false if the form is not found

    const textInputs = form.querySelectorAll('input[type="text"], input[type="search"], input[type="password"], textarea');
    const emailInputs = form.querySelectorAll('input[type="email"]');
    const numberInputs = form.querySelectorAll('input[type="tel"], input[type="number"]');

    textInputs.forEach(input => {
      input.focus();
      input.value = textValue; 
      flag = true;
    });
    emailInputs.forEach(input => {
      input.focus();
      input.value = emailValue;
      flag = true;
    });
    numberInputs.forEach(input => {
      input.focus(); 
      input.value = numberValue;
      flag = true;
    });

    return flag; // Return the flag indicating if any inputs were modified
  }, formElem);

  if (inputFlag) {
    const submission_stat =  await this.page.evaluate((formElem) => {
      const form = document.querySelector(formElem);
      if (form) {
        const submitButton = form.querySelector('input[type="submit"], button[type="submit"]');
        try{
          if (submitButton) {
            submitButton.click(); // Trigger the submit button click
          } else {
            form.submit(); // If no submit button found, try submitting the form directly
          }
          return true;
        } catch(error){
          return false;
        }
      }
    }, formElem);

    if (!submission_stat) {
      await this.page.keyboard.press('Enter');
    }
    await this.check_opened(formElem);
  }
  else {
    this.temp_result = 'False';
  }
};

Driver.prototype.reset_result = function(){
  this.temp_result = '';
  this.RESULT.reset();
};

Driver.prototype.check_redirect = function(){
  try {
    const parsedUrl1 = new URL(this.URL.current_url);
    const parsedUrl2 = new URL(this.page.url());

    return parsedUrl1.href !== parsedUrl2.href;
  } catch (e) {
    return false;
  }

};

Driver.prototype.check_opened = async function(element){
  if (this.check_redirect()){
    this.temp_result = "True - Redirect";
    return;
  }
  try{
    element, this.RESULT.after_local_DOM = await this.get_local_DOM(element);
  }
  catch(error){
    if (error.name === 'TimeoutError' || error.message.includes('stale element')) {
      this.temp_result = "True - Stale Element";
      console.log("Stale element error!");
    }
    return;
  }

  this.RESULT.after_outer_html = await this.page.evaluate(el => el.outerHTML, element);
  element, this.RESULT.after_local_DOM = await this.get_local_DOM(element)

  this.RESULT.outer_HTML_changed = this.RESULT.initial_outer_html != this.RESULT.after_outer_html;
  this.RESULT.local_DOM_changed = this.RESULT.initial_local_DOM != this.RESULT.after_local_DOM;
  this.RESULT.after_tags = await this.get_total_tags();
  
  if (this.RESULT.outer_HTML_changed)
    this.temp_result = "True - outerHTML change";
  else if (this.RESULT.local_DOM_changed)
    this.temp_result = "True? - Local DOM Change";
  else
    this.temp_result = "Check Filters";
};

Driver.prototype.click = async function(element, time = 3){
  await sleep(time);
  await element.click();
  await sleep(time);
};

Driver.prototype.get_element = async function(selector){

  const targetVal = this.parseOuterHTMLAttributes(this.RESULT.initial_outer_html);
  await this.page.waitForSelector(selector);
  const candidates = await this.page.$$(selector);

  let element = null;

  for (let candidate of candidates) {
    const outerHTML = await this.page.evaluate(el => el.outerHTML, candidate);
    const candidateVal = this.parseOuterHTMLAttributes(outerHTML);
    // Compare outerHTML
    if (this.compareAttributeObjects(targetVal, candidateVal)){
      element = candidate;
      break;
    }
  }

  return element;
};

Driver.prototype.get_local_DOM = async function(element, traversal_amt = this.DOM_traversal_amt){
  let original_element = await this.page.evaluateHandle(el => el.cloneNode(true), element);
  let ancestor = element;
  let parentHandle;
  for (let i = 0; i < traversal_amt; i++) {
    try {
      // Traverse up to the parent element
      parentHandle = await this.page.evaluateHandle(el => el.parentElement, ancestor);
      await this.page.evaluate(el => el.outerHTML, parentHandle);   // this will crash if we are at the top
      if (i > 0) await ancestor.dispose();
        ancestor = parentHandle;
    } catch (error) {
      if (parentHandle) await parentHandle.dispose();
      break;
    }
  }
  const outerHTML = await this.page.evaluate(el => el.outerHTML, ancestor);
  await ancestor.dispose();
  return original_element, outerHTML;
};

Driver.prototype.get_total_tags = async function(){
  const totalTags = await this.page.evaluate(() => {
    return document.getElementsByTagName('*').length;
  });
  return totalTags;
};

Driver.prototype.parseOuterHTMLAttributes = function(outerHTML) {
  const tagRegex = /^<(\w+)\s+/; // Regex to match the tag name
  const attributeRegex = /(\w+)\s*=\s*["']([^"']*)["']/g; // Regex to match attributes and their values
  const attributes = {}; // Dictionary to store attribute key-value pairs

  // Extract tag name
  const tagMatch = outerHTML.match(tagRegex);
  if (tagMatch) {
      attributes['tag'] = tagMatch[1].trim(); // Store the tag name (trimmed)
  }

  // Extract attributes
  let match;
  while ((match = attributeRegex.exec(outerHTML)) !== null) {
      const attributeName = match[1].trim(); // Attribute name (trimmed)
      const attributeValue = match[2].trim(); // Attribute value (trimmed)
      attributes[attributeName] = attributeValue;
  }

  return attributes;
};

Driver.prototype.compareAttributeObjects = function(obj1, obj2) {
  // Need to remove longest in case
  if (!obj1 || !obj2 || Object.keys(obj1).length !== Object.keys(obj2).length) {
      return false;
  }
  for (let key in obj1) {
      if (!(key in obj2) || obj1[key] !== obj2[key]) {
          return false;
      }
  }
  for (let key in obj2) {
      if (!(key in obj1)) {
          return false;
      }
  }
  return true;
};


(async () => {

  const html_options = [
    // 'drop_downs', 
    // 'buttons', 
    // 'links', 
    // 'logins', 
    'inputs'
  ];
  
  const links = [
    // 'https://en.wikipedia.org/wiki/Main_Page',
    // 'https://openai.com/', 
    'https://duckduckgo.com/', 
    // 'https://brightspace.nyu.edu/d2l/home',
    // 'https://picoctf.org/',
    // 'https://portswigger.net/web-security/all-labs'
  ];
  for (let link of links){
    for (let html_option of html_options){
      const test = new Driver(html_option, 'control', 0, {});
      // await test.initialize(link);
      // await test.find_elems();


      await test.initialize(link);
      if (test.replay_initialize()){
        console.log(test.chosen_elms.length)
        await test.test_all_elements();
      }
      await test.browser.close();
    }
  }

  // const test = new Driver('buttons', 'control', 0, {});
  // await test.initialize('https://en.wikipedia.org/wiki/Main_Page');
  // if (test.replay_initialize()){
  //   console.log(test.chosen_elms.length)
  //   await test.test_all_elements();
  // }
  console.log("FINISHED EVERYTHING");
})();
