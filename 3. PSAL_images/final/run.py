import subprocess
import json
from helper import divide_chunks
from time import sleep

# Load the list of websites
with open('websites.json', 'r') as f:
    websites = json.load(f)

SIZE = 2
chunks = list(divide_chunks(websites, SIZE))

for chunk in chunks:
    chunk_str = json.dumps(chunk)
    process = subprocess.Popen(['python3', 'image_breakages.py', chunk_str])
    process.wait()  # Wait for the subprocess to finish before continuing
    sleep(5)  # Add a delay if needed between subprocesses
