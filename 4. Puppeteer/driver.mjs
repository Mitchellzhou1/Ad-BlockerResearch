import puppeteer from 'puppeteer';
import { JSDOM } from 'jsdom';
import { Result } from './result.mjs';
import { Url } from './url.mjs';



function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }


class Driver{
  constructor(html_elem, adB, replay, data_dict){
    this.adBlocker = adB;
    this.driver = null;
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
    this.results = new Result()
    this.URL = new Url()                    // Correct instantiation of Url class
    this.temp_result = ''                   // used to temporarily hold the result
    this.final_result = data_dict
    // this.temp_chosen_elms= []
    this.chosen_elms = []

    /* RITIK */ 
    this.options = ''
    this.replay = replay

    /* Methods */

    // // Driver, page, Functions

    // this.initialize = initialize;
    // this.replay_initialize = replay_initialize;
    // this.is_loaded = is_loaded;
    // this.wait_until_loaded = wait_until_loaded;
    // this.load_site = load_site;
    // this.reinitialize = reinitialize;
    // this.scroll = scroll;
    // this.take_ss = take_ss;

    // // Comparison Methods

    // this.cursor_change = cursor_change;
    // this.check_redirect = check_redirect;
    // this.count_tags = count_tags;
    // this.get_local_dom = get_local_dom;
    
    // // Testing

    // this.check_opened = check_opened;
    // this.test_button = test_button;
    // this.test_page = test_page;

    // // Scaning
    // this.scan_page = scan_page;
    // this.get_elements = get_elements;
    // this.generate_xpath = generate_xpath;
    // this.get_correct_elem = get_correct_elem;
    // this.filter = filter;
    // this.get_specific_elem = get_specific_elem;
    // this.find_buttons = find_buttons;
    // this.find_dropdown = find_dropdown;
    // this.find_links = find_links;
    // this.find_login = find_login;
    // this.find_forms = find_forms;

    // // False Positive Checks
    // this.is_slideshow = is_slideshow;
    // this.is_required = is_required;
    // this.is_scrollpage = is_scrollpage;
    // this.is_download_link = is_download_link;
    // this.is_open_application = is_open_application;

    // // Submitting Forms
    // this.find_and_submit_forms = find_and_submit_forms;
    // this.enter_forms = enter_forms;
    // this.submit_form = submit_form;
  }

}

Driver.prototype.initialize = async function(){
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

  this.driver = page;
};

Driver.prototype.goto = async function(url) {
  await this.driver.goto(url);
};

Driver.prototype.find_elems = async function() {
  const methodMap = {
    'drop_downs': this.find_dropdowns.bind(this),
    'buttons': this.find_buttons.bind(this),
    'links': this.find_links.bind(this),
    'logins': this.find_logins.bind(this),
    'forms': this.find_forms.bind(this)
  };
  
  const method = methodMap[this.html_elem];
  
  if (method) {
    var ret = await method();
  } else {
    console.error("You have entered an unsupported HTML type");
  }

  console.log(ret);
  var unique = [];
  for (let html of unique){

    if (unique.length >= 15 && this.html_elem == 'links') break;

    if (!unique.includes(html)){
      // this.filter(html)
      unique.push(html);
    }

  }

  this.chosen_elms = unqiue;
};

Driver.prototype.specificElementFinder = async function(elems) {

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
    'logins': {
        'attributes': ['button', 'submit', '#'],
        'values': ['role', 'type']
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
  const { debug, final } = await this.driver.evaluate((attributes, values) => {
    const debug = [];
    const final = [];
    for (const value of values) {
      for (const attr of attributes) {
        const query = `[${value}='${attr}']`;
        const buttons = document.querySelectorAll(query);

        buttons.forEach(button => {
          debug.push({
            tagName: button.tagName,
            foundBy: query,
            outerHTML: button.outerHTML
          });

          final.push(button.outerHTML);  // elems is a set
        });
      }
    }
    return {debug, final};
  }, attributes, values);

  console.log("Printing Debugging");
  console.log(debug); // For debugging
  return final
};




Driver.prototype.find_dropdowns = async function(){
  /*
    Dropdowns are defined in this study if having specific HTML attributes
  */
  const elements_specific = await this.specificElementFinder();
  const final = new Set(elements_specific);
  
  return final;
};

Driver.prototype.find_buttons = async function(){
  /*
    Buttons are defined in this study as any element with 
    <button> tag, <a> tag with no href attribute, or having
    specific HTML attributes
  */

  await this.driver.waitForSelector('button, a');
  const elements_general = await this.driver.evaluate(() => {
    const buttonElements = document.querySelectorAll('button');
    const anchorElements = document.querySelectorAll('a');

    uniqueSet = new Set();
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
};

Driver.prototype.find_links = async function(){
  /*
    Links are defined in this study as <a> tag  with href attribute
  */
  await this.driver.waitForSelector('a');

  const elements_general = await this.driver.evaluate((currentURL, fullAddress) => {
    const anchorElements = document.querySelectorAll('a');
    const blacklist = ['#', '/', currentURL, fullAddress];
  
    const uniqueHrefs = new Set();
    
    anchorElements.forEach(anchor => {
      if (anchor.hasAttribute('href')) {
        const href = anchor.getAttribute('href');
        if (!blacklist.includes(href)) {
          uniqueHrefs.add(anchor.outerHTML);
        }
      }
    });
  
    return Array.from(uniqueHrefs);
  }, this.URL.current_url, this.URL.full_address);

  const final = new Set(elements_general);
  
  return final;
};

Driver.prototype.find_logins = async function(){
  /*
    Logins are defined in this study as any element with 
    <button> tag, <a> tag, or HTML elements having specific predefined attributes.
    These elements then go through a filter that checks for keywords such as 
    'login', 'signin', 'my account', etc.
  */

    const filter = [
      'login', 'my account', 'sign in', 'sign-in', 'signin', 'log in',  // English
      '登录', '我的帐户',  // Chinese (Simplified)
      'вход', 'войти', 'мой аккаунт',  // Russian
      'iniciar sesión', 'mi cuenta'  // Spanish
    ];
    await this.driver.waitForSelector('button, a');
    const elements_general = await this.driver.evaluate(() => {
      const buttonElements = document.querySelectorAll('button');
      const anchorElements = document.querySelectorAll('a');

      uniqueSet = new Set();
      buttonElements.forEach(button => {
        if (filter.some(word => button.outerHTML.includes(word))) {
          uniqueSet.add(button.outerHTML);
        }
      });
    
      anchorElements.forEach(anchor => {
        if (anchor.hasAttribute('href') && filter.some(word => anchor.outerHTML.includes(word))) {
          uniqueSet.add(anchor.outerHTML);
        }
      });

      return Array.from(uniqueSet);
    });

  const elements_specific = await this.specificElementFinder();
  const final = new Set([...elements_specific, ...elements_general]);
  
  return final;


};

Driver.prototype.find_forms = async function(){
  /*
    Forms are defined in this study as any element that has a <form> tag.
  */
    await this.driver.waitForSelector('form');

    const elements_general = await this.driver.evaluate(() => {
      const formElements = document.querySelectorAll('form');
    
      uniqueSet = new Set();
      
      formElements.forEach(form => {
        uniqueSet.add(form.outerHTML);
        }
      );
    
      return Array.from(uniqueSet);
    });
  
    const final = new Set(elements_general);
    
    return final;
};

(async () => {
  const test = new Driver('buttons', 'ublock', 0, {});
  await test.initialize();
  console.log("done initialize");
  await test.goto('https://www.programiz.com/python-programming/online-compiler/');
  console.log("done loading site");
  await test.find_elems();

})();
