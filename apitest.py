
from pyyoutube import Api
from pprint import pprint
from Google import Create_Service

key="AIzaSyDt_NYB2bM0gSG2vYUwHBqEcJIIMx-TBy4"
api = Api(api_key=key)
CLIENT_SECRET_FILE = 'client-secret.json'
API_NAME = 'youtube'
API_VERSION = 'v3'
SCOPES = ['https://www.googleapis.com/auth/youtube']

service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)


video_by_chart = api.get_videos_by_chart(chart="mostPopular", region_code="NL", count=10)
for i in video_by_chart.items:
    part_string = 'contentDetails,statistics,snippet'
    response = service.videos().list(
	    part=part_string,
	    id=i.id
    ).execute()
    pprint(response)
