# Bu araç @keyiflerolsun tarafından | @KekikAkademi için yazılmıştır.
 
import pymongo

import json
with open("SETTINGS.json", "r+") as dosya:
    MongoDB = json.load(dosya)["MongoDB"]

class FlaskAPIDB:
    def __init__(self):
        client          = pymongo.MongoClient(MongoDB)
        db              = client[self.__class__.__name__]
        self.collection = db["ISTIHDAM_DB"]

    def ara(self, sorgu:dict):
        say = self.collection.count_documents(sorgu)
        if say == 1:
            return self.collection.find_one(sorgu, {'_id': 0})
        elif say > 1:
            cursor = self.collection.find(sorgu, {'_id': 0})
            return {
                bak["company"] : {
                    "wikipedia" : bak["wikipedia"],
                    "indeed"      : bak["indeed"],
                    "glassdoor"      : bak["glassdoor"],
                }
                for bak in cursor
            }
        else:
            return None

    def ekle(self, data:dict):
        if "company" not in data.keys():
            return None

        if not self.ara({'company': {'$in': [data["company"]]}}):
            return self.collection.insert_one(data)
        else:
            return self.guncelle(data)

    def guncelle(self, data:dict):
        if "company" not in data.keys():
            return None

        company = self.ara({'company': {'$in': [data["company"]]}})
        if not company:
            return None

        return self.collection.update_one({'company': {'$in': [data["company"]]}},
            {
                "$set" : data
            }
        )

    def data_ver(self, company:str):
        return self.ara({'company': {'$in': [company]}})

    @property
    def sirketler(self):
        return list(self.ara({'company': {'$exists': True}}).keys())