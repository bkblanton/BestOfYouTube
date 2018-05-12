import pathlib
import argparse
import math
import os
import requests
import sys
import urllib.parse

def get_playlist_id_from_url(url):
    values = urllib.parse.parse_qs(urllib.parse.urlsplit(url).query).get('list')
    return values[0] if values is not None else None

def get_video_ids_from_playlist(playlistId, pageToken=None):
    params={
        'key': API_KEY,
        'part': 'contentDetails',
        'playlistId': playlistId,
        'maxResults': 50, # max per page
    }
    if pageToken:
        params['pageToken'] = pageToken
    parsed_response = requests.get('https://www.googleapis.com/youtube/v3/playlistItems', params=params).json()
    video_ids = []
    for item in parsed_response['items']:
        video_ids.append(item['contentDetails']['videoId'])
    if parsed_response.get('nextPageToken'):
        video_ids += get_video_ids_from_playlist(playlistId, pageToken=parsed_response['nextPageToken'])
    return video_ids

def get_videos_from_ids(video_ids):
    params={
        'key': API_KEY,
        'part': 'id,statistics,snippet',
        'id': ','.join(video_ids[:50]),
        'maxResults': 50,
    }
    parsed_response = requests.get('https://www.googleapis.com/youtube/v3/videos', params=params).json()
    videos = parsed_response['items']
    if len(video_ids) > 50:
        videos += get_videos_from_ids(video_ids[50:])
    return videos

def get_videos_from_playlist(playlistId):
    return get_videos_from_ids(get_video_ids_from_playlist(playlistId))

def score(video, consider_views=False):
    statistics = video['statistics']
    views = int(statistics.get('viewCount', 0))
    likes = int(statistics.get('likeCount', 0))
    dislikes = int(statistics.get('dislikeCount', 0))
    # dislikes = max(20, dislikes) # Too much uncertainty when dislikes < 20
    if dislikes == 0:
        return -math.inf
    if consider_views:
        if views == 0:
            return -math.inf
        return likes/dislikes * likes/views
    else:
        return likes/dislikes

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-k', '--key', default=os.getenv('YT_API_KEY'), help='Your YouTube API key. You may also specify this in the "YT_API_KEY" environment variable.')
    parser.add_argument('-v','--videos', action='store_true', help='Show individual videos instead of playlists.')
    parser.add_argument('-n','--num-videos', default=50, type=int, help='Number of top videos to include.')
    parser.add_argument('-V', '--consider-views', action='store_true', help='Also consider likes per view.')
    parser.add_argument('-c','--rebuild-cache', action='store_true', help='Rebuild the playlist video caches.')
    parser.add_argument('-i','--ids', action='store_true', help='Instead of the full URLs, output IDs only.')
    parser.add_argument('-p', '--polymer', action='store_true', help='Allow the new YouTube website for playlists.')
    parser.add_argument('playlist', nargs='+', help='Playlist ID or URL.')
    args = parser.parse_args(sys.argv[1:])
    
    API_KEY = args.key
    if API_KEY is None:
        print('Please set the "YT_API_KEY" environment variable or "-k" argument to your YouTube API key.', file=sys.stderr)
        exit(1)

    videos = []

    cache_directory = pathlib.Path('.cache')

    if not cache_directory.exists():
        cache_directory.mkdir()
    
    for playlist in args.playlist:
        playlist_id = get_playlist_id_from_url(playlist) or playlist
        videos_file_path = pathlib.Path(cache_directory.joinpath(playlist_id))
        if not args.rebuild_cache and videos_file_path.exists():
            with open(videos_file_path) as videos_file:
                videos += eval(videos_file.read())
        else:
            playlist_videos = get_videos_from_playlist(playlist_id)
            with open(videos_file_path, 'w', errors='ignore') as video_file:
                video_file.write(str(playlist_videos))
            videos += playlist_videos
    
    videos = sorted(videos, key=lambda video: score(video, consider_views=args.consider_views), reverse=True)[:args.num_videos]

    if args.videos:
        for video in videos:
            if args.ids:
                print(video['id'])
            else:
                print('https://youtu.be/' + video['id'])
    else:
        MAX_WATCH_VIDEOS = 50
        for i in range(0, len(videos), MAX_WATCH_VIDEOS):
            videos_slice = videos[i:i + MAX_WATCH_VIDEOS] 
            watch_videos_url = 'http://www.youtube.com/watch_videos?video_ids=' + ','.join(video['id'] for video in videos_slice)
            watch_url = requests.get(watch_videos_url).url
            output_playlist_id = get_playlist_id_from_url(watch_url)
            if args.ids:
                print(output_playlist_id)
            else:
                print('https://www.youtube.com/playlist?list=' + output_playlist_id + ('&disable_polymer=true' if not args.polymer else ''))
