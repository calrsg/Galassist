import asyncio
import json

class TwitLog:
    def __init__(self):
        self.filepath = "twitlog.json"
        self.lock = asyncio.Lock()
        self.data = {}

    async def load(self):
        async with self.lock:
            with open(self.filepath, "r") as f:
                self.data = json.load(f)

    async def dump(self):
        async with self.lock:
            with open(self.filepath, "w") as f:
                json.dump(self.data, f, indent=4)

    async def add_to_server(self, serverID, entryNum):
        serverID = str(serverID)
        async with self.lock:
            if serverID not in self.data["servers"]:
                self.data["servers"][serverID] = 0
            self.data["servers"][serverID] += entryNum

    async def add_to_user(self, userID, entryNum):
        userID = str(userID)
        async with self.lock:
            if userID not in self.data["users"]:
                self.data["users"][userID] = 0
            self.data["users"][userID] += entryNum

    async def add_total_fixed(self, entryNum):
        async with self.lock:
            self.data["links_fixed"] += entryNum

    async def add_ignored(self, userID):
        userID = str(userID)
        async with self.lock:
            if userID not in self.data["ignored"]:
                self.data["ignored"][userID] = True

    async def rem_ignored(self, userID):
        userID = str(userID)
        async with self.lock:
            if userID in self.data["ignored"]:
                self.data["ignored"].pop(userID, None)

    async def get_stats(self):
        async with self.lock:
            sorted_servers = {k: v for k, v in sorted(self.data["servers"].items(), key=lambda item: item[1], reverse=True)}
            sorted_users = {k: v for k, v in sorted(self.data["users"].items(), key=lambda item: item[1], reverse=True)}
            total_fixed = self.data["links_fixed"]
            return sorted_servers, sorted_users, total_fixed

    async def get_server_stats(self, serverID):
        serverID = str(serverID)
        async with self.lock:
            if serverID not in self.data["servers"]:
                return 0
            return self.data["servers"][serverID]

    async def get_user_stats(self, userID):
        userID = str(userID)
        async with self.lock:
            if userID not in self.data["users"]:
                return 0
            return self.data["users"][userID]

    async def get_ignored(self, userID):
        userID = str(userID)
        async with self.lock:
            if userID not in self.data["ignored"]:
                return False
            return True

    async def update(self, serverID, userID, entryNum):
        await self.add_to_server(serverID, entryNum)
        await self.add_to_user(userID, entryNum)
        await self.add_total_fixed(entryNum)