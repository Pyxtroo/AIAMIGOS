import pymongo
from pprint import pprint
from Google import Create_Service
from PIL import Image
import io
import re
from datetime import datetime, timedelta
import wget
import os
from azure.storage.blob import ContentSettings, BlobServiceClient
from pytube import YouTube
import os

d = datetime.today() - timedelta(days=1)
d = d.strftime('%Y-%m-%dT%H:%M:%SZ')
destination = r"C:\Users\Administrator\Desktop\AIAMIGOS\img"

CLIENT_SECRET_FILE = 'client-secret.json'
API_NAME = 'youtube'
API_VERSION = 'v3'
SCOPES = ['https://www.googleapis.com/auth/youtube']

service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)

CONNECTION_STRING = 'mongodb://mongodbaiamigos:aAp4MwYdF2IO6szxszck2VWIFLabFnvmDwhNe2IuxxlgG6PrPrj2cJ0kpAm6bYB9Nkel6GjwtwDFRfahhlxz5Q==@mongodbaiamigos.mongo.cosmos.azure.com:10255/?ssl=true&replicaSet=globaldb&retrywrites=false&maxIdleTimeMS=120000&appName=@mongodbaiamigos@'
client = pymongo.MongoClient(CONNECTION_STRING)
try:
    client.server_info() # validate connection string
except pymongo.errors.ServerSelectionTimeoutError:
    raise TimeoutError("Invalid API for MongoDB connection string or timed out when attempting to connect")

CONFIG = {
    "CONTAINER_NAME": "youtubeContainer",
    "STORAGE_ACCOUNT": "youtubestorage1",
    "STORAGE_KEY": "vgIi0duJjfBfjrFH/ymP5uVelar1uTtDJm8IDANBkqaZeXarwh1Q2X7lepqzeGtgy5xhrRy7FVQm+AStPOMBPg=="
}

block_blob_service = BlobServiceClient.from_connection_string(conn_str = 'DefaultEndpointsProtocol=https;AccountName=blobaiamigos;AccountKey=1j8SSH/W44kpioI3MYbunay9GIIhIWXGnm8gheKOOzHo2PazZCeb+bIfPgIe7QN0eV85wdbfnFdf+AStxwUhDA==;EndpointSuffix=core.windows.net')

db = client['youtubedata']
mycol = db['test01']
imgcol = db['img']

def upload_img_url(img_url , name):
    blob_client = block_blob_service.get_blob_client(container = 'imgcontainer', blob= name)
    with open(img_url, "rb") as data:
        blob_client.upload_blob(data, overwrite=True, content_settings=ContentSettings(content_type='image/jpeg'))
    print("img is uploaded to blob!!")

def upload_vid(name):
    SAVE_PATH = r"C:\Users\Administrator\Desktop\AIAMIGOS\vid"
    link = f"https://www.youtube.com/watch?v={name}"
    img_path = "vid.mp4"
    url = YouTube(link)
    video = url.streams.get_highest_resolution()
    video.download(filename = img_path, output_path = SAVE_PATH)

    blob_client = block_blob_service.get_blob_client(container = 'vidcontainer', blob= name +'.mp4')
    with open(r"C:\Users\Administrator\Desktop\AIAMIGOS\vid\vid.mp4", "rb") as data:
        blob_client.upload_blob(data, overwrite=True, content_settings=ContentSettings(content_type='video/,p4'))
    print("vid is uploaded to blob!!")

    if os.path.exists(r"C:\Users\Administrator\Desktop\AIAMIGOS\vid\vid.mp4"):
        os.remove(r'C:\Users\Administrator\Desktop\AIAMIGOS\vid\vid.mp4')

#DB CRUD

def delete_document(collection, document_id):
    collection.delete_one({"_id": document_id})
    print("Deleted document with _id {}".format(document_id))

def read_document(collection, document_id):
    print("Found a document with _id {}: {}".format(document_id, collection.find_one({"_id": document_id})))

def insert_document(collection, doc):
    document_id = collection.insert_one(doc)
    print("Inserted document with _id {}".format(document_id))
    return document_id

def mybar(current, total, width):
    print('Downloading %d (%d/%d bytes' % (current / total * 100, current, total), end='\r')

def ytsearchnonp(term):
    search = service.search().list(
            part="id",
            type='video',
            maxResults=50,
            order="viewCount",
            publishedAfter=d,
            q=term,
        )
    searchresponse = search.execute()
    return searchresponse

def ytsearchnp(term,np):
    search = service.search().list(
            part="id",
            type='video',
            maxResults=50,
            order="viewCount",
            publishedAfter=d,
            q=term,
            pageToken = np
        )
    searchresponse = search.execute()
    return searchresponse

def videoinfodb(videolist):
    for i in videolist['items']:
        try:
            upload_vid(i['id']['videoId'])
        except:
            pass

        try:
            wget.download('http://img.youtube.com/vi/' + i['id']['videoId'] + '/maxresdefault.jpg', bar=mybar, out=destination)
            f = Image.open(r"C:\Users\Administrator\Desktop\AIAMIGOS\img\maxresdefault.jpg")
            image_bytes = io.BytesIO()
            f.save(image_bytes, format='JPEG')
            image = {
                'data': image_bytes.getvalue()
            }
            insert_document(imgcol ,image)
            upload_img_url(r"C:\Users\Administrator\Desktop\AIAMIGOS\img\maxresdefault.jpg" , i['id']['videoId'])
            os.remove(r"C:\Users\Administrator\Desktop\AIAMIGOS\img\maxresdefault.jpg")
        except:
            pass

        response = service.videos().list(
            part='contentDetails,statistics,snippet',
            id=i['id']['videoId']
    ).execute()
        insert_document(mycol ,response)

def ytscrape(term):
    search = ytsearchnonp(term)
    nextpagetoken = search['nextPageToken']
    videoinfodb(search)
    search = ytsearchnp(term,nextpagetoken)
    nextpagetoken = search['nextPageToken']
    videoinfodb(search)

keywords = ['News', 'Gaming', 'Trailer', 'Movies', 'Review', 'Tutorial', 'DIY', 'Music', 'Animation', 'Animals', 'Art', 'Stocks', 'Cars', 'Tech', 'Ad', 'Sports', 'Event']

for word in keywords:
    ytscrape(word)
