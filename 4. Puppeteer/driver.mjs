import puppeteer from 'puppeteer';
import fs from 'fs';
import { JSDOM } from 'jsdom';
import { Result } from './result.mjs';
import { Url } from './url.mjs';



function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
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
    this.results = new Result()
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
  await this.page.goto(url);
};

Driver.prototype.goto = async function(url) {
  await this.page.goto(url);
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
};

Driver.prototype.checkCursorStyle = async function(cssSelector) {
  try {
      await this.page.waitForSelector(cssSelector);
      const element = await this.page.$(cssSelector);
      await element.hover();

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
  console.log(this.URL.full_address);
  console.log(this.chosen_elms);
  console.log('*'.repeat(100));
  await this.write_results();
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
    this.temp_result = '';              // reset the result between elements
    this.goto(this.URL.full_address);   // resets the page by refreshing it
    this.test_element();
    this.elem_indx += 1;
  }
};

(async () => {
  const html_options = ['drop_downs', 'buttons', 'links', 'logins', 'inputs'];
  // for (let html_option of html_options){
  //   const test = new Driver(html_option, 'control', 0, {});
  //   await test.initialize('https://en.wikipedia.org/wiki/Main_Page');
  //   await test.find_elems();
  //   await test.browser.close();
  // }

  const test = new Driver('buttons', 'control', 0, {});
  await test.initialize('https://en.wikipedia.org/wiki/Main_Page');
  if (test.replay_initialize()){
    await test.test_all_elements();
  }

})();
