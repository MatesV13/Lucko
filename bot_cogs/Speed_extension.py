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

botlocal = None 

class Speed (NamedTuple):
    did: str = ""
    osobe: None = []
    zadatci: None = []
    rezultati: None = []
    trajanje: int = 90
    kod: int = 0
    raspodijela: str = ""

async def IsBotAdmin (ctx):
    role = discord.utils.get(ctx.guild.roles, name="BotAdmin")
    if not(role in ctx.author.roles):
        await ctx.send("Sorry, nisi moj šef! :stuck_out_tongue_winking_eye: \nČini se da nemaš potrebne ovlasti da učiniš ovo...")
        return 0;
    return 1;  

korisnici = []
Dostupni_Speedovi = []
CF_ratings = []
CF_problemset = []

async def UPDATE_SF():
    sff = open("data_bases/speed.bot", "w")
    for SF in Dostupni_Speedovi:
        while len(SF.osobe) > len(SF.rezultati):
            SF.osobe.remove(SF.osobe[-1])
        print(SF, file = sff)
    sff.close()

async def reloadSpeedBot():
    global Dostupni_Speedovi
    Dostupni_Speedovi = []
    with open("data_bases/speed.bot") as fp: 
        Lines = fp.readlines()
        for line in Lines:
            if line == "\n": continue
            line = line[:-1]
            iduci_speed = eval(line)
            Dostupni_Speedovi.append(iduci_speed)
    fp.close()
    botlocal.dostupni_speedovi = Dostupni_Speedovi
    printf(str(int(time.time())) + " Loaded - SPEEDOVI - " + str(len(Dostupni_Speedovi)) + " speedova.")


def setup(bot):
    print('Speedforces se loada!')
    bot.add_cog(Speedforces_cog(bot))

def teardown(bot):
    print('Speedforces se unloada!')
    bot.remove_cog("Speedforces")


