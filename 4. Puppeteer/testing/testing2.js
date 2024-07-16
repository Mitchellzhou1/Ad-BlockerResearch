const fs = require('fs');
const path = require('path');

// Function to list files in the current directory
function listFilesInDirectory() {
  try {
    const directoryPath = __dirname;
    const files = fs.readdirSync(directoryPath);
    
    console.log('Files in the current directory:');
    files.forEach((file) => {
      const filePath = path.join(directoryPath, file);
      const fileStats = fs.statSync(filePath);
      
      if (fileStats.isFile()) {
        console.log(`- ${file}`);
      }
    });
  } catch (err) {
    console.error('Error reading directory:', err);
  }
}

// Call the function
listFilesInDirectory();
