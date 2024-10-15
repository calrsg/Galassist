import requests
import json

class OsuPlayer:
    def __init__(self, data: []):
        self.name = data["username"]
        self.id = int(data["user_id"])
        self.country = data["country"]
        self.pp = float(data["pp_raw"])
        self.rank = int(data["pp_rank"])
        self.badges = 0
        self.pbadges = 0

    def getName(self):
        return self.name

    def getId(self):
        return self.id

    def getCountry(self):
        return self.country

    def getPP(self):
        return self.pp

    def getRank(self):
        return self.rank

    def setBadgesAll(self, badges: int, pbadges: int):
        self.badges = badges
        self.pbadges = pbadges

class OsuApi:
    def __init__(self):
        self.apiurl = "https://osu.ppy.sh/api/"
        self.apikey = ""

        with open("./config.json") as file:
            contents = json.loads(file.read())
            self.apikey = contents["osu"]["osu_api"]

    def getPlayer(self, username) -> OsuPlayer:
        request = requests.get(f"{self.apiurl}get_user?k={self.apikey}&u={username}&m=0")
        if request.status_code != 200:
            print(f"Error fetching data, status code {request.status_code}")
            return None
        data = request.json()
        return data[0]