import os
import sys
import requests
import json

def initialize_blacklists():
    """
    Combines all the Black lists into 1 big list
    """
    current_dir = os.path.dirname(os.path.realpath(__file__))
    extensions_dir = os.path.abspath(os.path.join(current_dir, 'blacklists'))

    # Check if extensions_dir exists, if not, create it
    if not os.path.exists(extensions_dir):
        os.makedirs(extensions_dir)

    # URLs for the files to download
    files_urls = {
        "easylist.txt": "https://easylist.to/easylist/easylist.txt",
        "easyprivacy.txt": "https://easylist.to/easylist/easyprivacy.txt",
        "Peter Lowe": "https://pgl.yoyo.org/adservers/serverlist.php"
        # Add the correct file extension if needed, e.g., .txt
    }

    # Iterate over the files and their URLs
    for filename, url in files_urls.items():
        filepath = os.path.join(extensions_dir, filename)

        # Check if file exists
        if not os.path.exists(filepath):
            print(f"Downloading {filename} from {url}")
            try:
                response = requests.get(url)
                response.raise_for_status()  # Raise an HTTP Error for bad responses
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                f.close()
                print(f"Downloaded {filename} successfully.")
            except requests.RequestException as e:
                print(f"Error downloading {filename}: {e}")
        else:
            print(f"{filename} already exists.")


def write_blacklist(website, data):
    path = f'Results/blacklist/{website}.json'
    with open(path, 'w') as f:
        f.write(data)


def main():
    if len(sys.argv) < 2:
        print("Usage: ./wrapper.py {function} {parameters}")
        sys.exit(1)

    # The first argument is the function name
    func_name = sys.argv[1]

    # All subsequent arguments are passed to the function
    func_args = sys.argv[2:]

    try:
        # Get the function by name from the current module
        func = getattr(sys.modules[__name__], func_name)
    except AttributeError:
        print(f"Function '{func_name}' not found")
        sys.exit(1)

    # Call the function with the provided arguments
    func(*func_args)



if __name__ == "__main__":
    main()