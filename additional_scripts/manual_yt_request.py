"""Do manual request to yt with specified parameters."""
from vtc import db_yt_interface
from googleapiclient.discovery import build
import json


def main():
    api_service = db_yt_interface.PrepareAPI(filepath='../data/api_quota_state.json')
    api_key = api_service.get_api_key(delay=False)
    youtube = build('youtube', 'v3', developerKey=api_key)
    response = youtube.search().list(
        part='snippet',
        maxResults=2,
        publishedAfter='2025-02-01T00:00:00Z',
        publishedBefore='2025-02-02T23:59:59Z',
        q='boat',
        regionCode='US',
        safeSearch='none',
        type='video',
    ).execute()
    api_service.change_quota(api_key, -100)
    quota_left = api_service.get_quota_left(api_key)
    print(quota_left)
    print(json.dumps(response, indent=4))


if __name__ == '__main__':
    main()