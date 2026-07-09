from pymongo import MongoClient


class LeagueDB: # store data with respect to users discord id

    def __init__(self):
        self.client = MongoClient("mongodb://localhost:27017/")
        self.database =  self.client["LeagueWidgetDB"]
        self.collection = self.database['users']

    def create_user(self, discordID: str, gamename: str, tagline: str):

        if(self.find_user_by_discordID(discordID)):
            return f"You have already linked a riot account. Try the update or delete commands, or help for more info"
        else:
            self.collection.insert_one({
                "discordID": discordID,
                "gamename": gamename,
                "tagline": tagline,
                
                # Other stats
                "favourite-champion": "",
                "top-champion": "",
                "top-mastery": "",
                "total-mastery": "",

                "rank-solo-duo": "",
                "rank-flex": "",

                "time-played": "",
                "games-played": "",
                "games-won": ""
                })


    def find_user_by_discordID(self, discordID: str):
        
        try:
            user = next(user for user in self.collection.find({"discordID": discordID}))
        except Exception as e:
            print(f"Exception: user not found. {e}")
            return None
        return user
    
# db = LeagueDB()
# db.collection.insert_one({"discordID": "1234"})
# print(db.find_user_by_discordID("124"))
# db.create_user("1", "1", "1")