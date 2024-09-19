import { fileURLToPath } from 'url';
import { dirname } from 'path';
import { spawn, exec } from 'child_process';




const file_extensions = [
    ".js",   //JavaScript
    ".css",  // Cascading Style Sheets
    ".swf",  // Adobe Flash
    ".gif",  // Graphics Interchange Format
    ".jpg",  // Joint Photographic Experts Group
    ".jpeg", // Joint Photographic Experts Group
    ".png",  // Portable Network Graphics
    ".mp4",  // MPEG-4 video file
    ".mp3",  // MPEG Audio Layer III
    ".html", // Hypertext Markup Language
    ".php",  // Hypertext Preprocessor
    ".asp",  // Active Server Pages
    ".aspx", // Active Server Pages
    ".xml",  // Extensible Markup Language
    ".svg",  // Scalable Vector Graphics
    ".woff", // Web Open Font Format
    ".woff2",// # Web Open Font Format 2
    ".ttf",  // TrueType Font
    ".otf",  // OpenType Font
    ".webm", // WebM video file
    ".webp", // WebP image file
    ".ico"   //Icon file
 ]
 

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




class TrieNode {
    constructor() {
      this.children = {};
      this.isEndOfWord = false;
    }
  }
  
class Trie {
    constructor() {
    this.root = new TrieNode();
}
    insert(word) {
    let node = this.root;
    for (let char of word) {
    if (!node.children[char]) {
        node.children[char] = new TrieNode();
    }
    node = node.children[char];
    }
    node.isEndOfWord = true;
}
    search(word) {
    let node = this.root;
    for (let char of word) {
    if (!node.children[char]) return false;
    node = node.children[char];
    }
    return node.isEndOfWord;
}
}
 

export async function initialize_blacklist() {

    const __filename = fileURLToPath(import.meta.url);
    const __dirname = dirname(__filename);
    const blacklist_dir = __dirname + '/blacklists';
    await run_cmd('initialize_blacklists');

    const trie = new Trie();

    const black_lists = ["easylist.txt", "easyprivacy.txt", "Peter Lowe"]

    for (let i = 0 ; i < black_lists.length; i++){
        const fileStream = createReadStream(filePath);
        const rl = readline.createInterface({
            input: fileStream,
            crlfDelay: Infinity
        });

        rl.on('line', (line) => {
            // console.log(`Line: ${line}`);
            if (black_lists[i] == 'easylists.txt'){
                
            }
        });

        rl.on('close', () => {
        console.log('File reading completed.');
        });
    }



      
    
}

