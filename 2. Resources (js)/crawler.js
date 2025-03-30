import { fork } from 'child_process';
import fs from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

// Get the current file path and directory name
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);


const TIMEOUT = 5 * 60 * 1000; // 15 minutes
const SIZE = 5;                 // Number of driver processes to create

const catapult = false;          // testing mode




const websiteKey = (url) => {
  const parsedUrl = new URL(url);
  const hostname = parsedUrl.hostname; 

  const domain = hostname.startsWith('www.') ? hostname.slice(4) : hostname;

  const baseDomain = domain.replace(/\.(com|net|org|co|io|gov|edu|info|biz)$/i, '');

  return baseDomain;  
};

function divideChunks(arr, chunkSize) {
  if (chunkSize <= 0) {
      throw new Error('Chunk size must be greater than 0');
  }
  
  return Array.from({ length: Math.ceil(arr.length / chunkSize) }, (_, i) => 
      arr.slice(i * chunkSize, i * chunkSize + chunkSize)
  );
};

function subset(jsonArray) {
  const jsonObjects = jsonArray
    .map(jsonString => JSON.parse(jsonString))
    .filter(obj => Object.keys(obj).length > 0); // Keep only non-empty objects

  if (jsonObjects.length === 0) return {}; // Return empty object if all were empty

  const commonPairs = {};

  for (const [key, value] of Object.entries(jsonObjects[0])) {
    if (jsonObjects.every(obj => obj.hasOwnProperty(key))) {
      commonPairs[key] = value;
    }
  }

  return commonPairs;
}

function write_results(website, data) {
  let finalData = {[website]: data};
  const filePath = join(`./Results/all_resources.json`);

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

async function runBatch(chunk, extn, extn_lst, control_resources) {
  const results = [];
  const jobs = chunk.map((site, index) => {
    const key = websiteKey(site);
    
    var processCount;
    if (control_resources==='false'){
      processCount = (extn === 'control') ? 3 : 1;
    }
    else{
      processCount = 1;
    }

    // Create an array of promises for each job
    const jobPromises = Array.from({ length: processCount }, (_, processIndex) => {
      return new Promise((resolve, reject) => {
        const childProcess = fork(join(__dirname, 'driver.mjs'), [extn, site, key, extn_lst, control_resources]);

        childProcess.on('message', (message) => {
            results[processIndex] = message;
        });

        childProcess.on('error', (err) => {
          console.error(`Error in process ${index}, instance ${processIndex}:`, err);
          reject(err);
        });

        childProcess.on('exit', (code) => {
          console.log(`Extn ${extn}, instance ${processIndex} exited with code ${code}`);
          resolve();
        });

        setTimeout(() => {
          if (childProcess.exitCode === null) {
            console.log(`Timeout exceeded... terminating job ${index}, instance ${processIndex}`);
            childProcess.kill();
          }
        }, TIMEOUT);
      });
    });

    return Promise.all(jobPromises);
  });

  // Wait for all jobs in the batch to finish
  await Promise.all(jobs);

  return results;
};


async function runInBatches(chunksList, extn_lst) {
  
  for (const chunk of chunksList) {

    console.log('Processing Chunk:', chunk);

    for (const website of chunk){
      /*

      Check 1: run 3 control browsers and get the subset of the images

      */

      console.log('Running controls', website);
      const control_resources = await runBatch(chunk, 'control', extn_lst, 'false'); //starts 3 control browsers
      if (control_resources.length == 0){
        continue;
      }

      //need to store this value
      const control_final_subset = subset(control_resources);
      // write_results(websiteKey(website), control_final_subset);

      const extn_resources = new Array(extn_lst.length);
      const extn_resources_string = JSON.stringify(control_final_subset, null, 2);

      const extnPromises = extn_lst.map((extn, i) => {
        console.log('Testing extn:', extn);
        return runBatch(chunk, extn, extn_lst, extn_resources_string).then(result => {
          extn_resources[i] = result;
        });
      });

      await Promise.all(extnPromises);

      await new Promise(resolve => setTimeout(resolve, 2000)); // Sleep for 2 seconds between batches
      
      console.log("Finished running website:", website);

      console.log("Starting Comparison for:", website);
      
    }
     
  }
};




const websites = [
  // "https://www.cnn.com",
  // "https://www.bbc.com",
  // "https://www.nytimes.com",
  // "https://www.theguardian.com",
  "https://www.washingtonpost.com",         // doesn't work in headless
  "https://www.nbcnews.com",
  "https://www.reuters.com",
  "https://www.forbes.com",
  "https://www.wsj.com",
  "https://www.nbcnews.com/",
  'https://www.washingtonpost.com/',
  'https://www.uxmatters.com/',
  'https://www.reddit.com/',
  "https://www.baidu.com",  
  "https://www.tmall.com",  
  "https://www.weibo.com",  
  "https://www.jd.com",     
  "https://www.douyin.com", 
  "https://www.mi.com",     // Electronics and smartphones
  "https://www.cctv.com",   // National TV broadcaster
  "https://www.taobao.com", // E-commerce platform
  "https://www.163.com",    // News and entertainment
  "https://www.qq.com",     // Instant messaging and social media
  "https://www.bilibili.com", // Video-sharing platform
  "https://www.meituan.com", // Local services and food delivery
  "https://www.alipay.com",  // Online payment platform
  "https://www.zol.com.cn",  // Technology news and reviews
  "https://www.dianping.com", // Business reviews
  "https://www.tudou.com",   // Video streaming platform
  "https://www.wechat.com",  // Messaging app

]

let extn_lst = [
  'adblock', 
  // 'ublock', 
  // 'privacy-badger',
  // 'adguard',
  'control', // launching control is required
];



(async () => {

  const args = process.argv.slice(2);

  const chunks = divideChunks(websites, SIZE);

  try {
    await runInBatches(chunks, extn_lst);
    console.log('All batches processed.');
  } catch (err) {
    console.error('Error processing batches:', err);
  }
  

  console.log('All processing completed. Exiting program.');
  process.exit(0); // Explicitly exit the program
})();
