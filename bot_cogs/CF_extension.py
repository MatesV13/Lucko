import discord
import sys
import random
import hashlib
import time
import requests
import asyncio
import math
import re 
from typing import NamedTuple
from discord.ext import commands

def setup(bot):
    print('Codeforces se loada!')
    bot.add_cog(CFonly_cog(bot))

def teardown(bot):
    print('Codeforces se unloada!')
    bot.remove_cog('Codeforces')

def normalize(x):
    y = ""
    x = x.lower()
    for c in x:
        if c=='č':
            y+='c'
        elif c=='ć':
            y+='c'
        elif c=='ž':
            y+='z'
        elif c=='š':
            y+='s'
        elif c=='đ':
            y+='d'
        elif ord(c)>=ord('a') and ord(c)<=ord('z'):
            y+=c
    return y

async def try_to_get (link):
    for xakfme in range(10):
        ReQuEsT = requests.get(link)
        if ReQuEsT.status_code==200:
            return ReQuEsT.json()
        else: await asyncio.sleep(1)
    ReQuEsT = {'status':'FAIL'}
    return ReQuEsT

########################### Codeforces naredbe

korisnici = None
CF_problemset = None
CF_ratings = None

async def IsBotAdmin (ctx):
    role = discord.utils.get(ctx.guild.roles, name="BotAdmin")
    if not(role in ctx.author.roles):
        await ctx.send("Sorry, nisi Tech_support! :stuck_out_tongue_winking_eye:")
        return 0;
    return 1;   

