import requests
import json
import timing
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pandas as pd

# Creates the selenium driver used to query youtube
def selenium_gen():
    chrome_path = r"C:\Users\jeffb\Anaconda3\Scripts\chromedriver.exe"
    options = Options()
    options.add_argument('--headless')  # suppresses the browser from opening
    options.add_argument('--disable-gpu')
    options.add_argument("--log-level=3")  # supresses console errors
    driver = webdriver.Chrome(chrome_path, chrome_options=options)

    return driver

def uploads_get(query, API_KEY):
    print('Getting channel ID...')

    driver = selenium_gen()
    driver.get('https://www.youtube.com/results?search_query=' + query)

    username = driver.find_element_by_xpath('//*[@id="byline"]/a').get_attribute('href')
    username = username.split('/')[4]
    driver.quit()

    # When first result link contains the channel ID
    if username[0:2] == 'UC' and len(username) == 24:
        upload_ID = username.replace('UC', 'UU')

    # when the first result link contains the plain username
    else:
        id_fetch = requests.get('https://www.googleapis.com/youtube/v3/channels?part='
                                'id&forUsername=' + username + '&key=' + API_KEY)

        id_response = json.loads(id_fetch.content)
        id_fetch.close

        channelID = id_response['items'][0]['id']
        upload_ID = channelID.replace('UC', 'UU')

    print('Channel Upload ID found: ' + upload_ID)
    return(upload_ID)

# Get number total number of video results for page counting
def vid_num_get(channelUploads, API_KEY):
    response = requests.get('https://www.googleapis.com/youtube/v3/playlistItems?part=contentDetails&maxResults=2' +
                            '&playlistId=' + channelUploads + '&fields=pageInfo%2FtotalResults&key=' + API_KEY)

    result = json.loads(response.content)
    response.close()
    video_count = result['pageInfo']
    vid_num = video_count['totalResults']

    page_total = (vid_num // 50) + 1
    return page_total

# Get all video IDs from the selected channel
def vid_ID_get(uploads, pages, channel, API_KEY):
    nextPage = ''
    pageCount = 0
    videos = []
    for _ in range(pages):
        response = requests.get('https://www.googleapis.com/youtube/v3/playlistItems?part=contentDetails&' +
                                'maxResults=50&pageToken=' + nextPage + '&playlistId=' + uploads +
                                '&fields=items%2FcontentDetails%2FvideoId%2CnextPageToken&key=' + API_KEY)
        try:
            result = json.loads(response.content)
            response.close()
            returnedVideos = result['items']

            for video in returnedVideos:
                videos.append(video['contentDetails']['videoId'])

            nextPage = result['nextPageToken']
            pageCount += 1
            print('Grabbing Video IDs from ' + channel + ' (' + str(pageCount) + '/' + str(pages) + ')')

        # triggers when loop reaches last valid video id [partial pages]
        except KeyError:
            pageCount += 1
            print('Grabbing Video IDs from ' + channel + ' (' + str(pageCount) + '/' + str(pages) + ')')

    video_list = pd.Series(videos)
    return video_list

def main():
    key = open('Key.txt', 'r')
    API_KEY = key.read()

    channel = input('Enter name of channel: ')

    uploads = uploads_get(channel, API_KEY)
    pages = vid_num_get(uploads, API_KEY)
    video_list = vid_ID_get(uploads, pages, channel, API_KEY)

    video_list.to_csv('vid_id/' + channel + '-videoIDs-test.csv', encoding='utf-8', index=False)

if __name__ == '__main__':
    main()
