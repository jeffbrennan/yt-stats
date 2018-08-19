import requests, json, csv, time, datetime,timing
from urllib.error import HTTPError, URLError
from bs4 import BeautifulSoup
from urllib import request

keyGet = open('Key.txt', 'r')
API_KEY = keyGet.read()
idPath = 'C:/Users/jeffb/Documents/Python/webPrograms/webScraping/yt-stats/IDs/'

channel_dict = {'WSHH':'UU-yXuc1__OzjwpsJPlxYUCQ', 'Lyrical-Lemonade':'UUtylTUUVIGY_i5afsQYeBZA', 'Lonewolf':'UUtLgQnGkWe74dukALaUNt1Q', \
                'TeamSESH': 'UUmOVEae8Tl7XmdjdxLbJHkw', 'H3H3': 'UULtREJY21xRfCuEKvdki1Kw', 'No-Jumper': 'UUNNTZgxNQuBrhbO0VrG8woA', 'Jeffree-Star': 'UUkvK_5omS-42Ovgah8KRKtg'}
channel = 'Jeffree-Star'
channelUploads = channel_dict[channel]

nextPage = ''
timeNow = time.time()
fileName = datetime.datetime.fromtimestamp(timeNow).strftime('%m_%d_%H_%M_')
videos = []

## Get number of results
inp = requests.get('https://www.googleapis.com/youtube/v3/playlistItems?part=contentDetails&maxResults=2'+
                            '&playlistId='+channelUploads+'&fields=pageInfo%2FtotalResults&key='+API_KEY)
                    
resultData = json.loads(inp.content)
inp.close()
video_count = resultData['pageInfo']
vidnum = video_count['totalResults']

pageTotal = (vidnum//50)+1
pageCount = 0  

for _ in range(pageTotal):
    r = requests.get('https://www.googleapis.com/youtube/v3/playlistItems?part=contentDetails&maxResults=50&pageToken='+nextPage+
                        '&playlistId='+channelUploads+'&fields=items%2FcontentDetails%2FvideoId%2CnextPageToken&key='+API_KEY)
    try:
        data = json.loads(r.content)
        r.close()
        returnedVideos = data['items']
        
        for video in returnedVideos:
            videos.append(video['contentDetails']['videoId'])
            
        nextPage = (data['nextPageToken'])
        pageCount +=1
        print('Grabbing Video IDs from ' + channel + '(' +str(pageCount)+'/'+str(pageTotal)+')')   

    except HTTPError as e:
        print('The server couldn\'t fulfill the request.')
        print('Error code: ', e.code)        
    except URLError as e:
        print('We failed to reach a server.')
        print('Reason: ', e.reason)
    except KeyError as e:
        pageCount +=1
        print('Grabbing Video IDs from ' + channel + '(' +str(pageCount)+'/'+str(pageTotal)+')')   


with open(idPath+channel+'-videoIDs.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    for i in videos:
        writer.writerow([i])