class Speedforces_cog(commands.Cog, name="Speedforces", description="Naredbe vezane za korištenje funkcija Speedforcesa"):
    def __init__(self, bot):
        global botlocal
        botlocal = self.bot = bot
        global Dostupni_Speedovi, korisnici, CF_problemset, CF_ratings
        Dostupni_Speedovi = bot.dostupni_speedovi
        korisnici = bot.korisnici
        CF_problemset = bot.CF_problemset
        CF_ratings = bot.CF_ratings

        
    @commands.command(name='allSF', brief="Vraća sve dostupne Speedforcese!", help='Vraća sve dostupne Speedforcese!')
    async def allSF(self, ctx):
        global Dostupni_Speedovi
        if len(Dostupni_Speedovi)==0:
            await ctx.send("Trenutno ne postoji ni jedan Speedforces! Stvori ga koristeći ;addSF")
            return;
        ctx.send("Dostupni Speedforcesi: ")
        for SF in Dostupni_Speedovi:
            await ctx.send("Speedforces (id=" + str(SF.kod) + ") - trajanje " + str(SF.trajanje) + " minuta - raspodijela " + SF.raspodijela)
        await UPDATE_SF()
       
        
    @commands.command(name='delSF', brief="Briše speedforces po njegovom kodu", help='Nepovratno briše nastali speedforces po njegovom kodu. \nSpeedforces može obrisati samo njegov autor ili BotAdmin.')
    async def delSF(self, ctx, kod):
        global Dostupni_Speedovi
        if kod=="all":
            if not (await IsBotAdmin(ctx)): return;
            while len(Dostupni_Speedovi):
                Dostupni_Speedovi.remove(Dostupni_Speedovi[0])
            print("", end="", file =open("data_bases/speed.bot", "w"))
            await ctx.send("Sva Speedforces natjecanja su obrisana")
            return;
        if not kod.isnumeric():
            await ctx.send("Kod nije prepoznat...")
            return;
        kod = int(kod)
        idx = -1
        for i in range(len(Dostupni_Speedovi)):
            if (Dostupni_Speedovi[i]).kod == kod:
                idx = i
                break
        if idx==-1:
            await ctx.send("Čini se da odabrani Speedforces ne postoji? Probaj ponovo...")
            return
        SF = Dostupni_Speedovi[idx]
        if not (await IsBotAdmin(ctx)): return;
        Dostupni_Speedovi.remove(SF)
        await ctx.send("Speedforces (kod: " + str(kod) + ") je obrisan!")
        await UPDATE_SF()

    @commands.command(name='addSF', brief="Stvara novi Speedforces", help='Stvara novi Speedforces. \nDa bi započeli speedforces, morate koristiti ;startSF {kod} \nTežine zadataka odvojite znakovima / bez dodatnih razmaka.' )
    async def addSF(self, ctx, vrijeme="90", zadatci_SF = "800/800/800/800/800/900/900/900/1000/1000"):
        global Dostupni_Speedovi, CF_problemset, CF_ratings
        SF = Speed()
        SF = SF._replace(zadatci = [])
        SF = SF._replace(osobe = [])
        SF = SF._replace(rezultati = [])
        SF = SF._replace(raspodijela = zadatci_SF)
        SF = SF._replace(did = str(ctx.author.id))
        SF = SF._replace(trajanje = int(vrijeme))
        SF = SF._replace(kod = random.randint(1000000000, 9999999999))
        for zadatak in list(map(int, zadatci_SF.split('/'))):
            if (zadatak <= 4000 and zadatak >= 0 and zadatak%100==0 and len(CF_ratings[zadatak//100])):
                while True:
                    novi_zadatak = CF_problemset[random.choice(CF_ratings[zadatak//100])]
                    index = str(novi_zadatak["contestId"]) + "/" + str(novi_zadatak["index"])
                    if not(index in SF.zadatci):
                        SF.zadatci.append(index)
                        break
            else:
                await ctx.send("Nije moguće pronaći zadatak težine "+ str(zadatak)+ ", pa speedforces nije stvoren...")
                return;

        Dostupni_Speedovi.append(SF)
        poruka = "Stvoren je novi Speedforces! (id= "+ str(SF.kod) + ")\n"
        poruka += "Trajanje ovog Speedforcesa je " + str(vrijeme) + " minuta.\n"
        poruka += "Raspodijela težina je " + zadatci_SF + ".\n"
        poruka += "Kod ovog natjecanja je " + str(SF.kod) + ".\n"
        poruka += "Započni natjecanje koristeći ;startSF " + str(SF.kod) + " - zadatke ćeš dobiti u DM! :smiley:"
        await ctx.send(poruka)
        await UPDATE_SF()

    @commands.command(name='startSF', brief="Započinje Speedforces po njegovom kodu", help='Započinje već stvoreni Speedforces \nNajprije morate stvoriti Speedforces koristeći ;addSF')
    async def startSF(self, ctx, kod):
        global Dostupni_Speedovi, korisnici 
        idx = -1
        for i in range(len(korisnici)):
            if (korisnici[i]).did == str(ctx.author.id):
                idx = i
                break
        if idx==-1 or korisnici[idx].CF=="Null":
            await ctx.send("Najprije se moraš prijaviti svojim codeforces računom!")
            return;
        CF_username = korisnici[idx].CF

        idx = -1
        for i in range(len(Dostupni_Speedovi)):
            if (Dostupni_Speedovi[i]).kod == int(kod):
                idx = i
                break
        if idx==-1:
            await ctx.send("Čini se da odabrani Speedforces ne postoji? Probaj ponovo...")
            return;
        SF = Dostupni_Speedovi[idx]
        
        SpeedForcesZadatci = "Zadatci su: \n"
        for zad in SF.zadatci:
            SpeedForcesZadatci += "<https://codeforces.com/problemset/problem/" + zad + ">\n"
            
        channel = await ctx.author.create_dm()
        await channel.send(SpeedForcesZadatci)
        pocetak = int(time.time())

        trajanje = (SF.trajanje)*60
        await asyncio.sleep(trajanje//2)
        await channel.send("Ostalo ti je još pola vremena!")
        trajanje -= trajanje//2
        if trajanje > 300:
            await asyncio.sleep(trajanje-300)
            await channel.send("Ostalo ti je još 5 minuta!")
            trajanje = 300
        await asyncio.sleep(trajanje)
        await channel.send("Vrijeme je isteklo!")

        broj_rjesenih = 0
        penalty = 0
        for zad in SF.zadatci:
            link =  "https://codeforces.com/api/contest.status?contestId=" + list(zad.split('/'))[0] + "&handle=" + CF_username
            ReQuEsT = requests.get(link)
            if ReQuEsT is None:
                await ctx.send("Čini se da je Codeforces srušen trenutno, pa ne mogu napraviti što trenutno tražiš od mene :cry:")
                await ctx.send("Pokušaj kasnije... Ovaj pokušaj se ne broji i neće biti zabilježen! :heart:")
                return;
            pokusaji = ((ReQuEsT.json())["result"])[::-1]
            cur_penalty = 0
            for pokusaj in pokusaji:
                if pokusaj["creationTimeSeconds"] < pocetak:
                    continue
                if "verdict" in pokusaj:
                    if pokusaj["verdict"]=="OK":
                        cur_penalty += (pokusaj["creationTimeSeconds"] - pocetak)
                        penalty += cur_penalty
                        broj_rjesenih += 1
                        break
                    else:
                        cur_penalty += 737

        await channel.send("Tvoj rezultat za Speedforces (id=" + str(SF.kod) + ") je " + str(broj_rjesenih) + " točnih zadataka, a penalty je " + str(penalty))
        if SF in Dostupni_Speedovi:
            Dostupni_Speedovi[Dostupni_Speedovi.index(SF)].osobe.append(CF_username)
            Dostupni_Speedovi[Dostupni_Speedovi.index(SF)].rezultati.append((broj_rjesenih, penalty))
        await UPDATE_SF()

    @commands.command(name='statusSF', brief="Pokazuje standings za specifičan Speedforces", help="Pokazuje standings za specifičan Speedforces!")
    async def statusSF(self, ctx, kod):
        kod = int(kod)
        idx = -1
        for i in range(len(Dostupni_Speedovi)):
            if (Dostupni_Speedovi[i]).kod == kod:
                idx = i
                break
        if idx==-1:
            await ctx.send("Čini se da odabrani Speedforces ne postoji? Probaj ponovo...")
            return
        SF = Dostupni_Speedovi[idx]

        status = []
        for i in range(len(SF.rezultati)):
            x = ((SF.rezultati[i][0]), (SF.rezultati[i][1]), SF.osobe[i])
            status.append(x)
        poruka = "STANJE: (id= " + str(SF.kod) + ")\n"
        status = sorted(status, key = lambda pair : (pair[0] * (123456789123456789) - pair[1]), reverse=True)
        po_redu = 1
        for rezultat in status:
            poruka += str(po_redu) + ". " + rezultat[2] + " - " + str(rezultat[0]) + " riješenih zadataka - penalty: " + str(rezultat[1]) + "\n"
            po_redu += 1
        if len(status)==0:
            poruka += "Zasad nitko nije dovršio natjecanje..."
        await ctx.send(poruka)


