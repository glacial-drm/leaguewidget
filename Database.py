from pymongo import MongoClient


class LeagueDB: # store data with respect to users discord id

    def __init__(self):
        self.client = MongoClient("mongodb://localhost:27017/")
        self.database =  self.client["LeagueWidgetDB"]
        self.collection = self.database['users']


    def find_user_by_discordID(self, discordID: str):
        
        try:
            user = next(user for user in self.collection.find({"discordID": discordID}))
        except:
            print(f"Exception: userID: {discordID} not found. (database)")
            return None
        return user
    
    def get_field_by_discordID(self, discordID: str, field: str):
        return self.__db.client[discordID][field]
    
# db = LeagueDB()
# db.collection.insert_one({"discordID": "1234"})
# print(db.find_user_by_discordID("124"))
# db.create_user("1", "1", "1")