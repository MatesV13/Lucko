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
    print('Lockout se loada!')
    bot.add_cog(Lockout_cog(bot))

def teardown(bot):
    print('Lockout se unloada!')
    bot.remove_cog('Lockout')

class User (NamedTuple):
    ime: str = "Null"         ### discord username
    did: str = "Null"          ### discord id
    CF: str = "Null"           ### CF username
    CSES: str = "Null"       ### CSES username
    AT: str = "Null"          ### AT username
    solve: list = []         ### zadatci = 2 ako nije pokušavano / 1 ako je pokušavano / 0 ako je riješeno

korisnici = []
CF_ratings = []
CF_problemset = []

class Duel (NamedTuple):
    osoba1: User = User()
    osoba2: User = User()
    zadatci: list = []
    vrijednosti: list = []
    rezultat: list = []
    tezine: str = ""
    pocetak: int=0
    trajanje: int=0
    kod: int=0
    
dueli = []

async def try_to_get (link):
    for xakfme in range(10):
        ReQuEsT = requests.get(link)
        if ReQuEsT.status_code==200:
            return ReQuEsT.json()
        else: await asyncio.sleep(1)
    ReQuEsT = {'status':'FAIL'}
    return ReQuEsT

########################### Lockout naredbe!
        
class Lockout_cog(commands.Cog, name="Lockout", description="Naredbe koje podupiru stvaranje Lockout duela!"):
    def __init__(self, bot):
        self.bot = bot
        global korisnici, CF_ratings, CF_problemset
        korisnici = bot.korisnici
        CF_ratings = bot.CF_ratings
        CF_problemset = bot.CF_problemset

    @commands.command(name='del_duel', brief='Briše aktivni duel u kojem si član.', help="Može obrisati aktivan duel u kojem si član\nOva funkcija zaobilazi timeout od 5 minuta ukoliko ste pogriješili u stvaranju duela\nBilo koja od dvije uključene osobe može obrisati duel\nZa brisanje je potreban kod duela koji je prikazan pri stvaranju duela!")
    async def del_duel(self, ctx, id : int):
        global dueli
        maknut=0
        for duel in dueli:
            if duel.kod==id and (duel.osoba1.did==str(ctx.author.id) or duel.osoba2.did==str(ctx.author.id)):
                dueli.remove(duel)
                maknut += 1
        if maknut==0:
            await ctx.send("Čini se da nema duela kojeg možeš obrisati...")
        else:
            await ctx.send("Lockout duel (id=" + str(id) + ") obrisan!")
            

    @commands.command(name='all_duels', brief='Ispisuje listu aktivnih duela!', help="Ispisuje listu aktivnih duela i svih potrebnih podataka, među kojima je i kod duela")
    async def all_duels(self, ctx):
        global dueli
        poruka = "Aktivni dueli: \n\n"
        if len(dueli)==0:
            poruka = "Nema aktivnih duela! :cry:"
        for duel in dueli:
            poruka += duel.osoba1.CF + " vs. " + duel.osoba2.CF + " -  duel u trajanju od " + str(duel.trajanje) + " minuta.\n"
            poruka += "Težine zadataka: " + duel.tezine + "\n"
            poruka += "Vrijednosti zadataka: " + ("/".join(map(str, duel.vrijednosti))) + "\n"
            poruka += "Kod duela je " + str(duel.kod) + "\n\n"
        await ctx.send(poruka)
        
    @commands.command(name='lets_duel', brief='Prihvaća duel protiv drugog korisnika!', help="Prihvaća najnoviji duel koji je predložen protiv tebe\nUkoliko želiš prihvatiti specifičan duel (koji nije najnoviji) možeš dodati njegov kod.")
    async def lets_duel(self, ctx, LockoutId: int = 0):
        global dueli
        idx = -1
        for i in range(len(dueli)):
            duel = dueli[i]
            if duel.osoba2.did == str(ctx.author.id) and duel.pocetak==0 and (LockoutId==0 or LockoutId == duel.kod):
                idx = i
        if idx==-1:
            await ctx.send("Ne postoji duel kojeg možeš započeti! \nAko želiš stvoriti duel, koristi ;lockout {protivnik} \nAko koristiš LockoutId, provjeri id. Ne možeš prihvatiti tuđi duel!")
            return;

        
        tekst = "Duel pokrenut - <@!" + duel.osoba1.did + "> vs. <@!" + duel.osoba2.did + "> \nZadatci su:\n"
        for i in range(len(dueli[idx].zadatci)):
            tekst += str(dueli[idx].vrijednosti[i]) + ": <https://codeforces.com/problemset/problem/" + dueli[idx].zadatci[i] + ">\n"
        await ctx.send(tekst)
            
        dueli[idx] = dueli[idx]._replace(pocetak=int(time.time()))
        duel = dueli[idx]
        dueli.remove(dueli[idx])
        
        jos30=1
        if (duel.trajanje < 45):
            jos30=0
        jos15=1
        if (duel.trajanje < 25):
            jos15=0
        jos5 = 1
        score1, score2 = 0, 0
        max_score = sum(duel.vrijednosti)

        stanje = "STANJE :\n"
        for i in range(len(duel.zadatci)):
            tko = "Nitko još!"
            if duel.rezultat[i]==1:
                tko = duel.osoba1.CF
            elif duel.rezultat[i]==2:
                tko = duel.osoba2.CF
            elif duel.rezultat[i]==3:
                tko = "Neriješeno!"
            stanje += str(duel.vrijednosti[i]) + ": " + tko + "\n"
        stanje += "====================\n"
        stanje += duel.osoba1.CF + ": " + str(score1) + "\n"
        stanje += duel.osoba2.CF + ": " + str(score2)
        sendS = await ctx.send(stanje)

        PING = 10
        while (duel.pocetak + 60*duel.trajanje-PING >= int(time.time())):
            await asyncio.sleep(PING)
            if duel.pocetak + 60*(duel.trajanje-30) < int(time.time()) and jos30:
                jos30=0
                await ctx.send(" <@!" + duel.osoba1.did + "> & <@!" + duel.osoba2.did + "> - preostalo vam je još manje od 30 minuta.")
            if duel.pocetak + 60*(duel.trajanje-15) < int(time.time()) and jos15:
                jos15=0
                await ctx.send(" <@!" + duel.osoba1.did + "> & <@!" + duel.osoba2.did + "> - preostalo vam je još manje od 15 minuta!")
            if duel.pocetak + 60*(duel.trajanje-5) < int(time.time()) and jos5:
                jos5=0
                await ctx.send(" <@!" + duel.osoba1.did + "> & <@!" + duel.osoba2.did + "> - preostalo vam je još manje od 5 minuta!!!")
            for i in range(len(duel.zadatci)):
                if duel.rezultat[i]==0:
                    contestId, problemId = (duel.zadatci[i]).split('/')

                    link = "https://codeforces.com/api/contest.status?contestId="+str(contestId)+"&handle="+str((duel.osoba1).CF)
                    ReQuEsT = await try_to_get(link)
                    if ReQuEsT["status"]!="OK":
                        await ctx.send("Čini se da je Codeforces srušen trenutno, pa ne mogu napraviti što trenutno tražiš od mene :cry:")
                        await ctx.send("Stoga je duel obustavljen i rezultat je određen prema trenutnom stanju... ")
                        duel = duel._replace(pocetak=0)
                        break
                    subovi = ReQuEsT["result"]
                    for sub in subovi:
                        if (('verdict' in sub) and sub['verdict']=='OK') and sub['problem']['index']==problemId:
                            duel.rezultat[i]+=1
                            break

                    link = "https://codeforces.com/api/contest.status?contestId="+str(contestId)+"&handle="+str((duel.osoba2).CF)
                    ReQuEsT = await try_to_get(link)
                    if ReQuEsT["status"]!="OK":
                        await ctx.send("Čini se da je Codeforces srušen trenutno, pa ne mogu napraviti što trenutno tražiš od mene :cry:")
                        await ctx.send("Stoga je duel obustavljen i rezultat je određen prema trenutnom stanju... ")
                        duel = duel._replace(pocetak=0)
                        break
                    subovi = ReQuEsT["result"]
                    for sub in subovi:
                        if (('verdict' in sub) and sub['verdict']=='OK') and sub['problem']['index']==problemId:
                            duel.rezultat[i]+=2
                            break

                    if duel.rezultat[i]==1:
                        await ctx.send(" <@!" + duel.osoba2.did + "> - <@!" + duel.osoba1.did + "> brže je riješio zadatak " + duel.zadatci[i] + "!\nZato dobiva " + str(duel.vrijednosti[i]) + " bodova za zadatak i ovaj zadatak više ne može biti rješavan!")
                        score1 += duel.vrijednosti[i]
                    elif duel.rezultat[i]==2:
                        await ctx.send(" <@!" + duel.osoba1.did + "> - <@!" + duel.osoba2.did + "> brže je riješio zadatak " + duel.zadatci[i] + "!\nZato dobiva " + str(duel.vrijednosti[i]) + " bodova za zadatak i ovaj zadatak više ne može biti rješavan!")
                        score2 += duel.vrijednosti[i]
                    elif duel.rezultat[i]==3:
                        score1 += duel.vrijednosti[i]//2
                        score2 += duel.vrijednosti[i]//2
                        await ctx.send(" <@!" + duel.osoba1.did + "> & <@!" + duel.osoba2.did + "> - vremenska razlika je premala!\nOboje dobivate po " + str(duel.vrijednosti[i]//2) + " bodova za zadatak " + duel.zadatci[i])

            stanje = "STANJE :\n"
            for i in range(len(duel.zadatci)):
                tko = "Nitko još!"
                if duel.rezultat[i]==1:
                    tko = duel.osoba1.CF
                elif duel.rezultat[i]==2:
                    tko = duel.osoba2.CF
                elif duel.rezultat[i]==3:
                    tko = "Neriješeno!"
                stanje += str(duel.vrijednosti[i]) + ": " + tko + "\n"
            stanje += "====================\n"
            stanje += duel.osoba1.CF + ": " + str(score1) + "\n"
            stanje += duel.osoba2.CF + ": " + str(score2)

            await sendS.edit(content=stanje)
            if score1 > max_score//2 or score2 > max_score//2:
                break

        if score1 > score2:
            await ctx.send("<@!" + duel.osoba1.did + "> pobjedio/la je <@!" + duel.osoba2.did + "> u ovom duelu!")
        elif score2 > score1:
            await ctx.send("<@!" + duel.osoba2.did + "> pobjedio/la je <@!" + duel.osoba1.did + "> u ovom duelu!")
        else:
            await ctx.send("Nije moguće odrediti pobjednika između <@!" + duel.osoba1.did + "> i <@!" + duel.osoba2.did + "> u ovom duelu... Neriješeno?")
        printf("duel =" +str(duel))

    @commands.command(name='lockout', brief="Stvara duel protiv drugog korisnika", help='Stvara duel protiv drugog korisnika! \nDrugi korisnik mora prihvatiti! \nMoguće je izabrati vlastiti raspored težina; odvojite ih kosom crtom! npr. "100/200/300/400/500" \nPozivnica vrijedi samo 5 min!')
    async def lockout(self, ctx, username2, trajanje="60", tezina="800/900/1000/1100/1200", vrijednosti="100/200/300/400/500"):
        async with ctx.typing():
            global dueli, korisnici, CF_problemset, CF_ratings
            novi_duel = Duel(User(), User(), [], [], [], tezina, 0, 0, 0)
            for i in range(len(korisnici)):
                korisnik = korisnici[i]
                if str(ctx.author.id) == korisnik.did:
                    novi_duel = novi_duel._replace(osoba1=korisnik)
            if (novi_duel.osoba1).CF == "Null":
                await ctx.send("Najprije trebaš povezati discord sa svojim CF accom: koristi naredbu ;link CF {username}")
                return;
            
            for i in range(len(korisnici)):
                korisnik = korisnici[i]
                if username2 in {(korisnik.ime.split('#'))[0], korisnik.ime, korisnik.CF, korisnik.CSES, korisnik.AT}:
                    novi_duel = novi_duel._replace(osoba2=korisnik)
            if (novi_duel.osoba2).ime == "Null":
                await ctx.send("Korisnik kojeg želiš izazvati ne postoji! :cry:")
                return;
            if (novi_duel.osoba2).CF == "Null":
                await ctx.send("Korisnik kojeg želiš izazvati još nije povezao svoj CF acc!")
                return;

            if novi_duel.osoba1 == novi_duel.osoba2:
                await ctx.send("Ne možeš se boriti sam protiv sebe... :rofl:")
                return;

            if len(list(map(int, tezina.split('/')))) > len(list(map(int, vrijednosti.split('/')))):
                await ctx.send("Nedostaju argumenti za 'vrijednosti' ili ima višak argumenata za 'težina'!")
                return;
            if len(list(map(int, tezina.split('/')))) < len(list(map(int, vrijednosti.split('/')))):
                await ctx.send("Nedostaju argumenti za 'težina' ili ima višak argumenata za 'vrijednosti'!")
                return;
            
            odabrane_tezine = list(map(int, tezina.split('/')))
            for idx in odabrane_tezine:
                for _ in range (21):
                    if _ == 20:
                        await ctx.send("Nije moguće stvoriti duel jer ste riješili previše zadataka! :rofl:")
                        return;

                    original = random.choice(CF_ratings[idx//100])
                    contestId = (CF_problemset[original])["contestId"]    

                    for _ in range(11):
                        if _==10:
                            ctx.send("Ne mogu dohvatiti Codeforces u ovom trenutku... Duel nije stvoren. :cry:")
                            await ctx.send("Pokušajte kasnije... Neće zadaci pobjeći! :heart:")
                            return;
                        link = "https://codeforces.com/api/contest.status?contestId="+str(contestId)+"&handle="+str(((novi_duel).osoba1).CF)
                        ReQuEsT = requests.get(link)
                        if ReQuEsT.status_code==200:
                            break
                        else: await asyncio.sleep(1)

                    if len(ReQuEsT.json()["result"])!=0:
                        continue

                    for _ in range(11):
                        if _==10:
                            ctx.send("Ne mogu dohvatiti Codeforces u ovom trenutku... Duel nije stvoren. :cry:")
                            await ctx.send("Pokušajte kasnije... Neće zadaci pobjeći! :heart:")
                            return;
                        link = "https://codeforces.com/api/contest.status?contestId="+str(contestId)+"&handle="+str(((novi_duel).osoba2).CF)
                        ReQuEsT = requests.get(link)
                        if ReQuEsT.status_code==200:
                            break
                        else: await asyncio.sleep(1)

                    if len(ReQuEsT.json()["result"])!=0:
                        continue

                    (novi_duel.zadatci).append(str(contestId) + "/" + str((CF_problemset[original])["index"]))
                    break

            novi_duel = novi_duel._replace(vrijednosti = list(map(int, vrijednosti.split('/'))))
            novi_duel = novi_duel._replace(trajanje = int(trajanje))
            novi_duel = novi_duel._replace(rezultat = [0 for _ in range(len(novi_duel.zadatci))])
            novi_duel = novi_duel._replace(kod = random.randint(1000000000, 9999999999))

        dueli.append(novi_duel)
        await ctx.send("Duel pripremljen! Korisnik <@!" + novi_duel.osoba2.did + "> sada mora odgovoriti s `;lets_duel`! \nU slučaju potrebe, kod novostvorenog duela je: " + str((novi_duel).kod))
        await asyncio.sleep(5*60)
        if novi_duel in dueli:
            dueli.remove(novi_duel)
            await ctx.send(ctx.message.author.mention + "! Korisnik <@!" + novi_duel.osoba2.did + "> nije odgovorio na tvoj duel na vrijeme, i zato je obrisan!")
