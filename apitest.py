import re
import pymongo
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

CONNECTION_STRING = 'mongodb://mongodbaiamigos:aAp4MwYdF2IO6szxszck2VWIFLabFnvmDwhNe2IuxxlgG6PrPrj2cJ0kpAm6bYB9Nkel6GjwtwDFRfahhlxz5Q==@mongodbaiamigos.mongo.cosmos.azure.com:10255/?ssl=true&replicaSet=globaldb&retrywrites=false&maxIdleTimeMS=120000&appName=@mongodbaiamigos@'
client = pymongo.MongoClient(CONNECTION_STRING)
try:
    client.server_info() # validate connection string
except pymongo.errors.ServerSelectionTimeoutError:
    raise TimeoutError("Invalid API for MongoDB connection string or timed out when attempting to connect")

db = client['youtubedata']
mycol = db['test01']

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

video_by_chart = api.get_videos_by_chart(chart="mostPopular", region_code="NL", count=1)
for i in video_by_chart.items:
    part_string = 'contentDetails,statistics,snippet'
    response = service.videos().list(
	    part=part_string,
	    id=i.id
    ).execute()
    insert_document(mycol ,response)
    pprint(response)
