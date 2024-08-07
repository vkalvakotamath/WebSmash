import requests

# pip install beautifulsoup and wget

from bs4 import BeautifulSoup
import wget
import os


# This is the script I used for fetching cat pictures shut up.
url = 'https://www.reddit.com/r/cats/'
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')



image_links = []
for link in soup.find_all('a'):
    href = link.get('href')
    if href and href.endswith(('.jpg', '.png',)):
        image_links.append(href)

if not os.path.exists('cat_pictures'):
    os.makedirs('cat_pictures')


for i, link in enumerate(image_links[:10]):

    try:

        if not link.startswith('http'):
            link = 'https://www.reddit.com' + link

        filename = f"cat_{i+1}{os.path.splitext(link)[1]}"
        
        print(f"Downloading: {filename}")
        wget.download(link, out=os.path.join('cat_pictures', filename))
        print() 
    except Exception as e:
        print(f"Something went wrong, please try again")

print("CATS! Complete.")