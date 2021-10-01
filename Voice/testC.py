import urllib.request
from bs4 import BeautifulSoup


# urlData = "http://www.youtube.com/watch?v=KQEOBZLx-Z8"
# webUrl = urllib.request.urlopen(urlData)

soup = BeautifulSoup(urllib.request.urlopen('https://www.youtube.com/watch?v=i_5xPDX-erE').read().decode("utf-8"), features="lxml")

# test = urllib.request.urlopen('http://www.youtube.com/watch?v=KQEOBZLx-Z8').read().decode("utf-8")

# print(soup)

print(str(soup.title)[7:-8])