import requests
import json
import time
import datetime
import timing
import pandas as pd

def pad(seq, target_len, padding=None):
    seq_len = len(seq)
    seq.extend([padding] * (target_len - seq_len))
    return seq

def json_parse(x):
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

        video_result = pad(video_result, 9)
    return video_result

def api_call(vid_query, results, API_KEY):
    response = requests.get('https://www.googleapis.com/youtube/v3/videos?part=id%2C' +
                            '+snippet%2C+contentDetails%2C+statistics' +
                            '&id=' + vid_query + '&maxResults=' + str(results) +
                            '&fields=items(contentDetails%2Fduration%2Cid%2Csnippet' +
                            '(channelTitle%2CpublishedAt%2Ctitle)%2Cstatistics)&key=' + API_KEY)

    vid_stats = json.loads(response.content)
    response.close()
    return vid_stats

def df_transform(df):
    num_columns = ['Likes', 'Dislikes', 'Comments', 'Views']
    for x in num_columns:
        df[x] = pd.to_numeric(df[x])

    df['Engagement'] = (df['Likes'] + df['Dislikes'] + df['Comments']) / df['Views']
    df['Like_Ratio'] = df['Likes'] / (df['Likes'] + df['Dislikes'])
    df['Controversy'] = df['Comments'] / df['Views']

    return df

def stat_get(channel, request_type):
    id_counter = -1
    row_counter = 0

    video_ids = pd.read_csv('vid_id/' + channel + '-videoIDs.csv', squeeze=True).tolist()
    vid_df = pd.DataFrame(columns=['Vid_ID', 'Published', 'Channel', 'Video', 'Duration',
                                   'Views', 'Likes', 'Dislikes', 'Comments'])

    if request_type == '2':
        video_ids = video_ids[0:25]

    vid_num = len(video_ids)
    page_num = (vid_num // 50) + 1

    for page in range(page_num):
        if (vid_num - id_counter) > 50:
            vid_query = '%2C+'.join(video_ids[id_counter + 1: id_counter + 51])
            results = 50
        elif (vid_num - id_counter) < 50:
            vid_query = '%2C+'.join(video_ids[id_counter + 1:])
            results = len(video_ids[id_counter + 1:])

        vid_stats = api_call(vid_query, results, API_KEY)

        for vid in vid_stats['items']:
            video_result = json_parse(vid)
            vid_df.loc[row_counter] = video_result
            row_counter += 1

        id_counter += results
        print('Grabbing stats from ' + channel + ' (' + str(page + 1) + '/' + str(page_num) + ')')

    out_df = df_transform(vid_df)
    out_df.to_csv('output/' + timestamp + channel + '-stats.csv', encoding='utf8', index=False)

def stat_request():
    channels = []
    request = str(input('1 - All statistics | 2 - Recent statistics: '))
    [stat_get(i, request) for i in channels]  # gets stats for every channel listed in 'channels'

keyGet = open('Key.txt', 'r')
API_KEY = keyGet.read()
time_now = time.time()
timestamp = datetime.datetime.fromtimestamp(time_now).strftime('%m-%d--%H-%M--')

stat_request()
