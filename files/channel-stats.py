import requests, json, csv, time, datetime, timing
keyGet = open('Key.txt', 'r')
API_KEY = keyGet.read()
timeNow = time.time()
fileDate = datetime.datetime.fromtimestamp(timeNow).strftime('%m-%d--%H-%M--')
idPath = 'C:/Users/jeffb/Documents/Python/webPrograms/webScraping/yt-stats/IDs/'
outputPath = 'C:/Users/jeffb/Documents/Python/webPrograms/webScraping/yt-stats/output/'

def allStatGet (channel):
    videos = []

    with open(idPath+channel+'-videoIDs.csv', newline='') as r:
        file = csv.reader(r, delimiter =',')
        for row in file:
            for i in row:
                videos.append(i)

    id_counter = -1
    statPage_counter = 0
    results = 50
    vidnum = len(videos)
    pageTotal = (vidnum // 50) + 1

    with open(outputPath+fileDate+channel+'-stats.csv', 'w', encoding ='utf8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['ID', 'Published_At', 'Channel Title', 'Video Title', 'Duration', 
                        'View_Count', 'Like_Count','Dislike_Count', 'Comment_Count'])

        for _ in range(pageTotal):

            if (vidnum - id_counter) > 50:
                video_ids = '%2C+'.join(videos[id_counter+1:id_counter+51])
            elif (vidnum - id_counter) < 50:
                video_ids = '%2C+'.join(videos[id_counter+1:])
                results = len(videos[id_counter+1:])
            else:
                print ('error catch')
            

            statGet = requests.get('https://www.googleapis.com/youtube/v3/videos?part=id%2C+snippet%2C+contentDetails%2C+statistics'+
                                    '&id='+video_ids+'&maxResults='+str(results)+'&fields=items(contentDetails%2Fduration%2Cid%2Csnippet'+
                                    '(channelTitle%2CpublishedAt%2Ctitle)%2Cstatistics)&key='+API_KEY)

            statInfo = json.loads(statGet.content)
            statGet.close()
        
            for x in statInfo['items']:
                try:
                    writer.writerow(["'"+ x ['id'],
                                x['snippet']['publishedAt'],
                                x['snippet']['channelTitle'],
                                x['snippet']['title'],
                                x['contentDetails']['duration'],
                                x['statistics']['viewCount'],
                                x['statistics']['likeCount'],
                                x['statistics']['dislikeCount'],
                                x['statistics']['commentCount']])
                                
                except KeyError:
                    print (x['id'] + ': key error')
                    writer.writerow(["'" + x['id'],
                                x['snippet']['publishedAt'],
                                x['snippet']['channelTitle'],
                                x['snippet']['title'],
                                x['contentDetails']['duration']])
                    pass

            id_counter = (id_counter + results)
            statPage_counter +=1
            print('Grabbing stats from ' + channel + ' (' +str(statPage_counter)+'/'+str(pageTotal)+')')

def newStatGet (channel):
    videos = []
    x = 0
    with open(idPath+channel+'-videoIDs.csv', newline='') as r:
        file = csv.reader(r, delimiter =',')
        for row in file:
            for i in row:
                videos.append(i)

    id_counter = -1 
    results = 25
    video_ids = '%2C+'.join(videos[0:25])
    
    with open(outputPath+fileDate+channel+'-newstats.csv', 'w', encoding ='utf8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['ID', 'Published_At', 'Channel Title', 'Video Title', 'Duration', 
                        'View_Count', 'Like_Count','Dislike_Count', 'Comment_Count'])            

        statGet = requests.get('https://www.googleapis.com/youtube/v3/videos?part=id%2C+snippet%2C+contentDetails%2C+statistics'+
                                '&id='+video_ids+'&maxResults='+str(results)+'&fields=items(contentDetails%2Fduration%2Cid%2Csnippet'+
                                '(channelTitle%2CpublishedAt%2Ctitle)%2Cstatistics)&key='+API_KEY)

        statInfo = json.loads(statGet.content)
        statGet.close()
    
        for x in statInfo['items']:
            try:
                writer.writerow(["'"+ x ['id'],
                            x['snippet']['publishedAt'],
                            x['snippet']['channelTitle'],
                            x['snippet']['title'],
                            x['contentDetails']['duration'],
                            x['statistics']['viewCount'],
                            x['statistics']['likeCount'],
                            x['statistics']['dislikeCount'],
                            x['statistics']['commentCount']])
                            
            except KeyError:
                print (x['id'] + ': key error')
                writer.writerow(["'" + x['id'],
                                x['snippet']['publishedAt'],
                                x['snippet']['channelTitle'],
                                x['snippet']['title'],
                                x['contentDetails']['duration']])
                pass

            id_counter = (id_counter + results)
    
def regularGet():
    #channels = ['Lyrical-Lemonade', 'Lonewolf', 'WSHH']
    channels = ['Lonewolf']
    for i in channels:
        print ('Grabbing video stats from ' + i)
        newStatGet(i)
def completeGet():
    newChannels = ['Jeffree-Star']  
    
    for i in newChannels:
            allStatGet(i)

regularGet()
#completeGet()