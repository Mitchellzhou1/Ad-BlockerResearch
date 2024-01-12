import requests

url = "https://www.uxmatters.com/images/sponsors/UXmattersPatreonBanner.png"

response = requests.get(url)

# Print the HTTP request headers
print("HTTP Request Headers:")
for key, value in response.request.headers.items():
    print(f"{key}: {value}")
