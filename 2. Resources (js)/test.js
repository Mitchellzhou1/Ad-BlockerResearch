import { fork } from 'child_process';
import fs from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const b = {
    "blacklist": {
        "https://www.uxmatters.com/images/sponsors/UXmattersPatreonBanner.png": {
            "responseCode": 200,
            "statusText": "N/A",
            "contentLength": "9467",
            "contentType": "image/png",
            "referrer": "https://www.uxmatters.com/",
            "blacklistRule": "||uxmatters.com/images/sponsors/"
        }
    }
}

const c = {
    "blacklist": {
        "https://www.uxmatters.com/images/sponsors/UXmattersPatreonBanner.png": {
            "responseCode": 600
        }
    }
}


function write_results(website, data) {
    let finalData = {[website]: data.blacklist};
    const filePath = join(`./Results/resources/all_resources.json`);
  
    if (fs.existsSync(filePath)) {
        const existingData = fs.readFileSync(filePath, 'utf8');
        if (existingData) {
          // If file exists, parse the existing data and combine it with new data
          const existingJson = JSON.parse(existingData);
          finalData = { ...existingJson, ...finalData };
        } 
    }
    
    
    finalData = JSON.stringify(finalData, null, 2);
  
    // Write the combined data back to the file
    fs.writeFileSync(filePath, finalData, 'utf8', (err) => {
      if (err) {
        console.error('Error writing file:', err);
        return;
      }
      console.log('Data has been written to', filePath);
    });
  };


write_results('uxmatters', b);
write_results('test', c);