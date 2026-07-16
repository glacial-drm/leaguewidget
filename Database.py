from pymongo import MongoClient


class LeagueDB: # store data with respect to users discord id

    def __init__(self):
        self.client = MongoClient("mongodb://localhost:27017/")
        self.database =  self.client["LeagueWidgetDB"]
        self.collection = self.database['users']


    def find_user_by_discordID(self, discordID: str):
        
        try:
            user = next(user for user in self.collection.find({"discordID": discordID}))
        except StopIteration:
            print(f"userID: {discordID} not found in database")
            return -1
        
        return user
    
    def get_field_by_discordID(self, discordID: str, field: str):
        return self.__db.client[discordID][field]
    
    def set_fields(self, discordID: str, path: str, fieldsDict: dict):
        
        for key, value in fieldsDict.items():
            self.collection.update_one(
                {"discordID": discordID},
                {"$set": {f"{path}.{key}": value}})
    
# db = LeagueDB()
# print(db.find_user_by_discordID("141412050863259648224"))