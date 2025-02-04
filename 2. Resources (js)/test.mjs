import https from 'https';
import fs from 'fs'

// Function to download an image
function downloadImage(url, fileName) {
    const file = fs.createWriteStream(fileName);

    https.get(url, (response) => {
        response.pipe(file); // Pipe the response data to the file

        file.on('finish', () => {
            file.close();
            console.log(`Image downloaded and saved as ${fileName}`);
        });
    }).on('error', (err) => {
        fs.unlink(fileName, () => {}); // Delete the file if there's an error
        console.error(`Error downloading image: ${err.message}`);
    });
}

// Get the URL and filename from command-line arguments

const url = 'https://www.uxmatters.com/images/sponsors/UXmattersPatreonBanner.png';
const fileName = 'DELETE_THIS.png';
downloadImage(url, fileName);