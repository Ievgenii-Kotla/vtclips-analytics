"""Do manual request to yt with specified parameters."""
from src.vtc import db_yt_interface
from googleapiclient.discovery import build
import json


def search():
    api_service = db_yt_interface.PrepareAPI(filepath='../state/api_quota_state.json')
    api_key = api_service.get_api_key(delay=False, purpose=db_yt_interface.PrepareAPI.SEARCH)
    youtube = build('youtube', 'v3', developerKey=api_key)
    response = youtube.search().list(
        part='snippet',
        maxResults=50,
        publishedAfter='2024-10-17T21:42:59Z',
        publishedBefore='2024-12-05T09:22:15Z',
        q='"amelia watson"',
        regionCode='US',
        safeSearch='none',
        type='video',
    ).execute()
    api_service.change_quota(api_key, -100)
    quota_left = api_service.get_quota_left(api_key)
    print("Quota left: ", quota_left)
    print(json.dumps(response, indent=4))


def channels_list():
    api_service = db_yt_interface.PrepareAPI(filepath='../state/api_quota_state.json')
    api_key = api_service.get_api_key(delay=False, purpose=db_yt_interface.PrepareAPI.SEARCH)
    youtube = build('youtube', 'v3', developerKey=api_key)
    response = youtube.channels().list(
        part='brandingSettings,content'
             'Details,contentOwnerDetails,id,localizations,snippet,statistics,status,topicDetails',
        id='UCmbs8T6MWqUHP1tIQvSgKrg'
    ).execute()
    api_service.change_quota(api_key, -1)
    quota_left = api_service.get_quota_left(api_key)
    print("Quota left: ", quota_left)
    print(json.dumps(response, indent=4))


def videos_list():
    api_service = db_yt_interface.PrepareAPI(filepath='../state/api_quota_state.json')
    api_key = api_service.get_api_key(delay=False, purpose=db_yt_interface.PrepareAPI.SEARCH)
    youtube = build('youtube', 'v3', developerKey=api_key)
    response = youtube.videos().list(
        part='contentDetails,id,liveStreamingDetails,localizations,paidProductPlacementDetails,player,'
             'recordingDetails,snippet,statistics,status,topicDetails',
        id='bxRO2BIlmEg'


    ).execute()
    api_service.change_quota(api_key, -1)
    quota_left = api_service.get_quota_left(api_key)
    print("Quota left: ", quota_left)
    print(json.dumps(response, indent=4))


def search_channel_videos():
    api_service = db_yt_interface.PrepareAPI(filepath='../state/api_quota_state.json')
    api_key = api_service.get_api_key(delay=False, purpose=db_yt_interface.PrepareAPI.SEARCH)
    youtube = build('youtube', 'v3', developerKey=api_key)
    response = youtube.search().list(
        part='snippet',
        channelId='UCmbs8T6MWqUHP1tIQvSgKrg',
        maxResults=50,
        # publishedAfter='2020-07-12T00:00:00Z',
        # publishedBefore='2020-07-24T23:59:59Z',
        #q='DG_2g04HDl8',
        regionCode='US',
        safeSearch='none',
        type='video',
    ).execute()
    api_service.change_quota(api_key, -100)
    quota_left = api_service.get_quota_left(api_key)
    print("Quota left: ", quota_left)
    print(json.dumps(response, indent=4))


def playlist_items():
    # Ouro Kronii example playlist ID: UUmbs8T6MWqUHP1tIQvSgKrg
    # Nerrev example playlist ID: UUUY4NGgaom5tDxhe4b1YX0g
    # bugged azki one: UU0TXe_LYZ4scaW2XMyi5_kw
    #  next page token for it: EAAaHlBUOkNHUWlFRGhCTWpCQ1FUSkdPVU0xTmpNMU9UVQ
    api_service = db_yt_interface.PrepareAPI(filepath='../state/api_quota_state.json')
    api_key = api_service.get_api_key(delay=False, purpose=db_yt_interface.PrepareAPI.SEARCH)
    youtube = build('youtube', 'v3', developerKey=api_key)
    response = youtube.playlistItems().list(
        part='snippet,status,id,contentDetails',
        maxResults=50,
        playlistId='UU0TXe_LYZ4scaW2XMyi5_kw',
        pageToken='EAAaHlBUOkNHUWlFRGhCTWpCQ1FUSkdPVU0xTmpNMU9UVQ'
    ).execute()
    api_service.change_quota(api_key, -1)
    quota_left = api_service.get_quota_left(api_key)
    print("Quota left: ", quota_left)
    print(json.dumps(response, indent=4))


def main():
    if 1:
        search()
    if 0:
        channels_list()
    if 0:
        videos_list()
    if 0:
        search_channel_videos()
    if 0:
        playlist_items()


if __name__ == '__main__':
    main()