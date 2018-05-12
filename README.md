# Best of YouTube
Given a YouTube playlist, this Python 3 script generates a new playlist of the best videos, unaffected by video popularity.

## Usage
### Example
```
$ python bestof.py "https://www.youtube.com/watch?v=GAPqEAWW9lc&list=PU6nSFpj9HTCZ5t-N3Rm3-HA"
https://www.youtube.com/playlist?list=TLGGwGS6wazU5oswODA1MjAxOA&disable_polymer=true
```
### Options
```
usage: bestof.py [-h] [-k KEY] [-v] [-t] [-n NUM_VIDEOS] [-V] [-c] [-i] [-p]
                 playlist [playlist ...]

positional arguments:
  playlist              Playlist ID or URL.

optional arguments:
  -h, --help            show this help message and exit
  -k KEY, --key KEY     Your YouTube API key. You may also specify this in the
                        "YT_API_KEY" environment variable.
  -v, --videos          Show individual videos instead of playlists.
  -t, --video-titles    Show video titles.
  -n NUM_VIDEOS, --num-videos NUM_VIDEOS
                        Number of top videos to include.
  -V, --consider-views  Also consider likes per view.
  -c, --rebuild-cache   Rebuild the playlist video caches.
  -i, --ids             Instead of the full URLs, output IDs only.
  -p, --polymer         Allow the new YouTube website for playlists.
```

## Installing Requirements
```
pip install -r requirements.txt
```

## Obtaining a YouTube API key
1. Visit the Google Cloud console.
2. Create a new project.
3. Enable **YouTube Data API v3** for your project.
4. Create a new API key credential.
