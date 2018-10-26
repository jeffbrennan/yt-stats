import requests
import json
import time
import datetime
import timing
from urllib.error import HTTPError, URLError
from bs4 import BeautifulSoup
from urllib import request
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pandas as pd

keyGet = open('Key.txt', 'r')
API_KEY = keyGet.read()

idPath = 'C:/Users/jeffb/Documents/Python/webPrograms/webScraping/yt-stats/IDs/'
fileName = datetime.datetime.fromtimestamp(time.time()).strftime('%m_%d_%H_%M_')

# channel_dict = {'WSHH':'UU-yXuc1__OzjwpsJPlxYUCQ', 'Lyrical-Lemonade':'UUtylTUUVIGY_i5afsQYeBZA',
#                 'Lonewolf':'UUtLgQnGkWe74dukALaUNt1Q', 'TeamSESH': 'UUmOVEae8Tl7XmdjdxLbJHkw',
#                 'H3H3': 'UULtREJY21xRfCuEKvdki1Kw', 'No-Jumper': 'UUNNTZgxNQuBrhbO0VrG8woA',
#                 'Jeffree-Star': 'UUkvK_5omS-42Ovgah8KRKtg', 'JRE' : 'UUzQUP1qoWDoEbmsQxvdjxgQ'}

def channelUploadsGet(query):  # needs bug fixing / testing
    chrome_path = r"C:\Users\jeffb\Anaconda3\Scripts\chromedriver.exe"
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument("--log-level=3")
    driver = webdriver.Chrome(chrome_path, chrome_options=options)

    print('Getting channel ID...')

    driver.get('https://www.youtube.com/results?search_query=' + query)
    videoUrl = driver.find_element_by_xpath('//*[@id="video-title"]').get_attribute('href')
    driver.quit

    r = requests.get(videoUrl)
    soup = BeautifulSoup(r.text, 'html.parser')
    results = soup.findAll('a')

    for link in results:
        if link.has_attr('href') and len(link['href']) == 33:
            channelID = link['href']

    channelID = channelID.replace('/channel/UC', 'UU')

    print('Channel Upload ID found: ' + channelID)
    return(channelID)

# Get number of results
def videoNumGet(channelUploads, API_KEY):
    inp = requests.get('https://www.googleapis.com/youtube/v3/playlistItems?part=contentDetails&maxResults=2' +
                       '&playlistId=' + channelUploads + '&fields=pageInfo%2FtotalResults&key=' + API_KEY)

    resultData = json.loads(inp.content)
    inp.close()
    video_count = resultData['pageInfo']
    vidnum = video_count['totalResults']

    pageTotal = (vidnum // 50) + 1
    return pageTotal

# Get IDs
def videoIDGet(channelUploads, API_KEY, pageTotal):
    nextPage = ''
    pageCount = 0
    videos = []
    for _ in range(pageTotal):
        r = requests.get('https://www.googleapis.com/youtube/v3/playlistItems?part=contentDetails&' +
                         'maxResults=50&pageToken=' + nextPage + '&playlistId=' + channelUploads +
                         '&fields=items%2FcontentDetails%2FvideoId%2CnextPageToken&key=' + API_KEY)
        try:
            data = json.loads(r.content)
            r.close()
            returnedVideos = data['items']

            for video in returnedVideos:
                videos.append(video['contentDetails']['videoId'])

            nextPage = (data['nextPageToken'])
            pageCount += 1
            print('Grabbing Video IDs from ' + channel + ' (' + str(pageCount) + '/' + str(pageTotal) + ')')

        except HTTPError as e:
            print('The server couldn\'t fulfill the request.')
            print('Error code: ', e.code)
        except URLError as e:
            print('We failed to reach a server.')
            print('Reason: ', e.reason)
        except KeyError as e:
            pageCount += 1
            print('Grabbing Video IDs from ' + channel + ' (' + str(pageCount) + '/' + str(pageTotal) + ')')

    return videos

channel = 'H3H3 Productions'
channelUploads = channelUploadsGet(channel)
# channelUploads = 'UULtREJY21xRfCuEKvdki1Kw'
pageTotal = videoNumGet(channelUploads, API_KEY)

videos = videoIDGet(channelUploads, API_KEY, pageTotal)
video_list = pd.Series(videos)

video_list.to_csv(idPath + channel + '-videoIDs.csv', encoding='utf-8', index=False)
