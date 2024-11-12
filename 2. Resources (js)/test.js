import fs from 'fs';

// Create a sample Map object
const map = new Map([
  ['name', 'John'],
  ['age', 30],
  ['city', 'New York']
]);

function store(key, blacklistedItems){
    const blacklist = Object.fromEntries(blacklistedItems);
    const blacklistString = JSON.stringify(blacklist, null, 4);  // Adds indentation for readability

    fs.writeFile(`${key}.json`, blacklistString, (err) => {
        if (err) {
            console.error('Error writing file:', err);
        } else {
            console.log('File successfully written!');
        }
    });
    };

store('dog', map);