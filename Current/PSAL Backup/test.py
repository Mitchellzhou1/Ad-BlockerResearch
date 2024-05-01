import requests


def get_final_url(url):
    try:
        response = requests.head(url, allow_redirects=True, timeout=4)
        final_url = response.url
        return final_url
    except Exception as e:
        print(e)
        return url


def compare_urls(url1, url2):
    final_url1 = get_final_url(url1)
    final_url2 = get_final_url(url2)

    return final_url1 == final_url2


url1 = "http://www.teamusa.org"
url2 = "https://tweetsy.io/"

result = compare_urls(url1, url2)
print(result)
