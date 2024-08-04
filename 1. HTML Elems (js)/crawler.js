const { fork } = require('child_process');
const fs = require('fs');
const path = require('path'); 


const TIMEOUT = 15 * 60 * 1000; // 15 minutes in milliseconds
const SIZE = 2;                 // Number of driver processes to create
function divideChunks(arr, chunkSize) {
  if (chunkSize <= 0) {
      throw new Error('Chunk size must be greater than 0');
  }
  
  return Array.from({ length: Math.ceil(arr.length / chunkSize) }, (_, i) => 
      arr.slice(i * chunkSize, i * chunkSize + chunkSize)
  );
}

function write_results(data, html_elem, adBlocker, replay) {
  let folder;
  if (replay === 0) {
    folder = 'replay_0';
  } else {
    folder = 'replay_1';
  }

  const jsonData = JSON.stringify(data, null, 2);
  const filePath = path.join(__dirname, `./Results/${folder}/${html_elem}_${adBlocker}.json`);

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
}

function combineResults(results, html_elem, adBlocker, replay) {
  const final = results.reduce((acc, curr) => ({ ...acc, ...curr }), {});
  write_results(final, html_elem, adBlocker, replay);
  return final;
};

async function runBatch(chunk, html_option, extn, replay) {
  const results = [];
  const jobs = chunk.map((site, index) => {
      return new Promise((resolve, reject) => {
          const childProcess = fork(path.join(__dirname, 'driver.mjs'), [site, html_option, extn, replay]);

          childProcess.on('message', (message) => {
            results[index] = message;
          });

          childProcess.on('error', (err) => {
              console.error(`Error in process ${index}:`, err);
              reject(err);
          });

          childProcess.on('exit', (code) => {
              console.log(`Process ${index} exited with code ${code}`);
              resolve();
          });

          setTimeout(() => {
              if (childProcess.exitCode === null) { // process is still running
                  console.log(`Timeout exceeded... terminating job ${index}`);
                  childProcess.kill();
              }
          }, TIMEOUT);
      });
  });



  // Wait for all jobs in the batch to finish
  await Promise.all(jobs);

  combineResults(results, html_option, extn, replay);
}

async function runInBatches(chunksList, html_option, extn, replay) {
  for (const chunk of chunksList) {
      console.log('Processing batch:', chunk);
      await runBatch(chunk, html_option, extn, replay);
      console.log('Batch completed. Waiting before proceeding to the next batch...');
      await new Promise(resolve => setTimeout(resolve, 2000)); // Sleep for 2 seconds between batches
  }
}




const html_options = [
  // 'drop_downs', 
  // 'buttons', 
  // 'links', 
  // 'logins', 
  'inputs'
];

const links = [
  'https://t.hi098123.com/korean-number#google_vignette'
  // 'https://openai.com/', 
  // 'https://duckduckgo.com/', 
  // 'https://brightspace.nyu.edu/d2l/home',
  // 'https://picoctf.org/',
  // 'https://rufus.ie/en/',              // scroll down, download, redirect
  // 'https://picoctf.org/contact.html'   // Is application open
  // 'https://en.wikipedia.org/w/index.php?title=Special:UserLogin&returnto=Main+Page&returntoquery=centralAuthAutologinTried%3D1%26centralAuthError%3DNot%2Bcentrally%2Blogged%2Bin'  //isRequired
  //    'https://canyoublockit.com/'      // testing adblocker
];

let extn_lst = [
  'control', 
  // 'adblock', 
  'ublock', 
  // 'privacy-badger'
];


(async () => {

  const args = process.argv.slice(2);
  let replay = 0; // Default value

  // Extract the --replay argument
  args.forEach((arg, index) => {
    if (arg === '--replay' && args[index + 1] !== undefined) {
      replay = parseInt(args[index + 1], 10);
    }
  });

  // Ensure replay is either 0 or 1
  if (isNaN(replay) || (replay !== 0 && replay !== 1)) {
    console.error('Invalid --replay argument. Please provide 0 or 1.');
    process.exit(1);
  }


  if (replay === 0)
    extn_lst = ['control']
  const chunks = divideChunks(links, SIZE);
  for (let html_option of html_options) {
    for (let extn of extn_lst) {
      try {
        await runInBatches(chunks, html_option, extn, replay);
        console.log('All batches processed.');
      } catch (err) {
        console.error('Error processing batches:', err);
      }
    }
  }
  console.log('All processing completed. Exiting program.');
  process.exit(0); // Explicitly exit the program
})();
