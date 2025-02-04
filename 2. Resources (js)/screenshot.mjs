import puppeteer from 'puppeteer';
import https from 'https';
import { Url } from '../1. HTML Elems (js)/url.mjs';
import fs from 'fs';
import { fork } from 'child_process';

async function findImage(missingUrl, page) {

    const results = [];

    // 1. Check <img> tags
    const imgElements = await page.$$('img');
    for (const img of imgElements) {
        const src = await img.evaluate(el => el.src);
        if (src === missingUrl) {
            results.push(img);
        }
    }

    // 2. Check CSS background-image
    const allElements = await page.$$('*');
    for (const el of allElements) {
        const bgImage = await el.evaluate(el => window.getComputedStyle(el).backgroundImage);
        if (bgImage.includes(missingUrl)) {
            results.push(el);
        }
    }

    // 3. Check <picture> elements
    const pictureSources = await page.$$('picture source');
    for (const source of pictureSources) {
        const srcset = await source.evaluate(el => el.srcset);
        if (srcset.includes(missingUrl)) {
            results.push(source);
        }
    }

    // 4. Check <object> tags
    const objectElements = await page.$$('object');
    for (const object of objectElements) {
        const data = await object.evaluate(el => el.data);
        if (data === missingUrl) {
            results.push(object);
        }
    }

    // 5. Check <embed> tags
    const embedElements = await page.$$('embed');
    for (const embed of embedElements) {
        const src = await embed.evaluate(el => el.src);
        if (src === missingUrl) {
            results.push(embed);
        }
    }

    // 6. Check inline SVG
    const svgImages = await page.$$('svg image');
    for (const svgImage of svgImages) {
        const href = await svgImage.evaluate(el => el.getAttribute('xlink:href') || el.getAttribute('href'));
        if (href === missingUrl) {
            results.push(svgImage);
        }
    }

    // 7. Check <figure> elements
    const figureImages = await page.$$('figure img');
    for (const img of figureImages) {
        const src = await img.evaluate(el => el.src);
        if (src === missingUrl) {
            results.push(img);
        }
    }


    return results;
}


async function getParent(element, traversalAmt = 3, page) {
    let ancestor = element;
  
    for (let i = 0; i < traversalAmt; i++) {
      try {
        const parentHandle = await page.evaluateHandle(el => el.parentElement, ancestor);
          if (i > 0) await ancestor.dispose();
          ancestor = parentHandle;
          const parentElement = await page.evaluate(el => el, parentHandle);
        if (!parentElement) {
          await parentHandle.dispose();
          return null;
        }
      } catch (error) {
        console.error('Error during traversal:', error);
        if (ancestor) await ancestor.dispose();
        return null;
      }
    }
    return ancestor;
  }

  function downloadImage(url, fileName) {
    const file = fs.createWriteStream(fileName);

    https.get(url, (response) => {
        response.pipe(file); // Pipe the response data to the file

        file.on('finish', () => {
            file.close();
            console.log(`Image downloaded and saved as ${fileName}`);
        });
    }).on('error', (err) => {
        fs.unlink(fileName, () => {}); // Delete the file if there's an error
        console.error(`Error downloading image: ${err.message}`);
    });
}

// Example usage
export async function take_ss(missingUrls, pageUrl, adblocker, browser, page) {

    // const missingUrl = 'https://www.uxmatters.com/images/sponsors/UXmattersPatreonBanner.png';
    // const pageUrl = 'https://www.uxmatters.com/'; // Replace with the target webpage URL
    var file_path;
    for (const [key, missingUrl] of Object.entries(missingUrls)) {

        const url_base = new Url()
        const adResources = [];
        url_base.initialize(pageUrl);
        var delete_flag = true;
        file_path  = 'screenshots' + '/' + url_base.key + '/' + adblocker;

        // const browser = await puppeteer.launch({ headless: true }); // Launch Puppeteer
        // const page = await browser.newPage(); // Open a new page
        // await page.goto(pageUrl); // Navigate to the specified URL


        if (!fs.existsSync(url_base.key)){
            fs.mkdirSync(file_path, { recursive: true });
            console.log(`Folder created successfully!: ${file_path}`);    
        }
        
        // For each element in the missing resources list:
        const resources = await findImage(missingUrl, page);       // returns list of CdpElementHandles

        if (resources){
        /*
        
        {
            id: 'img1',
            outerHTML: '<img src="img1.jpg" alt="Image 1">',
            parentHTML: '<div class="container"></div>'
        },
        {
            id: 'img2',
            outerHTML: '<img src="img2.jpg" alt="Image 2">',
            parentHTML: '<div class="container"></div>'
        }

        */

            // Take screenshots of the found elements
            delete_flag = false;

            // need for loop because 1 resource blocked could be reflect multiple times in the HTML
            for (const [index, elementHandle] of resources.entries()) {

                // Ensure the element is visible in the viewport
                await elementHandle.scrollIntoViewIfNeeded();

                // Take a screenshot of the element
                try{
                    await elementHandle.screenshot({ path: `${file_path}/img_${index}.png` });
                    console.log(`Screenshot saved: ${missingUrl}`);
                }
                catch{
                    downloadImage(missingUrl,`${file_path}/img_${index}.png`)
                }
                adResources.push({
                    id: `img_${index}.png`,
                    outerHTML: await elementHandle.evaluate(element => element.outerHTML),
                });

            }       
        }

        if (!delete_flag){
            const data = JSON.stringify(adResources, null, 2);

            // Write the string to a file
            fs.writeFile(`${file_path}/mappings.json`, data, (err) => {
                if (err) {
                    console.error('Error writing to file', err);
                } else {
                    console.log('File has been written successfully');
                }
            });

            await page.screenshot({
                path: `${file_path}/entire_page.png`, 
                fullPage: true,
            });
        }
        

    }

    return file_path;
}
