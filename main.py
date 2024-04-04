import asyncio
import pymongo
import instaloader
from instaloader.exceptions import TwoFactorAuthRequiredException
from telegram_bot import send_group_message
from userInfo import username, password
import time

class FollowerStatus:
    def __init__(self):
        self.username = username
        self.password = password
        self.fapassword = ""
        self.process = ""
        self.myclient = ""
        self.mydb = ""
        self.mycol = ""
        self.followers = []
        self.followees = []
        self.login()
        self.connect_database()

    def login(self):
        self.loader = instaloader.Instaloader()
        try:
            self.loader.login(self.username, self.password)
        except TwoFactorAuthRequiredException:
            self.fapassword = input("Lütfen İki Faktörlü Kimlik Doğrulama Kodunuzu Giriniz: ")
            self.loader.two_factor_login(self.fapassword)

    async def get_followers(self, target_profiles):
        try:
            self.process = "followers"
        except:
            self.get_followers()
        for target_profile in target_profiles:
            target_profile_content = instaloader.Profile.from_username(self.loader.context, target_profile)
            self.followers = target_profile_content.get_followers()
            for follower in self.followers:
                await self.check_database(target_profile, follower.username)

        self.mycol = self.mydb[(str(target_profile) + "_followers") if self.process == "followers" else (str(target_profile) + "_following")]
        existings = self.mycol.find()
        temp = []

        for existing in existings:
            if existing["username"] not in self.followers:
                temp.append(existing["username"])
        for element in temp:
            print("Takipçi Silindi: ", element)
            self.drop_from_database(element, target_profile)
            message = f"Seni Takip Etmeyi Bırakan Bilgisi:\nKullanıcı Adı: {username}\nTakipçi Sayısı: {len(self.followers)}"
            await send_group_message(message)

    async def get_following(self, target_profiles):
        try:
            self.process = "following"
        except:
            self.get_following()
        for target_profile in target_profiles:
            target_profile_content = instaloader.Profile.from_username(self.loader.context, target_profile)
            self.followees = target_profile_content.get_followees()
            for followee in self.followees:
                await self.check_database(target_profile, followee.username)

        self.mycol = self.mydb[(str(target_profile) + "_followers") if self.process == "followers" else (str(target_profile) + "_following")]
        existings = self.mycol.find()
        temp = []

        for existing in existings:
            if existing["username"] not in self.followees:
                temp.append(existing["username"])
        for element in temp:
            print("Takip Edilen Silindi: ", element)
            self.drop_from_database(element, target_profile)
            message = f"Takip Etmeyi Bıraktığın Bilgisi:\nKullanıcı Adı: {username}\nTakipçi Sayısı: {len(self.followees)}"
            await send_group_message(message)

    def connect_database(self):
        self.myclient = pymongo.MongoClient("mongodb://localhost:27017/")
        self.mydb = self.myclient["insta_tracking"]

    def add_to_database(self, import_user, target_profile):
        self.mycol = self.mydb[(str(target_profile) + "_followers") if self.process == "followers" else (str(target_profile) + "_following")]
        dict = {"username": import_user}
        x = self.mycol.insert_one(dict)

    def drop_from_database(self, import_user, target_profile):
        self.mycol = self.mydb[(str(target_profile) + "_followers") if self.process == "followers" else (str(target_profile) + "_following")]
        dict = {"username": import_user}
        self.mycol.delete_one(dict)

    async def check_database(self, target_profile, username):
        self.mycol = self.mydb[(str(target_profile) + "_followers") if self.process == "followers" else (str(target_profile) + "_following")]

        existing_user = self.mycol.find_one({"username": username})

        if self.process == "followers":
            if not existing_user:
                print("Yeni Takipçi Bulundu:", username)
                self.add_to_database(username, target_profile)
                message = f"Yeni Takipçi Bilgisi:\nKullanıcı Adı: {username}\nTakipçi Sayısı: {len(self.followers)}"
                await send_group_message(message)
            else:
                print("Zaten Takipçi:", username)
        elif self.process == "following":
            if not existing_user:
                print("Yeni Takip Edilen Bulundu: ", username)
                self.add_to_database(username, target_profile)
                message = f"Yeni Takip Edilen Bilgisi:\nKullanıcı Adı: {username}\nTakipçi Sayısı: {len(self.followees)}"
                await send_group_message(message)
            else:
                print("Zaten Takip Ediliyor: ", username)

async def main():
    follower_status = FollowerStatus()
    target_profiles = input("Lütfen Aradığınız Hesapları Virgülle Ayırarak Yazınız: ")
    target_profiles = target_profiles.split(",")
    
    while True:
        await asyncio.gather(
            follower_status.get_followers(target_profiles),
            follower_status.get_following(target_profiles)
        )
        
        # Her 1 saatte bir çalışması için 3600 saniye (1 saat) bekleme
        for i in range(3600, 0, -60):
            if i % 60 == 0:  # Her 1 dakikada bir
                print(f"Kalan süre: {i//60} dakika")
            time.sleep(60)  # 60 saniye (1 dakika) bekleme

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
asyncio.run(main())
