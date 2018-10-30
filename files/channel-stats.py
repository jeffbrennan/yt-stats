import requests
import json
import csv
import time
import datetime
import timing
import pandas as pd
import numpy as np

keyGet = open('Key.txt', 'r')
API_KEY = keyGet.read()
timeNow = time.time()
fileDate = datetime.datetime.fromtimestamp(timeNow).strftime('%m-%d--%H-%M--')
idPath = 'C:/Users/jeffb/Documents/Python/webPrograms/webScraping/yt-stats/IDs/'
outputPath = 'C:/Users/jeffb/Documents/Python/webPrograms/webScraping/yt-stats/output/'

def stat_get(channel, request_type):
    video_ids = pd.read_csv(idPath + channel + '-videoIDs.csv', squeeze=True).tolist()

    id_counter = -1
    statPage_counter = 0

    if request_type == '2':
        video_ids = video_ids[0:25]

    vidnum = len(video_ids)
    pageTotal = (vidnum // 50) + 1

    video_stats = pd.DataFrame(columns=['ID', 'Published_At', 'Channel Title',
                                        'Video Title', 'Duration', 'View_Count',
                                        'Like_Count', 'Dislike_Count', 'Comment_Count'])

    for _ in range(pageTotal):
        if (vidnum - id_counter) > 50:
            video_request = '%2C+'.join(video_ids[id_counter + 1: id_counter + 51])
            results = 50
        elif (vidnum - id_counter) < 50:
            video_request = '%2C+'.join(video_ids[id_counter + 1:])
            results = len(video_ids[id_counter + 1:])

        statGet = requests.get('https://www.googleapis.com/youtube/v3/videos?part=id%2C' +
                               '+snippet%2C+contentDetails%2C+statistics' +
                               '&id=' + video_request + '&maxResults=' + str(results) +
                               '&fields=items(contentDetails%2Fduration%2Cid%2Csnippet' +
                               '(channelTitle%2CpublishedAt%2Ctitle)%2Cstatistics)&key=' + API_KEY)

        statInfo = json.loads(statGet.content)
        statGet.close()

        row_counter = 0
        for x in statInfo['items']:
            try:
                video_result = [x['id'], x['snippet']['publishedAt'],
                                x['snippet']['channelTitle'], x['snippet']['title'],
                                x['contentDetails']['duration'],
                                x['statistics']['viewCount'],
                                x['statistics']['likeCount'],
                                x['statistics']['dislikeCount'],
                                x['statistics']['commentCount']]
            except KeyError:
                print(x['id'] + ': key error')

                video_result = [x['id'], x['snippet']['publishedAt'],
                                x['snippet']['channelTitle'],
                                x['snippet']['title'],
                                x['contentDetails']['duration']]
                pass

            video_stats.loc[row_counter] = video_result
            row_counter += 1

        id_counter = (id_counter + results)
        statPage_counter += 1
        print('Grabbing stats from ' + channel + ' (' + str(statPage_counter) + '/' + str(pageTotal) + ')')

    video_stats.to_csv(outputPath + fileDate + channel + '-stats.csv', encoding='utf8', index=False)

def stat_request():
    channels = ['JRE']
    request = str(input('1 - All statistics | 2 - Recent statistics: '))
    [stat_get(i, request) for i in channels]

stat_request()
