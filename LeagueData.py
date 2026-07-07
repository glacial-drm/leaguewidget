import os, requests, json
import urllib.request
from dotenv import load_dotenv

class LeagueData:
    __api_key = ""
    
    __gamename, __tagline = "", ""
    __puuid = ""    
    
    __urls, __posts = {}, {} # store any relevant dicts in the database ----------------
    
    def __init__(self, gamename:str, tagline:str):
        load_dotenv(override=False)
        self.__api_key = os.getenv("API_KEY")

        self.__urls["versions"] = "https://ddragon.leagueoflegends.com/api/versions.json"


        self.refresh_user(gamename, tagline)

    def refresh_user(self, gamename:str, tagline:str):        
        self.__set_gamename(gamename)
        self.__set_tagline(tagline)
        
        
        self.__urls["account"] = f"https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{self.__gamename}/{self.__tagline}?api_key={self.__api_key}"
        
        self.__posts["account"] = call(self.__urls["account"])
        self.__puuid = self.__posts["account"]["puuid"]
        
    
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
    
    def get_total_mastery(self):
        self.__urls["total-mastery"] = f"https://euw1.api.riotgames.com/lol/champion-mastery/v4/scores/by-puuid/{self.__puuid}?api_key={self.__api_key}"
        totalMastery = call(self.__urls["total-mastery"])
        
        return totalMastery

    def get_top_champ_mastery(self):
        pass
    def get_top_champ_name(self):
        
        top_champ_id = self.get_top_champ_id(self.__puuid)
        
        return self.champ_id_to_name(top_champ_id)    
    def get_top_champ_id(self):
        self.__urls["top-mastery"] = f"https://euw1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{self.__puuid}?api_key={self.__api_key}"

        self.__posts["top-mastery"] = call(self.__urls["top-mastery"])

        id = str(self.__posts["top-mastery"][0]["championId"])
        return id
    
    def champ_id_to_name(self, id: str):
        champ_json, name = "", ""
        try:
            with urllib.request.urlopen(self.__urls["versions"]) as version_url:
                
                league_version = json.loads(version_url.read().decode())[0] # set to latest version
                
                self.__urls["champions"] = f"https://ddragon.leagueoflegends.com/cdn/{league_version}/data/en_US/champion.json"
        except:
            print('Exception: failed to load latest version of league')

        try:
            with urllib.request.urlopen(self.__urls["champions"]) as champ_url:
            
                champ_json = json.loads(champ_url.read().decode())["data"]
        except:
            print('Exception: failed to load champ json data')

        name = next(champ for champ in champ_json if champ_json[champ]["key"] == id)
        return name

    def __set_gamename(self, gamename):
        self.__gamename = gamename
    def __set_tagline(self, tagline):
        self.__tagline = tagline
    
    def get_gamename(self):
        return self.__gamename
    def get_tagline(self):
        return self.__tagline

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

    
x = LeagueData("Glacial", "zelda")
print(x.get_total_mastery())
