// Importing the fs (file system) module
const fs = require('fs');

// Example data to write to the JSON file
const data = {
  name: 'John Doe',
  age: 30,
  city: 'New York'
};

// Convert data to JSON format
const jsonData = JSON.stringify(data, null, 2); // null and 2 are for pretty formatting

// File path where the JSON file will be written
const filePath = './record/data.json';

// Write JSON data to the file
fs.writeFile(filePath, jsonData, 'utf8', (err) => {
  if (err) {
    console.error('Error writing file:', err);
    return;
  }
  console.log('Data has been written to', filePath);
});
