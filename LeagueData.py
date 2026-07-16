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

    def delete_league_data(self, discordID:str):
        
        self.__db.collection.update_one( {'discordID': discordID}, { '$unset': { 'League of Legends': '' } } )


    def discordID_to_discordJSON(self, discordID: str):
        
        riotUser = self.__db.find_user_by_discordID(discordID)["Riot Games"]
        leagueUser = riotUser["League of Legends"]

        # Manipulated elements
        iconMastery = 10 if leagueUser['top-mastery'] > 10 else (0 if leagueUser['top-mastery'] < 4 else leagueUser['top-mastery']) # icons for 1, 2, 3 and above 10 are truncated
        
        soloDuo = self.get_rank_solo_duo(leagueUser["puuid"]).split(" ")[0].lower()
        flex = self.get_rank_flex(leagueUser["puuid"]).split(" ")[0].lower()
        
        # JSON
        json = {
        "data": {
            "dynamic": [
            {
                "type": 1,
                "name": "gamename#tagline",
                "value": f"{riotUser['gamename']}#{riotUser['tagline']}"
            },
            {
                "type": 1,
                "name": "rank-solo-duo",
                "value": f"{leagueUser['rank-solo-duo']}"
            },
            {
                "type": 3,
                "name": "img-solo-duo",
                "value": {
                "url": f"https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-shared-components/global/default/{soloDuo}.png"
                }
            },
            {
                "type": 3,
                "name": "champ-image",
                "value": {
                "url": f"https://ddragon.leagueoflegends.com/cdn/img/champion/loading/{leagueUser['splash-art-champion']}_{leagueUser['splash-art-skinID']}.jpg"
                }
            },
            {
                "type": 1,
                "name": "top-champion",
                "value": f"{leagueUser['top-champion']}"
            },
            {
                "type": 3,
                "name": "img-top-champion",
                "value": {
                "url": f"https://ddragon.leagueoflegends.com/cdn/16.13.1/img/champion/{leagueUser['top-champion']}.png"
                }
            },
            {
                "type": 1,
                "name": "total-mastery",
                "value": f"{leagueUser['total-mastery']}"
            },
            {
                "type": 1,
                "name": "rank-flex",
                "value": f"{leagueUser['rank-flex']}"
            },
            {
                "type": 3,
                "name": "img-flex",
                "value": {
                "url": f"https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-shared-components/global/default/{flex}.png"
                }
            },
            {
                "type": 2,
                "name": "games-won",
                "value": f"{leagueUser['games-won']}"
            },
            {
                "type": 2,
                "name": "games-played",
                "value": f"{leagueUser['games-played']}"
            },
            {
                "type": 2,
                "name": "summoner-level",
                "value": f"{leagueUser['summoner-level']}",
            },
            {
                "type": 1,
                "name": "top-mastery",
                "value": f"{leagueUser['top-mastery']}",
            },
            {
                "type": 3,
                "name": "icon-mastery",
                "value": {
                "url": f"https://raw.communitydragon.org/latest/game/assets/ux/mastery/legendarychampionmastery/masterycrest_level{iconMastery}.png"
                }
            }
            ]
        }
        }

        return json

    def create_user(self, discordID: str, gamename: str, tagline: str):

        if(self.__db.find_user_by_discordID(discordID) == -1): # if user's discordID exists in database
            self.link_riot_to_discordID(discordID, gamename, tagline)
            print(f"Adding {discordID} to database")
        else:
            raise Exception("User already has account linked")

    def link_riot_to_discordID(self, discordID: str, gamename: str, tagline: str):
        
        # Get user's encrypted puuid
            puuid_url = f"https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{gamename}/{tagline}?api_key={self.__api_key}"
        
            puuid = call(puuid_url)["puuid"]
            
            # Create user
            self.__db.collection.insert_one({
                # Identifiers
                "discordID": discordID,

                "Riot Games":{
                    "gamename": gamename,
                    "tagline": tagline,

                    "League of Legends": {
                        # API info
                        "puuid": puuid
                    }
                }})
            
            self.update_user(discordID)

    def update_user(self, discordID:str):

        user = self.__db.find_user_by_discordID(discordID)
        puuid = user["Riot Games"]["League of Legends"]["puuid"]
        
        stats = {
            # Displayed stats
            "splash-art-champion": self.get_top_champ_name(puuid),
            "splash-art-skinID": 0,                        
            
            "top-champion": self.get_top_champ_name(puuid),
            "top-mastery": self.get_top_champ_mastery(puuid),
            "total-mastery": self.get_total_mastery(puuid),

            "rank-solo-duo": self.get_rank_solo_duo(puuid),
            "rank-flex": self.get_rank_flex(puuid),

            "summoner-level": self.get_summoner_level(puuid),
            "games-played": self.get_total_games_played(puuid),
            "games-won": self.get_total_games_won(puuid)
        }

        self.__db.set_fields(discordID, "Riot Games.League of Legends", stats)

    def get_champion_skin_list(self, championName):
        
        championUrl = f"https://ddragon.leagueoflegends.com/cdn/16.13.1/data/en_US/champion/{championName}.json"

        try:
            championSkins = [(skin['num'], skin['name']) for skin in call(championUrl)['data'][championName]['skins'] if "(" not in skin["name"]]
        except:
            print(f"Error: Champion name not found (skin search)")
            return None

        return championSkins

    def set_splash_art(self, discordID: str, championName: str, skinID: str):
        
        # Check skinID for champion exists
        try:
            champURL = f"https://ddragon.leagueoflegends.com/cdn/img/champion/splash/{championName.capitalize()}_{skinID}.jpg"
            call_image(champURL)
        except Exception as e:
            
            print(f"Exception {e}: Champion / skin ID not found (splash art)")
            return None

        values = {
            "splash-art-champion": championName,
            "splash-art-skinID": skinID
        }

        self.__db.set_fields(discordID, "Riot Games.League of Legends", values)

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

        return gamesWon

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

        return gamesPlayed



    def get_rank_flex(self, puuid: str):
        rankURL = f"https://euw1.api.riotgames.com/lol/league/v4/entries/by-puuid/{puuid}?api_key={self.__api_key}"
        flex = None

        try:
            flex = next(queue for queue in call(rankURL) if queue["queueType"] == "RANKED_FLEX_SR")
        except:
            return(f"Unranked")
        
        
        return f"{flex['tier'].capitalize()} {flex['rank']}"

    def get_rank_solo_duo(self, puuid: str):
        rankURL = f"https://euw1.api.riotgames.com/lol/league/v4/entries/by-puuid/{puuid}?api_key={self.__api_key}"
        solo_duo = None

        try:
            solo_duo = next(queue for queue in call(rankURL) if queue["queueType"] == "RANKED_SOLO_5x5")
        except:
            return(f"Unranked")
        
        return f"{solo_duo['tier'].capitalize()} {solo_duo['rank']}"
    


    def get_total_mastery(self, puuid: str):
        masteryUrl = f"https://euw1.api.riotgames.com/lol/champion-mastery/v4/scores/by-puuid/{puuid}?api_key={self.__api_key}"
        
        totalMastery = call(masteryUrl)
        
        return totalMastery

    def get_top_champ_mastery(self, puuid: str):
        
        topMasteryURL = f"https://euw1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}/top?count=1&api_key={self.__api_key}"
        
        topChampion = call(topMasteryURL)[0]
        mastery = topChampion["championLevel"]
        
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
            print(f'Error {response.status_code} accessing: {url}')
            return None
    except requests.exceptions.RequestException as e:
        
        print(f'Exception: {e} (RequestException during call)')
        return None

def call_image(url: str):
    try:
        resp = requests.get(url)
        resp.raise_for_status()  # Make sure the request didn't fail
    except requests.exceptions.HTTPError as e:
        print(f'Exception: {e} (Image call failed)')
        return None

x = LeagueData()
# x.create_user(414120508632596482, "Glacial", "Zelda")
# x.set_splash_art(414120508632596482, 'Gwen', 11)
# print(x.get_champion_skin_list("Gwen"))
# print(x.discordID_to_discordJSON(414120508632596482))
