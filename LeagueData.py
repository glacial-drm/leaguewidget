import os, requests, json
import urllib.request
import Database
from dotenv import load_dotenv

class LeagueData:
    __api_key = ""
    
    __puuid = ""    
    
    __urls, __posts = {}, {} # store any relevant dicts in the database ----------------
    
    def __init__(self):
        load_dotenv(override=False)
        self.__api_key = os.getenv("API_KEY")

        self.__db = Database.LeagueDB()

    def create_user(self, discordID: str, gamename: str, tagline: str):

        if(self.__db.find_user_by_discordID(discordID)): # if user's discordID exists in database
            return f"A riot account is already linked to this discord account. Try the update or delete commands, or help for more info"
        else:
            self.link_riot_to_discordID(discordID, gamename, tagline)

    def link_riot_to_discordID(self, discordID: str, gamename: str, tagline: str):
        
        # Get user's encrypted puuid
            puuid_url = f"https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{gamename}/{tagline}?api_key={self.__api_key}"
        
            puuid = call(puuid_url)["puuid"]
            
            # Create user
            self.__db.collection.insert_one({
                # Identifiers
                "discordID": discordID,
                "gamename": gamename,
                "tagline": tagline,
                
                # API info
                "puuid": puuid,

                # Displayed stats
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
            
            self.update_user(discordID)

    def update_user(self, discordID:str):

        user = self.__db.find_user_by_discordID(discordID)
        puuid = user["puuid"]

        newValues = {"$set": {
                
                "favourite-champion": "",
                "top-champion": self.get_top_champ_name(puuid),
                "top-mastery": "",
                "total-mastery": self.get_total_mastery(puuid),

                "rank-solo-duo": "",
                "rank-flex": "",

                "time-played": "",
                "games-played": "",
                "games-won": ""
        }}
        
        self.__db.collection.update_one({"discordID": user["discordID"]}, newValues)
        


    def get_time_played(self): # make sure it's in ms
        pass

    def get_total_games_won(self):
        pass

    def get_total_games_played(self):
        pass



    def get_rank_flex(self):
        pass

    def get_rank_solo_duo_(self):
        pass
    


    def get_total_mastery(self, puuid: str):
        masteryUrl = f"https://euw1.api.riotgames.com/lol/champion-mastery/v4/scores/by-puuid/{puuid}?api_key={self.__api_key}"
        
        totalMastery = call(masteryUrl)
        
        return totalMastery

    def get_top_champ_mastery(self, puuid: str):
        topMasteryURL = f"https://euw1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}?api_key={self.__api_key}"
        
        topChampion = call(topMasteryURL)[0]
        # mastery = str(topChampion["mastery"])
        
        # return mastery
    
    def get_top_champ_name(self, puuid: str):
        
        top_champ_id = self.get_top_champ_id(puuid)
        
        return self.champ_id_to_name(top_champ_id)    
    
    def get_top_champ_id(self, puuid: str):
        
        topMasteryURL = f"https://euw1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}?api_key={self.__api_key}"
        
        topChampion = call(topMasteryURL)[0]
        id = str(topChampion["championId"])
        
        return id
    
    def champ_id_to_name(self, id: str):
        
        championsURL, champ_json, name = "", "", ""
        
        try:
            with urllib.request.urlopen("https://ddragon.leagueoflegends.com/api/versions.json") as version_url:
                
                league_version = json.loads(version_url.read().decode())[0] # latest version
                
                championsURL = f"https://ddragon.leagueoflegends.com/cdn/{league_version}/data/en_US/champion.json"
        except:
            print('Exception: failed to load latest version of league')

        try:
            with urllib.request.urlopen(championsURL) as champ_url:
            
                champ_json = json.loads(champ_url.read().decode())["data"]
        except:
            print('Exception: failed to load champ json data')

        name = next(champ for champ in champ_json if champ_json[champ]["key"] == id)
        return name


def call(url: str):

    try:
        response = requests.get(url)

        if response.status_code == 200:
            posts = response.json()
            return posts
        else:
            print('Error:', response.status_code)
            return None
    except requests.exceptions.RequestException as e:
        
        print('Exception:', e)
        return None

    
x = LeagueData()
x.create_user("414120508632596482","Glacial", "zelda")
