import puppeteer from 'puppeteer';
import fs from 'fs';

async function findImageEmbeddings(imageUrl, pageUrl) {
    const browser = await puppeteer.launch({ headless: true }); // Launch Puppeteer
    const page = await browser.newPage(); // Open a new page
    await page.goto(pageUrl); // Navigate to the specified URL

    const results = [];

    // Helper function to add results
    const addResult = (selector, method, elementHandle) => {
        results.push({ selector, method, elementHandle });
    };

    // 1. Check <img> tags
    const imgElements = await page.$$('img');
    for (const img of imgElements) {
        const src = await img.evaluate(el => el.src);
        if (src === imageUrl) {
            addResult('img', `<img> tag with src="${src}"`, img);
        }
    }

    // 2. Check CSS background-image
    const allElements = await page.$$('*');
    for (const el of allElements) {
        const bgImage = await el.evaluate(el => window.getComputedStyle(el).backgroundImage);
        if (bgImage.includes(imageUrl)) {
            addResult(el.tagName.toLowerCase(), `CSS background-image with URL "${imageUrl}"`, el);
        }
    }

    // 3. Check <picture> elements
    const pictureSources = await page.$$('picture source');
    for (const source of pictureSources) {
        const srcset = await source.evaluate(el => el.srcset);
        if (srcset.includes(imageUrl)) {
            addResult('picture source', `<picture> element with srcset="${srcset}"`, source);
        }
    }

    // 4. Check <object> tags
    const objectElements = await page.$$('object');
    for (const object of objectElements) {
        const data = await object.evaluate(el => el.data);
        if (data === imageUrl) {
            addResult('object', `<object> tag with data="${data}"`, object);
        }
    }

    // 5. Check <embed> tags
    const embedElements = await page.$$('embed');
    for (const embed of embedElements) {
        const src = await embed.evaluate(el => el.src);
        if (src === imageUrl) {
            addResult('embed', `<embed> tag with src="${src}"`, embed);
        }
    }

    // 6. Check inline SVG
    const svgImages = await page.$$('svg image');
    for (const svgImage of svgImages) {
        const href = await svgImage.evaluate(el => el.getAttribute('xlink:href') || el.getAttribute('href'));
        if (href === imageUrl) {
            addResult('svg image', `Inline SVG with href="${href}"`, svgImage);
        }
    }

    // 7. Check <figure> elements
    const figureImages = await page.$$('figure img');
    for (const img of figureImages) {
        const src = await img.evaluate(el => el.src);
        if (src === imageUrl) {
            addResult('figure img', `<figure> element with src="${src}"`, img);
        }
    }

    // Take screenshots of the found elements
    for (const result of results) {
        const { selector, method, elementHandle } = result;
        const screenshotPath = `screenshot_${selector}_${Date.now()}.png`;

        // Ensure the element is visible in the viewport
        await elementHandle.scrollIntoViewIfNeeded();

        // Take a screenshot of the element
        await elementHandle.screenshot({ path: screenshotPath });
        console.log(`Screenshot saved: ${screenshotPath} (${method})`);
    }

    await browser.close(); // Close the browser
    return results;
}

// Example usage
(async () => {
    const imageUrl = 'https://www.uxmatters.com/images/sponsors/UXmattersPatreonBanner.png';
    const pageUrl = 'https://www.uxmatters.com/'; // Replace with the target webpage URL
    const embeddings = await findImageEmbeddings(imageUrl, pageUrl);
    console.log(embeddings);
})();