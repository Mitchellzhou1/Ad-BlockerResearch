import os
import subprocess
from time import sleep
import pyperclip


# Change to the home directory
os.chdir('/home/character/go/src/github.com/catapult-project/catapult/web_page_replay_go')


def root_file(site):
    website_root = site.split("://")[1]
    if 'www' in website_root:
        website_root = '_'.join(website_root.split('.')[1:])
    else:
        website_root = '_'.join(website_root.split('.'))

    return website_root


websites = [
        "https://google.com",
        "https://youtube.com",
        "https://facebook.com",
        "https://twitter.com",
        "https://instagram.com",
        "https://baidu.com",
        "https://wikipedia.org",
        "https://amazon.com",
        "https://yahoo.com",
        "https://reddit.com",
        "https://qq.com",
        "https://taobao.com",
        "https://tmall.com",
        "https://live.com",
        "https://vk.com",
        "https://weibo.com",
        "https://sina.com.cn",
        "https://yahoo.co.jp",
        "https://360.cn",
        "https://sohu.com",
        "https://jd.com",
        "https://zoom.us",
        "https://linkedin.com",
        "https://netflix.com",
        "https://twitch.tv",
        "https://office.com",
        "https://microsoft.com",
        "https://pinterest.com",
        "https://ebay.com",
        "https://bing.com",
        "https://pornhub.com",
        "https://whatsapp.com",
        "https://msn.com",
        "https://ok.ru",
        "https://aliexpress.com",
        "https://apple.com",
        "https://bilibili.com",
        "https://yandex.ru",
        "https://imgur.com",
        "https://imdb.com",
        "https://csdn.net",
        "https://tumblr.com",
        "https://fandom.com",
        "https://github.com",
        "https://stackoverflow.com",
        "https://adobe.com",
        "https://spotify.com",
        "https://wordpress.com",
        "https://quora.com",
        "https://cnn.com",
        "https://nytimes.com",
        "https://bbc.com",
        "https://amazon.in",
        "https://mail.ru",
        "https://walmart.com",
        "https://google.com.br",
        "https://etsy.com",
        "https://paypal.com",
        "https://google.co.in",
        "https://bbc.co.uk",
        "https://microsoftonline.com",
        "https://zillow.com",
        "https://weather.com",
        "https://duckduckgo.com",
        "https://buzzfeed.com",
        "https://indeed.com",
        "https://craigslist.org",
        "https://chase.com",
        "https://nih.gov",
        "https://hulu.com",
        "https://dropbox.com",
        "https://bongacams.com",
        "https://google.de",
        "https://t.co",
        "https://salesforce.com",
        "https://roblox.com",
        "https://kickstarter.com",
        "https://espn.com",
        "https://airbnb.com",
        "https://uol.com.br",
        "https://naver.com",
        "https://xvideos.com",
        "https://dominos.com",
        "https://businessinsider.com",
        "https://archive.org",
        "https://forbes.com",
        "https://vimeo.com",
        "https://youporn.com",
        "https://onlyfans.com",
        "https://slideshare.net",
        "https://theguardian.com",
        "https://target.com",
        "https://usatoday.com",
        "https://realtor.com",
        "https://wayfair.com",
        "https://goodreads.com",
        "https://bbc.co.uk",
        "https://merriam-webster.com",
        "https://ign.com",
        "https://dailymotion.com",
        "https://cnet.com",
        "https://news.yahoo.com",
        "https://foxnews.com",
        "https://harvard.edu"
    ]

for site in websites:
    for extn in ['control', 'adblock', 'ublock', 'privacy-badger']:
        site = root_file(site)
        print("Testing", site)
        pyperclip.copy(site)

        start_server = [
            'go', 'run', 'src/wpr.go', 'replay',
            '--http_port=8080',
            '--https_port=8081',
            f'/home/character/archive/{extn}_{site}.wprgo'
        ]
        process1 = subprocess.Popen(start_server, shell=False)
        sleep(2)

        browser = [
                "./chrome_120/chrome",
                "--host-resolver-rules=MAP *:80 127.0.0.1:8080,MAP *:443 127.0.0.1:8081,EXCLUDE localhost",
                "--ignore-certificate-errors-spki-list=PhrPvGIaAMmd29hj8BCZOq096yj7uMpRNHpn5PDxI6I=,2HcXCSKKJS0lEXLQEWhpHUfGuojiU0tiT5gOF9LP6IQ="
        ]

        # Run the command
        process2 = subprocess.Popen(browser, shell=False)

        wait = input("Continue?")

        process1.terminate()
        process2.terminate()
        # os.system('pkill -f java')
        os.system('pkill -f wpr')
exit()

