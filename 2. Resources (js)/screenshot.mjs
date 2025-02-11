import puppeteer from 'puppeteer';
import { exec } from 'child_process';
import https from 'https';
import fs from 'fs';
import { fork } from 'child_process';

function removeDirectory(directoryPath) {
    // Execute the shell command 'rm -rf' on the provided directory path
    exec(`rm -rf ${directoryPath}`, (err, stdout, stderr) => {
      if (err) {
        console.error(`Error executing rm -rf: ${stderr}`);
      } else {
        console.log(`Successfully deleted: ${directoryPath}`);
      }
    });
  }

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
};

async function clickVideos(missingUrl, page) {

    const results = [];

    const videoElements = await page.$$('video')
    for (const vids of videoElements) {
        const src = await vids.evaluate(el => el.src);
        if (src === missingUrl) {
            results.push(vids);
        }
    }
    return results;
};


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
    try{
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
    }catch{
        return 'Failed to Download';
    }
}

// Example usage
export async function take_ss(missingUrls, pageUrl, adblocker, browser, page, key, resource) {

    var file_path  = 'screenshots' + '/' + key + '/' + adblocker;
    var delete_flag = true;
    var page_resources;
    var adResources = [];
    for (const [i, missingUrl] of Object.entries(missingUrls)) {

        // const browser = await puppeteer.launch({ headless: true }); // Launch Puppeteer
        // const page = await browser.newPage(); // Open a new page
        // await page.goto(pageUrl); // Navigate to the specified URL

        let resource = missingUrl.type;
        if (!fs.existsSync(file_path)){
            fs.mkdirSync(file_path, { recursive: true });
            console.log(`Folder created successfully!: ${file_path}`);    
        }
        
        // For each element in the missing resources list:
        if (resource == 'images') {
            page_resources = await findImage(missingUrl, page);       // returns list of CdpElementHandles
        } else {
            page_resources = await clickVideos(missingUrl, page);
        }

   

        // Take screenshots of the found elements
        delete_flag = false;

        // need for loop because 1 resource blocked could be reflect multiple times in the HTML
        if (resource == 'images') {
            for (const [index, elementHandle] of page_resources.entries()) {

            try{
                await elementHandle.scrollIntoViewIfNeeded();
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
        else {
            console.log(missingUrl);
            downloadImage(missingUrl,`${file_path}/vid_${i}.mp4`)
            adResources.push({
                id: `img_${i}.png`,
                Url: missingUrl
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
    }else{
        removeDirectory(file_path);
    }

    return file_path;
}
