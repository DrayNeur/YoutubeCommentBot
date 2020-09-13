from urllib.request import urlopen
import os
import re
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import time

CLIENT_SECRET_FILE = 'client_secret.json'
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']

def authorization():
  flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
  credentials = flow.run_console()
  youtube = build('youtube', 'v3', credentials=credentials)
  return youtube


def insert_comment(youtube, channel_id, video_id, text):
    insert_result = youtube.commentThreads().insert(
        part="snippet",
        body=dict(
            snippet=dict(
                channelId=channel_id,
                videoId=video_id,
                topLevelComment=dict(
                    snippet=dict(
                        textOriginal=text)
                )
            )
        )
    ).execute()

    comment = insert_result["snippet"]["topLevelComment"]
    author = comment["snippet"]["authorDisplayName"]
    text = comment["snippet"]["textDisplay"]
    print("Success comment (%s): %s" % (author, text))


def findChannelId(videoID):
  html = urlopen("https://www.youtube.com/watch?v=" + videoID)
  text = html.read()
  plaintext = text.decode('utf8')
  links = re.findall("href=[\"\'](.*?)[\"\']", plaintext)
  channelid = ""
  for link in links:
    if link.startswith("http://www.youtube.com/channel/"):
      channelid = link.replace('http://www.youtube.com/channel/', '')
      continue
  return channelid


def search_by_keyword(youtube, query):
  search_response = youtube.search().list(
    q=query.replace(' ', '+'),
    part="id,snippet",
    maxResults=25
  ).execute()

  videos = []

  for search_result in search_response.get("items", []):
    if search_result["id"]["kind"] == "youtube#video":
      videos.append("%s" % (search_result["id"]["videoId"]))
  return videos


if __name__ == "__main__":
  os.system("clear")
  auth = authorization()
  while 1:
    time.sleep(1,5)
    videos = search_by_keyword(auth, "KERWORDS_HERE")
    for video in videos:
      channelid = findChannelId(video)
      print("\n____")
      print("Video id:", video)
      print("Channel ID:", channelid)
      insert_comment(auth, channelid, video, "COMMENT_HERE")
      print("____")
      time.sleep(1)