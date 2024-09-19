#!/usr/bin/env python3

import multiprocessing
import subprocess
import os
import sys

NUM_PROCESSES = 4  # Change this to the number of files or processes you want to run

# Path to the Node.js script you want to execute (e.g., driver.mjs)
SCRIPT_PATH = 'driver.mjs'

def divide_chunks(l, n):
    # looping till length l
    for i in range(0, len(l), n):
        yield l[i:i + n]


def is_finished(website, extn):
    


def run_node_script(process_num, adblocker, website):
    """
    This function will run the Node.js script using subprocess.
    """
    print(f"Starting process {process_num}")
    
    # Execute the Node.js script with subprocess
    try:
        result = subprocess.run(['node', SCRIPT_PATH, adblocker, website], capture_output=True, text=True)
        
        # Print the output or handle as needed
        print(f"Process {process_num} output:\n{result.stdout}")
        print(f"Process {process_num} completed.")
    
    except Exception as e:
        print(f"Process {process_num} encountered an error: {e}")




def main():

    extensions = [
        "control",
        "ublock",
        # "adblock",
        # "privacy-badger",
        # "adguard"
    ]

    websites = [
        "https://wqah.com/",
        "https://linuxtracker.org/,"
        # "https://www.ubuntugeek.com/#google_vignette",
    ]

    chunks = list(divide_chunks(websites, NUM_PROCESSES))
    
    # Start NUM_PROCESSES parallel processes
    for chunk in chunks:
        processes = []
        for i in range(len(chunk)):
            for extn in extensions:
                # Create a multiprocessing process that runs the Node.js script
                p = multiprocessing.Process(target=run_node_script, args=(i, chunk[i], extn))
                processes.append(p)
                p.start()
            
            # Ensure all processes finish execution
            for p in processes:
                p.join()

if __name__ == "__main__":
    main()
