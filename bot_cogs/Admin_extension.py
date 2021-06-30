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

TOKEN, KEY, SECRET, GROUP_LINK = None, None, None, None

def setup(bot):
    print('Admin_extension se loada.')
    with open("data_bases/secret.bot") as fp:
        global TOKEN, KEY, SECRET, GROUP_LINK
        TOKEN = fp.readline().replace('\n','')
        KEY = fp.readline().replace('\n','') 
        SECRET = fp.readline().replace('\n','')
        GROUP_LINK = fp.readline().replace('\n', '')
    bot.add_cog(Admin_cog(bot))

def teardown(bot):
    print('Admin_extension se unloada.')
    bot.remove_cog('Admin')

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

class Zadatak (NamedTuple):
    ime: str = ""                ### ime zadatka
    tezina: float = ""         ### procijena tezine
    natjecanje: str = ""     ### ime natjecanja
    izvor: str = ""              ### link na zadatak
    tags: str = ""               ### tagovi
    ans: str = "None"         ### link na tutorial


korisnici = None
zadatci = None
contests = None
botlocal = None

async def IsBotAdmin (ctx):
    try:
        role = discord.utils.get(ctx.guild.roles, name="BotAdmin")
        if not(role in ctx.author.roles):
            await ctx.send("Sorry, nisi moj šef! :stuck_out_tongue_winking_eye: \nČini se da nemaš potrebne ovlasti da učiniš ovo...")
            return 0;
        else: return 1;
    except:
        return 0;


async def UPDATE_FILE():
    global korisnici
    f = open("data_bases/korisnici.bot", "w")
    for user in korisnici:
        linija = user.ime + '&' + user.did + '&' + user.CF + '&' + user.CSES + '&' + user.AT + '&'
        for i in user.solve:
            linija+=str(i)
        f.write(linija + '\n')
    f.close()
    botlocal.korisnici = korisnici
    return;

async def UPDATE_ZADATCI():
    global zadatci, contests
    f = open("data_bases/zadatci.bot", "w")
    linija = '#'.join(map(str, contests))
    f.write(linija + '\n')
    for zad in zadatci:
        linija = zad.ime + '#' + str(zad.tezina) + '#' + zad.natjecanje + '#' + zad.izvor + '#' + zad.tags + '#' + zad.ans
        f.write(linija + '\n')
    f.close()
    botlocal.contests = contests
    botlocal.zadatci = zadatci
    return;

async def try_to_get (link):
    for xakfme in range(10):
        ReQuEsT = requests.get(link)
        if ReQuEsT.status_code==200:
            return ReQuEsT.json()
        else: await asyncio.sleep(1)
    ReQuEsT = {'status':'FAIL'}
    return ReQuEsT


########################### Admin naredbe


