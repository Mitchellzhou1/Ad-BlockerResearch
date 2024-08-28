// Import the `exec` function from `child_process` using ES Module syntax
import { exec } from 'node:child_process';

// Run a command using `exec`
exec('ls -l', (error, stdout, stderr) => {
    if (error) {
        console.error(`exec error: ${error}`);
        return;
    }
    console.log(`stdout: ${stdout}`);
    console.error(`stderr: ${stderr}`);
});
