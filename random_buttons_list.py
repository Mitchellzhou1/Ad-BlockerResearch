import csv

def initialize_csv_file():
    filename = "website_data.csv"
    fieldnames = ["Website Name", "HTML Content"]

    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

    print(f"CSV file '{filename}' initialized with headers successfully.")

def add_to_csv(website_name, html_content, HTML_obj):
    filename = f"{HTML_obj}.csv"
    object = f"{HTML_obj} HTML Content"
    fieldnames = ["Website Name", "HTML"]

    data = {"Website Name": website_name, "HTML": html_content}

    with open(filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        # Write data rows
        writer.writerow(data)

    print("Added Elem")
# Initialize the CSV file with headers if it doesn't exist
initialize_csv_file()

# Example usage:
website_name_1 = "ExampleWebsite1"
html_content_1 = "<html><body><h1>Hello from ExampleWebsite1!</h1></body></html>"
add_to_csv(website_name_1, html_content_1, "buttons")

website_name_2 = "ExampleWebsite2"
html_content_2 = "<html><body><h1>Hello from ExampleWebsite2!</h1></body></html>"
add_to_csv(website_name_2, html_content_2, "buttons")
