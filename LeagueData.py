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

    def discordID_to_discordJSON(self, discordID: str):
        
        user = self.__db.find_user_by_discordID(discordID)
        
        # Image elements

        json = {
        "data": {
            "dynamic": [
            {
                "type": 1,
                "name": "gamename#tagline",
                "value": f"{user['gamename']}#{user['tagline']}"
            },
            {
                "type": 1,
                "name": "rank-solo-duo",
                "value": f"{user['rank-solo-duo']}"
            },
            {
                "type": 3,
                "name": "img-solo-duo",
                "value": {
                "url": "https://raw.communitydragon.org/14.10/plugins/rcp-fe-lol-static-assets/global/default/images/ranked-emblem/emblem-bronze.png"
                }
            },
            {
                "type": 3,
                "name": "champ-image",
                "value": {
                "url": f"https://ddragon.leagueoflegends.com/cdn/img/champion/loading/{user['favourite-champion']}_{user['skinID-favourite-champion']}.jpg"
                }
            },
            {
                "type": 1,
                "name": "top-champion",
                "value": f"{user['top-champion']}"
            },
            {
                "type": 3,
                "name": "img-top-champion",
                "value": {
                "url": f"https://ddragon.leagueoflegends.com/cdn/16.13.1/img/champion/{user['top-champion']}.png"
                }
            },
            {
                "type": 1,
                "name": "total-mastery",
                "value": f"{user['total-mastery']}"
            },
            {
                "type": 1,
                "name": "rank-flex",
                "value": f"{user['rank-flex']}"
            },
            {
                "type": 3,
                "name": "img-flex",
                "value": {
                "url": "https://raw.communitydragon.org/14.10/plugins/rcp-fe-lol-static-assets/global/default/images/ranked-emblem/emblem-bronze.png"
                }
            },
            {
                "type": 2,
                "name": "games-won",
                "value": f"{user['games-won']}"
            },
            {
                "type": 2,
                "name": "games-played",
                "value": f"{user['games-played']}"
            },
            {
                "type": 1,
                "name": "summoner-level",
                "value": f"{user['summoner-level']}",
            },
            {
                "type": 1,
                "name": "top-mastery",
                "value": f"{user['top-mastery']}",
            },
            {
                "type": 3,
                "name": "icon-mastery",
                "value": {
                "url": "https://raw.communitydragon.org/14.10/plugins/rcp-fe-lol-static-assets/global/default/images/ranked-emblem/emblem-bronze.png"
                }
            }
            ]
        }
        }

        return json

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
                "puuid": puuid
                })
            
            self.update_user(discordID)

    def update_user(self, discordID:str):

        user = self.__db.find_user_by_discordID(discordID)
        puuid = user["puuid"]

        newValues = {"$set": {
                # Displayed stats
                "top-champion": self.get_top_champ_name(puuid),
                "top-mastery": self.get_top_champ_mastery(puuid),
                "total-mastery": self.get_total_mastery(puuid),

                "rank-solo-duo": self.get_rank_solo_duo(puuid),
                "rank-flex": self.get_rank_flex(puuid),

                "summoner-level": self.get_summoner_level(puuid),
                "games-played": self.get_total_games_played(puuid),
                "games-won": self.get_total_games_won(puuid)
        }}
        
        self.__db.collection.update_one({"discordID": user["discordID"]}, newValues)
        
    

    def get_champion_skin_list(self, championName):
        
        championUrl = f"https://ddragon.leagueoflegends.com/cdn/16.13.1/data/en_US/champion/{championName}.json"

        try:
            championSkins = [(skin['num'], skin['name']) for skin in call(championUrl)['data'][championName]['skins'] if "(" not in skin["name"]]
        except:
            print(f"Error: Champion name not found (skin search)")
            return None

        return championSkins

    def set_favourite_champion(self, discordID: str, championName: str, skinID: str):
        user = self.__db.find_user_by_discordID(discordID)

        newValues = {"$set": {
                # Displayed stats
                "favourite-champion": championName,
                "skinID-favourite-champion": skinID
        }}
        
        self.__db.collection.update_one({"discordID": user["discordID"]}, newValues)

    def get_summoner_level(self, puuid: str): # make sure it's in ms
        summonerURL = f"https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}?api_key={self.__api_key}"

        summoner = call(summonerURL)

        return summoner["summonerLevel"]

    def get_total_games_won(self, puuid: str):
        rankURL = f"https://euw1.api.riotgames.com/lol/league/v4/entries/by-puuid/{puuid}?api_key={self.__api_key}"
        gamesWon = 0

        try:
            soloDuo = next(queue for queue in call(rankURL) if queue["queueType"] == "RANKED_SOLO_5x5")
            
            gamesWon += soloDuo["wins"]
        except:
            pass

        try:
            flex = next(queue for queue in call(rankURL) if queue["queueType"] == "RANKED_FLEX_SR")
            
            gamesWon += flex["wins"]
        except:
            pass

        return str(gamesWon)

    def get_total_games_played(self, puuid: str):
        rankURL = f"https://euw1.api.riotgames.com/lol/league/v4/entries/by-puuid/{puuid}?api_key={self.__api_key}"
        gamesPlayed = 0

        try:
            soloDuo = next(queue for queue in call(rankURL) if queue["queueType"] == "RANKED_SOLO_5x5")
            
            gamesPlayed += soloDuo["wins"]
            gamesPlayed += soloDuo["losses"]
        except:
            pass

        try:
            flex = next(queue for queue in call(rankURL) if queue["queueType"] == "RANKED_FLEX_SR")
            
            gamesPlayed += flex["wins"]
            gamesPlayed += flex["losses"]
        except:
            pass

        return str(gamesPlayed)



    def get_rank_flex(self, puuid: str):
        rankURL = f"https://euw1.api.riotgames.com/lol/league/v4/entries/by-puuid/{puuid}?api_key={self.__api_key}"
        flex = None

        try:
            flex = next(queue for queue in call(rankURL) if queue["queueType"] == "RANKED_FLEX_SR")
        except:
            return(f"Unranked")
        
        
        return f"{flex['tier']} {flex['rank']}"

    def get_rank_solo_duo(self, puuid: str):
        rankURL = f"https://euw1.api.riotgames.com/lol/league/v4/entries/by-puuid/{puuid}?api_key={self.__api_key}"
        solo_duo = None

        try:
            solo_duo = next(queue for queue in call(rankURL) if queue["queueType"] == "RANKED_SOLO_5x5")
        except:
            return(f"Unranked")
        
        return f"{solo_duo['tier']} {solo_duo['rank']}"
    


    def get_total_mastery(self, puuid: str):
        masteryUrl = f"https://euw1.api.riotgames.com/lol/champion-mastery/v4/scores/by-puuid/{puuid}?api_key={self.__api_key}"
        
        totalMastery = call(masteryUrl)
        
        return totalMastery

    def get_top_champ_mastery(self, puuid: str):
        
        topMasteryURL = f"https://euw1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}/top?count=1&api_key={self.__api_key}"
        
        topChampion = call(topMasteryURL)[0]
        mastery = str(topChampion["championLevel"])
        
        return mastery
    
    def get_top_champ_name(self, puuid: str):
        
        top_champ_id = self.get_top_champ_id(puuid)
        
        return self.champ_id_to_name(top_champ_id)    
    
    def get_top_champ_id(self, puuid: str):
        
        topMasteryURL = f"https://euw1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}?api_key={self.__api_key}"
        
        topChampion = call(topMasteryURL)[0]
        id = str(topChampion["championId"])
        
        return id
    
    def champ_id_to_name(self, champId: str):
        
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

        name = next(champ for champ in champ_json if champ_json[champ]["key"] == champId)
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
x.create_user("414120508632596482", "Glacial", "Zelda")
print(x.get_champion_skin_list("Gwen"))
x.set_favourite_champion("414120508632596482", 'Gwen', '11')
# x.discordID_to_JSON("414120508632596482")
