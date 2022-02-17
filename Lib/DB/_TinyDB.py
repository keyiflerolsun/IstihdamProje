# Bu araç @keyiflerolsun tarafından | @KekikAkademi için yazılmıştır.
 
from tinydb import TinyDB, Query
from tinydb.operations import delete, add
from tinydb.queries import QueryLike

class FlaskAPIDB:
    def __init__(self):
        TinyDB.default_table_name = self.__class__.__name__
        self.db    = TinyDB("ISTIHDAM_DB.json", ensure_ascii=False, indent=2, sort_keys=False)
        self.sorgu = Query()

    def ara(self, sorgu:QueryLike):
        arama = self.db.search(sorgu)
        say   = len(arama)
        if say == 1:
            return arama[0]
        elif say > 1:
            cursor = arama
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

        if (not self.ara(self.sorgu.company == data["company"])):
            return self.db.insert(data)
        else:
            return self.guncelle(data)

    def data_ver(self, company:str):
        return self.ara(self.sorgu.company == company)

    @property
    def sirketler(self):
        return list(self.ara(self.sorgu.company.exists()).keys())

    def guncelle(self, data:dict):
        if "company" not in data.keys():
            return None

        company = self.ara(self.sorgu.company == data["company"])
        if not company:
            return None
        
        return self.db.update(data, self.sorgu.company == data["company"])