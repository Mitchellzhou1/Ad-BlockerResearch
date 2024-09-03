import { spawn } from 'node:child_process';

function run_cmd(cmd) {
    return new Promise((resolve, reject) => {
      const full_cmd = ['wrapper.py'].concat(cmd);
      const pythonProcess = spawn('python3', full_cmd);
  
      let result = '';
  
      pythonProcess.stdout.on('data', (data) => {
          result += data.toString(); // Accumulate output data
      });
  
      pythonProcess.stderr.on('data', (data) => {
          console.error(`Stderr: ${data}`);
      });
  
      pythonProcess.on('error', (error) => {
          reject(`Error: ${error.message}`);
      });
  
      pythonProcess.on('close', (code) => {
          console.log(`Process exited with code ${code}`);
          if (code === 0) {
              resolve(result); // Resolve with the accumulated result
          } else {
              reject(`Process exited with code ${code}`);
          }
      });
    });
  }

  
const output = await run_cmd(['get_wpr_ports']); // Wait for cmd to complete and get the output
console.log(`Command Output:\n${output}`); // Print the command output

// Execute the rest of the script
for (let i = 0; i < 10; i++) {
    console.log("TESTTTTTT");
}