class CFonly_cog(commands.Cog, name="Codeforces", description="Naredbe nad javnim codeforces zadatcima"):
    def __init__(self, bot):
        self.bot = bot
        global korisnici, CF_problemset, CF_ratings
        korisnici = bot.korisnici
        CF_problemset = bot.CF_problemset
        CF_ratings = bot.CF_ratings

    @commands.command(name='gimmeCF', brief="Daje nasumičan zadatak s codeforcesa", help='Daje nasumičan zadatak s codeforcesa, neke težine, iz nekog područja. \nAko ne želite specifičnu težinu, upišite prvi argument 0. \nAko ne želite specifičnu temu, upišite drugi argument NULL.')
    async def gimmeCF(self, ctx, tezina='0', podrucje='null'):
        global korisnici, CF_problemset, CF_ratings
        
        if not tezina.isdigit():
            tezina, podrucje = podrucje, tezina
            if not tezina.isdigit():
                tezina = '0'
        tezina = int(tezina)

        index = -1
        for i in range(len(korisnici)):
            if korisnici[i].did==str(ctx.author.id):
                index=i
        if index==-1 or korisnici[index].CF=="Null":
            await ctx.send("Najprije se moraš prijaviti CF accom: koristi ;link CF {username}")
            return;
        
        user_CF_rating = 800
        ReQuEsT = await try_to_get("https://codeforces.com/api/user.info?handles="+korisnici[index].CF)
        if ReQuEsT["status"]=="FAIL":
            await ctx.send("Čini se da je Codeforces srušen trenutno, pa ne mogu napraviti što trenutno tražiš od mene :cry:")
            await ctx.send("Pokušaj kasnije...")
        else: 
            user_CF_xxx = ReQuEsT["result"][0]
            if "rating" in user_CF_xxx:
                user_CF_rating = user_CF_xxx["rating"]
            if user_CF_rating <800:
                user_CF_rating=800
        dostupni=[]
        working_CF_problemset = CF_problemset[:]
        random.shuffle(working_CF_problemset)
        
        for i in range(len(working_CF_problemset)):
            zad = working_CF_problemset[i]
            if not('rating' in zad): continue
            if (tezina==zad['rating'] or (tezina==0 and (zad['rating'] >= user_CF_rating - 300 and zad['rating'] <= user_CF_rating + 300))) and (podrucje.lower()=='null' or (podrucje.lower() in zad['tags'])):
                contestId = zad["contestId"]
                link = "https://codeforces.com/api/contest.status?contestId="+str(contestId)+"&handle="+str(korisnici[index].CF)
                ReQuEsT = await try_to_get(link)
                if ReQuEsT["status"]=="OK" and len(ReQuEsT["result"])==0: 
                    dostupni.append(zad)
            if len(dostupni) > 2:
                break
        
        if len(dostupni):
            odabir = random.choice(dostupni)
            poruka = 'Preporučam zadatak "'+odabir["name"]+'" (rating ' + str(odabir["rating"]) +').\n'
            poruka += 'Zadatak je dostupan na: <https://codeforces.com/problemset/problem/' + str(odabir["contestId"]) + '/' + odabir["index"] + ">"
            await ctx.send(poruka)
        else:
            await ctx.send('Čini se da ne postoji zadatak koji zadovoljava tvoje argumente! :cry:')

    @commands.command(name='findCF', brief="Pronalazi zadatak s javno dostupnih codeforces zadatka", help='Pronalazi zadatak s javno dostupnih codeforces zadatka \nArgumenti mogu biti dijelovi imena zadatka, njegov rating, njegov kod (npr. 260626/A) ili neki njegov tag!\nSvi argumenti osim težine su stringovi. Neutralan argumen za težinu je 0, odnosno "null" za ostalo! \nAko argumen ima više riječi, zapiši ih pod navodnicima! Prikazuje prvih n rezultata')
    async def findCF(self, ctx, ime, rating, kod, tags, n="5"):
        global korisnici, CF_problemset, CF_ratings
        
        rating = int(rating)
        n = int(n)
        moguci=[]

        for idx in range(len(CF_problemset)):
            slicnost = 973
            zad = CF_problemset[idx]
        
            if (ime.lower())==(zad["name"].lower()): slicnost-=750
            elif (ime.lower()) in (zad["name"].lower()): slicnost -=350
            else:
                slicnost-=100
                myime = [0 for _ in range(26)]
                for c in normalize(ime):
                    myime[ord(c)-ord('a')]+=1
                zadime = [0 for _ in range(26)]
                for c in normalize(zad["name"]):
                    zadime[ord(c)-ord('a')]+=1
                for _ in range(26):
                    slicnost += abs(myime[_]-zadime[_])*3

            if rating!=0:
                slicnost -= 250 - abs(rating-zad["rating"])   

            izvor = str(zad["contestId"]) + "/" + zad["index"]
            if (kod in izvor) and ('/' in kod): slicnost -= 750
            elif kod.isalpha() and (kod in izvor): slicnost -= 350
            elif kod.isnumeric() and (kod in izvor): slicnost -= 500
            elif (kod!="") and (kod in izvor): slicnost -= 600

            tagovi = re.split(',|\\ ', tags)
            while '' in tagovi:
                tagovi.remove('')
            for tag in tagovi:
                if tag in zad["tags"]:
                    slicnost /= 2
           
            moguci.append((slicnost, idx))
        moguci.sort()

        rezultat = "PRONAĐENI ZADATCI:\n"
        for i in range(n):
            zadatak = CF_problemset[(moguci[i])[1]]
            rezultat += "Ime zadatka: " + zadatak["name"] + "\n"
            rezultat += "Težina: " + str(zadatak["rating"]) + "\n"
            rezultat += 'Zadatak je dostupan na: <https://codeforces.com/problemset/problem/' + str(zadatak["contestId"]) + '/'+ zadatak["index"] +'>\n'
            rezultat += "Tagovi: " + str(zadatak["tags"]) + "\n"
            vjerojatnost = max(1, (moguci[i])[0])
            vjerojatnost = math.log(vjerojatnost)/math.log(37) * 53
            vjerojatnost = max(0.0, 100 - vjerojatnost)
            rezultat += "Odgovara pretraživanju: " + str(round(vjerojatnost, 2)) + "%\n\n"
            if str(round(vjerojatnost, 2))=="0.0":
                break
            
        await ctx.send(rezultat)

    @commands.command(name='stalkCF', brief="Provjerava nedavnu aktivnost korisnika", help='Provjerava aktivnost korisnika\nDaje povratnu informaciju o aktivnosti korisnika na codeforcesu unazad malo više od sedam dana')
    async def stalkCF(self, ctx, handle):
        link = "https://codeforces.com/api/user.status?handle="+handle
        ReQuEsT = await try_to_get(link)
        if ReQuEsT["status"]!="OK":
            await ctx.send("Nije moguće naći podatke tog korisnika... Provjeri slovkanje!")
            return;
        AC, rest = [], []
        ago_time = 637000

        for subm in ReQuEsT["result"]:
            if subm["creationTimeSeconds"] < (int(time.time())-ago_time):
                break
            if subm["verdict"]=="OK":
                if subm["problem"] in rest:
                    rest.remove(subm["problem"])
                if subm["problem"] not in AC:
                    AC.append(subm["problem"])
            else:
                if subm["problem"] not in (AC+rest):
                    rest.append(subm["problem"])

        poruka = ""
        link = "https://codeforces.com/api/user.info?handles=" + handle
        ReQuEsT = await try_to_get(link)
        if ReQuEsT["status"]=="OK" and ReQuEsT["result"][0]["lastOnlineTimeSeconds"] + 300 > int(time.time()):
            poruka += "Wow, čini se da je "+handle+" upravo online! Anyway...\n"
        if ReQuEsT["status"]=="OK" and ReQuEsT["result"][0]["lastOnlineTimeSeconds"] + ago_time < int(time.time()):
            poruka += "Pa čini se da "+handle+" nije ni upalio codeforces... :cry:\n"
        

        if len(AC+rest)==0:
            poruka += "Tuga i jad: NI JEDAN JEDINI ZADATAK... :cry:"
        if len(AC)!=0:
            poruka += "Korisnik je uspio riješiti ove zadatke nedavno:\n"
            for zad in AC:
                poruka += zad["name"] + " (dostupan na <https://codeforces.com/problemset/problem/" + str(zad["contestId"]) + '/'+ zad["index"] +'>)\n'
        if len(rest)!=0:
            if len(AC)!=0: poruka += "\nOsim toga korisnik je pokušao riješiti i ovih par zadataka:\n"
            else: poruka += "Korisnik nije baš bio uspješan, ali barem je pokušao riješiti ove zadatke nedavno:\n"
            for zad in rest:
                poruka += zad["name"] + " (dostupan na <https://codeforces.com/problemset/problem/" + str(zad["contestId"]) + '/'+ zad["index"] +'>)\n'
        await ctx.send(poruka)
        
