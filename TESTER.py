from difflib import ndiff

# Function to read HTML content from files
def read_html_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

# Function to find added elements in the after source code compared to before source code
def find_added_elements(before_html, after_html):
    diffs = ndiff(before_html.splitlines(keepends=True), after_html.splitlines(keepends=True))
    added_elements = [line[2:] for line in diffs if line.startswith('+ ') and line[2:].strip()]
    return added_elements

# File paths for before and after HTML files
before_file_path = 'initial'
after_file_path = 'after'

# Read HTML content from files
before_source = read_html_from_file(before_file_path)
after_source = read_html_from_file(after_file_path)

# Find and print the added elements in the after source code compared to the before source code
added_elements = find_added_elements(before_source, after_source)
if added_elements:
    print("Added Elements:")
    for element in added_elements:
        print(element)
else:
    print("No added elements found.")
