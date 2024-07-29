// Assuming current_url and current_url2 are defined elsewhere in your code

// Parse the URLs\

current_url = 'https://www.awwwards.com/sites/stillstrom-by-maersk';

current_url2 = 'https://www.awwwards.com/sites/stillstrom-by-maersk#';

const parsedUrl1 = new URL(current_url);
const parsedUrl2 = new URL(current_url2);

// Compare the href properties of the two URL objects
if (parsedUrl1.href !== parsedUrl2.href) {
  console.log(parsedUrl1.href)
  console.log("Diff");
  return true; // Return true if the URLs are different
} else {
  console.log("SAME")
  return false; // Return false if the URLs are the same
}
