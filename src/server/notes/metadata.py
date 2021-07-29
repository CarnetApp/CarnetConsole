import json

class Metadata():

    

    def __init__(self):
        self.creation_date = -1
        self.last_modification_date = -1
        self.keywords = []
        self.rating = -1
        self.color = "none"
        self.urls = {}
        self.todolists = []

    def fromString(self, metadata_str):
        #todo
        jsonObj = json.loads(metadata_str)
        creation_date = jsonObj['creation_date']
        last_modification_date = jsonObj['last_modification_date']
        keywords = jsonObj['keywords']
        rating = jsonObj['rating']
        color = jsonObj['color']
        urls = jsonObj['urls']
        todolists = jsonObj['todolists']

    def toString(self):
        return json.dumps(self.__dict__)