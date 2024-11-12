import { fork } from 'child_process';
import fs from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

// Get the current file path and directory name
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);


const TIMEOUT = 5 * 60 * 1000; // 15 minutes
const SIZE = 1;                 // Number of driver processes to create

const catapult = false;          // testing mode




const websiteKey = (url) => {
  let key = '';
  url = url.replace(/^\/+|\/+$/g, ''); // Remove leading/trailing slashes
  if (url.includes('www.')) {
      key = url.split('www.')[1];
  } else {
      key = url.split('://')[1];
  }
  key = key.replace(/\//g, '-');
  return key;
};

function divideChunks(arr, chunkSize) {
  if (chunkSize <= 0) {
      throw new Error('Chunk size must be greater than 0');
  }
  
  return Array.from({ length: Math.ceil(arr.length / chunkSize) }, (_, i) => 
      arr.slice(i * chunkSize, i * chunkSize + chunkSize)
  );
};

function subset(jsonArray){
  const jsonObjects = jsonArray.map(jsonString => JSON.parse(jsonString));

  const commonPairs = {};

  for (const [key, value] of Object.entries(jsonObjects[0])) {
      if (jsonObjects.every(obj => obj.hasOwnProperty(key))) {
          commonPairs[key] = value;
      }
      else{
        console.log(key);
      }
  }

  return commonPairs;
};

function write_results(data) {x
  let folder;
  const jsonData = JSON.stringify(data, null, 2);
  const filePath = join(__dirname, `./Results/${folder}/${html_elem}_${adBlocker}.json`);

  // Check if the file already exists
  fs.readFile(filePath, 'utf8', (err, existingData) => {
    if (err && err.code !== 'ENOENT') {
      console.error('Error reading file:', err);
      return;
    }

    let combinedData;
    if (existingData) {
      // If file exists, parse the existing data and combine it with new data
      const existingJson = JSON.parse(existingData);
      combinedData = { ...existingJson, ...data };
    } else {
      // If file does not exist, use new data as combined data
      combinedData = data;
    }

    // Convert combined data back to JSON string
    const combinedJsonData = JSON.stringify(combinedData, null, 2);

    // Write the combined data back to the file
    fs.writeFile(filePath, combinedJsonData, 'utf8', (err) => {
      if (err) {
        console.error('Error writing file:', err);
        return;
      }
      console.log('Data has been written to', filePath);
    });
  });
};


async function runBatch(chunk, extn) {
  const results = [];
  const jobs = chunk.map((site, index) => {
    const key = websiteKey(site);

    // const processCount = (extn === 'control') ? 3 : 1;
    const processCount = 1;

    // Create an array of promises for each job
    const jobPromises = Array.from({ length: processCount }, (_, processIndex) => {
      return new Promise((resolve, reject) => {
        const childProcess = fork(join(__dirname, 'driver.mjs'), [extn, site, key]);

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
}



async function runInBatches(chunksList, extn) {
  
  for (const chunk of chunksList) {

    console.log('Processing Chunk:', chunk);

    for (const website of chunk){
      /*

      Check 1: run 3 control browsers and get the subset of the images

      */

      console.log('Running controls', website);
      const control_resources = await runBatch(chunk, 'control'); //starts 3 control browsers
      const control_final_subset = subset(control_resources);

      const extn_resources = new Array(extn_lst.length);
      const extnPromises = extn_lst.map((extn, i) => {
        console.log('Testing extn:', extn);
        return runBatch(chunk, extn).then(result => {
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




const html_options = [
  // 'drop_downs', 
  // 'buttons', 
  'links', 
  // 'logins', 
  // 'inputs'
];

const websites = [
  "https://www.uxmatters.com/",
]

let extn_lst = [
  'control', // the control is included in each run of the website
  // 'adblock', 
  // 'ublock', 
  // 'privacy-badger',
  // 'adguard'
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