class Admin_cog(commands.Cog, name="Admin", description="Služi uglavnom za administriranje bazama podataka"):  
    def __init__(self, bot):
        global botlocal
        self.bot = botlocal = bot
        global korisnici, zadatci, contests
        korisnici = bot.korisnici
        zadatci = bot.zadatci
        contests = bot.contests

    @commands.command(name='problem_info', brief='Vraća sve informacije o zadatku po njegovom izvoru!', help='Vraća sve informacije o zadatku po njegovom izvoru!\nJako koristan jer među vraćenim podatcima vraća i indeks zadatka u bazi podataka\nNpr. ;problem_info 260626/A')
    async def problem_info(self, ctx, idx):
        global zadatci
        br_find = 0
        for i in range(len(zadatci)):
            zad = zadatci[i]
            if idx == zad.izvor:
                info = '"' + zad.ime + '" '
                info += '"' + str(zad.tezina) + '" '
                info += '"' + zad.natjecanje + '" '
                info += '"' + zad.izvor + '" '
                info += '"' + zad.tags + '" '
                info += '"' + zad.ans + '"'
                info += "\nIndeks ovog zadatka u bazi je " + str(i)
                br_find+=1
                await ctx.send(info)
        if br_find==0:
            await ctx.send("Nema nađenih rezultata...")
                
    @commands.command(name='problem_edit', brief="Mjenja podatke zadatka u bazi", help='Nepovratno mjenja podatke zadatka u bazi, potrebno je znati indeks zadatka u bazi (prvi argument)- koristi problem_info ili findGLV\n\nime je ime zadatka\ntezina je procijena težine na ljestvici od 0 do 10 (npr 0.37)\nnatjecanje je kolokvijalno ime natjecanja (npr. Test)\nizvor je jedinstveni kod u codeforces bazi i sastoji se od contest id + redno slovo (npr. 260626/A)\ntagove valjda odvajati zarezima bez razmaka (npr. "math,vikanje")\nans je link na editorijal - naravno da nije nužan argument ako ga nema; stavi "None" u tom slučaju')
    async def problem_edit(self, ctx, idx, ime, tezina, natjecanje, izvor, tags, ans="None"):
        if not (await IsBotAdmin(ctx)): return;
        idx = int(idx)
        zad = zadatci[idx]
        info = '"' + zad.ime + '" '
        info += '"' + str(zad.tezina) + '" '
        info += '"' + zad.natjecanje + '" '
        info += '"' + zad.izvor + '" '
        info += '"' + zad.tags + '" '
        info += '"' + zad.ans + '" '
        await ctx.send("Stari info: " + info)
        sendS = await ctx.send("Jesi li siguran da želiš promjeniti podatke zadatka?\nKao potvrdu, stavi 👍 ovu poruku!")
        await sendS.add_reaction('👍' )
        try:
            reaction, _ = await self.bot.wait_for('reaction_add', check=lambda r, u: r.emoji=='👍'  and r.message.id == sendS.id and u == ctx.author, timeout=60)
        except asyncio.TimeoutError:
            await sendS.remove_reaction('👍', self.bot.user)
            return;
        zadatci[idx] = zadatci[idx]._replace(ime=ime)
        zadatci[idx] = zadatci[idx]._replace(tezina = float(tezina))
        zadatci[idx] = zadatci[idx]._replace(natjecanje = natjecanje)
        zadatci[idx] = zadatci[idx]._replace(izvor = izvor)
        zadatci[idx] = zadatci[idx]._replace(tags = tags)
        zadatci[idx] = zadatci[idx]._replace(ans = ans)
        zad = zadatci[idx]
        info = '"' + zad.ime + '" '
        info += '"' + str(zad.tezina) + '" '
        info += '"' + zad.natjecanje + '" '
        info += '"' + zad.izvor + '" '
        info += '"' + zad.tags + '" '
        info += '"' + zad.ans + '" '
        await UPDATE_ZADATCI()
        await ctx.send("Editirano. \nNovi info: " + info)

    @commands.command(name='problem_add', brief="Dodaje zadatak u bazu", help='Dodaje zadatak u bazu kroz sve potrebne parametre.\nime je ime zadatka\ntezina je procijena težine na ljestvici od 0 do 10 (npr 0.37)\nnatjecanje je kolokvijalno ime natjecanja (npr. Test)\nizvor je jedinstveni kod u codeforces bazi i sastoji se od contest id + redno slovo (npr. 260626/A)\ntagove valjda odvajati zarezima bez razmaka (npr. "math,vikanje")\nans je link na editorijal - naravno da nije nužan argument ako ga nema; stavi "None" u tom slučaju')
    async def problem_add(self, ctx, ime, tezina, natjecanje, izvor, tags, ans="None"):
        if not (await IsBotAdmin(ctx)): return;
        info = '"' + ime + '" '
        info += '"' + tezina + '" '
        info += '"' + natjecanje + '" '
        info += '"' + izvor + '" '
        info += '"' + tags + '" '
        info += '"' + ans + '" '
        await ctx.send("Info: " + info)
        sendS = await ctx.send("Jesi li siguran da želiš dodati zadatak?\nKao potvrdu, stavi 👍 ovu poruku!")
        await sendS.add_reaction('👍' )
        try:
            reaction, _ = await self.bot.wait_for('reaction_add', check=lambda r, u: r.emoji=='👍'  and r.message.id == sendS.id and u == ctx.author, timeout=60)
        except asyncio.TimeoutError:
            await sendS.remove_reaction('👍', self.bot.user)
            return;
        idx = len(zadatci)
        zadatci.append(Zadatak())
        zadatci[idx] = zadatci[idx]._replace(ime=ime)
        zadatci[idx] = zadatci[idx]._replace(tezina = float(tezina))
        zadatci[idx] = zadatci[idx]._replace(natjecanje = natjecanje)
        zadatci[idx] = zadatci[idx]._replace(izvor = izvor)
        zadatci[idx] = zadatci[idx]._replace(tags = tags)
        zadatci[idx] = zadatci[idx]._replace(ans = ans)
        zad = zadatci[idx]
        info = '"' + zad.ime + '" '
        info += '"' + str(zad.tezina) + '" '
        info += '"' + zad.natjecanje + '" '
        info += '"' + zad.izvor + '" '
        info += '"' + zad.tags + '" '
        info += '"' + zad.ans + '" '
        await UPDATE_ZADATCI()
        await ctx.send("Zadatak dodan. \nInfo: " + info)

    @commands.command(name='problem_del', brief="Briše zadatak iz baze", help='Nepovratno briše zadatak iz baze\nPotreban je indeks zadatka u bazi - koristi ;problem_info')
    async def problem_del(self, ctx, idx):
        if not (await IsBotAdmin(ctx)): return;
        idx = int(idx)
        zad = zadatci[idx]
        info = '"' + zad.ime + '" '
        info += '"' + str(zad.tezina) + '" '
        info += '"' + zad.natjecanje + '" '
        info += '"' + zad.izvor + '" '
        info += '"' + zad.tags + '" '
        info += '"' + zad.ans + '" '
        await ctx.send("Info: " + info)
        sendS = await ctx.send("Jesi li siguran da želiš izbrisati zadatak?\nKao potvrdu, stavi 👍 ovu poruku!")
        await sendS.add_reaction('👍' )
        try:
            reaction, _ = await self.bot.wait_for('reaction_add', check=lambda r, u: r.emoji=='👍'  and r.message.id == sendS.id and u == ctx.author, timeout=60)
        except asyncio.TimeoutError:
            await sendS.remove_reaction('👍', self.bot.user)
            return;
        zadatci.remove(zadatci[idx])
        await UPDATE_ZADATCI()
        await ctx.send("Zadatak je uspješno izbrisan")


    @commands.command(name='add_contest', brief="Povlači zadatke s codeforces natjecanja", help='Polu automatski povlači zadatke s nekog codeforces natjecanja\nArgument id je contest id na codeforcesu (šesteroznamenkasti broj u linku na contest)\nIme natjecanja je kolokvijalno ime natjecanja (npr. GLVoni 3.kolo)\nEditorial je link na editorial (na grupnom blogu), a ako još nije napisan stavi "None"')
    async def add_contest (self, ctx, id, ime, editorial="None"):
        global KEY, SECRET
        if not (await IsBotAdmin(ctx)): return;
        curtime = int(time.time())
        myrand = random.randint(100000, 999999)
        try_to_hash = str(myrand)+"/contest.standings?apiKey="+KEY+"&contestId="+str(id)+"&time="+str(curtime)+"#"+SECRET
        myhash = hashlib.sha512(bytes(try_to_hash, 'utf-8')).hexdigest()
        link = "https://codeforces.com/api/contest.standings?apiKey="+KEY+"&contestId="+str(id)+"&time="+str(curtime)+"&apiSig="+str(myrand)+myhash
        rezultat = await try_to_get(link)
        if rezultat["status"]!="OK":
            await ctx.send("Čini se da je Codeforces srušen trenutno, pa ne mogu napraviti što trenutno tražiš od mene :cry:")
            await ctx.send("Pokušaj kasnije...")
            return;
        for problem in (rezultat["result"]["problems"]):
            x = Zadatak(problem['name'], 0.0, ime, str(id) + "/" + problem['index'], ",".join(problem['tags']), editorial)
            sendS = await ctx.send(str(x) + "\nJesi li siguran da želiš dodati zadatak?\nKao potvrdu, stavi 👍 ovu poruku!")
            await sendS.add_reaction('👍' )
            try:
                reaction, _ = await self.bot.wait_for('reaction_add', check=lambda r, u: r.emoji=='👍'  and r.message.id == sendS.id and u == ctx.author, timeout=10)
            except asyncio.TimeoutError:
                await sendS.remove_reaction('👍', self.bot.user)
                await ctx.send(str(x) + " nije dodan")
                continue
            zadatci.append(x)
            await ctx.send("Dodan zadatak: " + str(x))
        await UPDATE_ZADATCI()
        await ctx.send("Natjecanje dodano!")

    @commands.command(name='add_editorial', brief="Dodaje editorijal svim zadatcima s istog natjecanje", help='Dodaje editorijal svim zadatcima s zadanog natjecanja.\nArgument id je contest id na codeforcesu (šesteroznamenkasti broj u linku na contest)\nEditorial je link na editorial (na grupnom blogu).')
    async def add_editorial(self, ctx, id, editorial):
        if not (await IsBotAdmin(ctx)): return;
        
        for i in range(len(zadatci)):
            if id == (zadatci[i].izvor.split('/'))[0]:
                zadatci[i] = zadatci[i]._replace(ans=editorial)
        await UPDATE_ZADATCI()
        await ctx.send("Editorial dodano!")
