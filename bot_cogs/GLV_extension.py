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

korisnici = None
contests = None
zadatci = None
botlocal = None

TOKEN, KEY, SECRET, GROUP_LINK = None, None, None, None

class User (NamedTuple):
    ime: str = "Null"         ### discord username
    did: str = "Null"          ### discord id
    CF: str = "Null"           ### CF username
    CSES: str = "Null"       ### CSES username
    AT: str = "Null"          ### AT username
    solve: list = []         ### zadatci = 2 ako nije pokušavano / 1 ako je pokušavano / 0 ako je riješeno

def setup(bot):
    print('GLVoni se loada.')
    with open("data_bases/secret.bot") as fp:
        global TOKEN, KEY, SECRET, GROUP_LINK
        TOKEN = fp.readline().replace('\n','')
        KEY = fp.readline().replace('\n','') 
        SECRET = fp.readline().replace('\n','')
        GROUP_LINK = fp.readline().replace('\n', '')
    bot.add_cog(GLV_cog(bot))

def teardown(bot):
    print('GLVoni se unloada.')
    bot.remove_cog('GLVoni')

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

async def IsBotAdmin (ctx):
    role = discord.utils.get(ctx.guild.roles, name="BotAdmin")
    if not(role in ctx.author.roles):
        await ctx.send("Sorry, nisi Tech_support! :stuck_out_tongue_winking_eye:")
        return 0;
    return 1;   


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


async def CF_UPIT(username, id):
    curtime = int(time.time())
    myrand = random.randint(100000, 999999)
    try_to_hash = str(myrand)+"/contest.status?apiKey="+KEY+"&contestId="+str(id)+"&handle="+username+"&time="+str(curtime)+"#"+SECRET
    myhash = hashlib.sha512(bytes(try_to_hash, 'utf-8')).hexdigest()
    link = "https://codeforces.com/api/contest.status?apiKey="+KEY+"&contestId="+str(id)+"&handle="+username+"&time="+str(curtime)+"&apiSig="+str(myrand)+myhash
    for xakfme in range(10):
        ReQuEsT = requests.get(link)
        if ReQuEsT.status_code==200:
            return ReQuEsT.json()
        else: await asyncio.sleep(1)
    ReQuEsT = {'status':'FAIL'}
    return ReQuEsT

########################### GLV naredbe!

class GLV_cog(commands.Cog, name="GLVoni", description="Sve naredbe koje podržavaju rad s našom grupom na codeforcesu i zadatcima u njoj!"):
    def __init__(self, bot):
        global botlocal
        self.bot = botlocal = bot
        global korisnici, zadatci, contests
        korisnici = bot.korisnici
        zadatci = bot.zadatci
        contest = bot.contests

    @commands.command(name='link', brief="Povezuje discord s drugim platformama", help='Koristi se za povezivanje discord računa s drugim platformama. \n;link CF {username} povezuje tvoj discord s codeforces računom. Povezivanje traje do 10 min.  \n;link AT {username} povezuje tvoj discord s atcoder računom. \n;link CSES {username} povezuje tvoj discord s cses računom.')
    async def link(self, ctx, portal, usernamexxx):
        global korisnici
        idx = -1
        for i in range(len(korisnici)):
            if (korisnici[i]).did==str(ctx.author.id):
                idx=i
        if idx==-1:
            korisnici.append(User(normalize(str(ctx.author.nick)), str(ctx.author.id), "Null", "Null", "Null", ([2 for _ in range(len(zadatci))])))
            idx = len(korisnici)-1
            
        if portal == "CF":
            check_problem = list(zadatci[0].izvor.split('/'))
            await ctx.send(ctx.message.author.mention + ' - Molim te, kao ' + usernamexxx + ', predaj kod koji daje COMPILATION_ERROR na zadatak: <https://codeforces.com/group/' + GROUP_LINK + '/contest/'+ check_problem[0] +'/problem/' +check_problem[1]+'>\nImaš 10 minuta kako bi to predao, a zatim ću te obavijestiti jesi li se dobro spojio! :wink:')
            WA=0
            time_start = int(time.time())
            PING = 10
            while time_start + 600 + PING > int(time.time()):
                await asyncio.sleep(PING)
                response = await CF_UPIT(usernamexxx, int(check_problem[0]))
                if response['status']=='OK':    
                    for submition in response['result']:
                        if submition['creationTimeSeconds'] < (int(time.time())-15*60):
                            break
                        if submition['problem']['index']==check_problem[1] and (('verdict' in submition) and submition['verdict']=="COMPILATION_ERROR"):
                            WA=1
                if WA: break
            if WA:
                korisnici[idx]=korisnici[idx]._replace(CF=usernamexxx)
                await ctx.send(ctx.message.author.mention + " je povezan na " + korisnici[idx].CF)
            else:
                await ctx.send(ctx.message.author.mention + " ! Tvoj račun **nije povezan** na  " + usernamexxx)
                
        else:
            if portal=="CSES":
                korisnici[idx]=korisnici[idx]._replace(CSES=usernamexxx)
                await ctx.send(ctx.message.author.mention + " je povezan na " + (korisnici[idx]).CSES)
            elif portal=="AT":
                korisnici[idx]=korisnici[idx]._replace(AT=usernamexxx)
                await ctx.send(ctx.message.author.mention + " je povezan na " + (korisnici[idx]).AT)
            else:
                await ctx.send("Platforma ne postoji!")
        await UPDATE_FILE()

        
    @commands.command(name='gimmeGLV', brief="Zadaje nasumičan zadatak s GLVforces natjecanja", help='Daje nasumičan zadatak težine od 1 do 10, iz nekog područja. \nAko ne želite specifičnu težinu, upišite prvi argument 0. \nAko ne želite specifičnu temu, upišite drugi argument NULL.')
    async def gimmeGLV(self, ctx, tezina='0', podrucje='null'):
        global korisnici, zadatci
        index = -1
        for i in range(len(korisnici)):
            if korisnici[i].did==str(ctx.author.id):
                index=i
        if index==-1 or (korisnici[index].CF).lower=="null":
            await ctx.send("Najprije se moraš prijaviti CF accom: koristi ;link CF {username}")
            return; 
        if not tezina.isdigit():
            tezina, podrucje = podrucje, tezina
            if not tezina.isdigit():
                tezina = '0'
        tezina = float(tezina)
        dostupni=[]
        for i in range(len(zadatci)):
            zad = zadatci[i]
            if (abs(zad.tezina - tezina) <=0.75 or tezina==0) and (podrucje.lower()=='null' or (podrucje.lower() in zad.tags)) and (korisnici[index].solve)[i]:
                dostupni.append(zad)
        if len(dostupni):
            odabir = random.choice(dostupni)
            poruka = 'Preporučam zadatak "'+odabir.ime+'" koji se pojavio na '+odabir.natjecanje+'.\n'
            url = list((odabir.izvor).split('||'))
            for i in range(len(url)):
                url[i] = list((url[i]).split('/'))
            poruka += 'Zadatak je dostupan na: <https://codeforces.com/group/' + GROUP_LINK + '/contest/'+url[0][0]+'/problem/'+url[0][1]+'>\n'
            for i in range(1, len(url)):
                poruka += 'Zadatak je također dostupan i ovdje: <https://codeforces.com/group/' + GROUP_LINK + '/contest/'+url[i][0]+'/problem/'+url[i][1]+'>\n'
            await ctx.send(poruka)
        else:
            await ctx.send('Čini se da ne postoji zadatak koji zadovoljava tvoje argumente! :cry:')

    @commands.command(name='findGLV', brief="Pomaže u pronalaženju zadatka s GLVforces natjecanja", help='Pronalazi zadatak s GLVonija \nArgumenti mogu biti dijelovi imena zadatka, njegove težine, ime natjecanja s kojeg je došao, \nnjegov kod (npr. 260626/A) ili neki njegov tag! Svi argumenti osim težine su stringovi. Neutralan argumen je 0.0 za težinu ili "null" inače! \nArgumenti idu tim redom. Ako argumen ima više riječi, zapiši ih pod navodnicima! Prikazuje prvih n rezultata')
    async def findGLV(self, ctx, ime, težina, natjecanje, kod, tags, n="5"):
        global zadatci
        težina = float(težina)
        n = min(int(n), 10)
        moguci=[]

        for idx in range(len(zadatci)):
            slicnost = 1250
            zad = zadatci[idx]

            if (ime.lower())==((zad.ime).lower()): slicnost-=750
            elif (ime.lower()) in ((zad.ime).lower()): slicnost -=250
            else:
                slicnost-=100
                myime = [0 for _ in range(27)]
                for c in normalize(ime):
                    myime[ord(c)-ord('a')]+=1
                zadime = [0 for _ in range(27)]
                for c in normalize(zad.ime):
                    zadime[ord(c)-ord('a')]+=1
                for _ in range(26):
                    slicnost += abs(myime[_]-zadime[_])*5

            if težina!=0.0:
                slicnost -= 250 - max(0, abs(težina-zad.tezina)-0.37)*73   

            if (natjecanje.lower())==((zad.natjecanje).lower()): slicnost-=500
            elif (natjecanje.lower()) in ((zad.natjecanje).lower()): slicnost -=150
            else:
                slicnost-=10
                myime = [0 for _ in range(27)]
                for c in normalize(natjecanje):
                    myime[ord(c)-ord('a')]+=1
                zadime = [0 for _ in range(27)]
                for c in normalize(zad.natjecanje):
                    zadime[ord(c)-ord('a')]+=1
                for _ in range(26):
                    slicnost += abs(myime[_]-zadime[_])

            if (kod in zad.izvor) and ('/' in kod): slicnost -= 750
            elif kod.isalpha() and (kod in zad.izvor): slicnost -= 250
            elif kod.isnumeric() and (kod in zad.izvor): slicnost -= 500

            tagovi = re.split(',|\\ ', tags)
            while '' in tagovi:
                tagovi.remove('')
            for tag in tagovi:
                if tag in zad.tags:
                    slicnost /= 1.73
           
            moguci.append((slicnost, idx))
        moguci.sort()

        rezultat = "PRONAĐENI ZADATCI:\n"
        for i in range(n):
            rezultat += "Ime zadatka: " + zadatci[(moguci[i])[1]].ime + "\n"
            rezultat += "Težina: " + str(zadatci[(moguci[i])[1]].tezina) + "\n"
            rezultat += "Natjecanje: " + zadatci[(moguci[i])[1]].natjecanje + "\n"
            url = list((zadatci[(moguci[i])[1]].izvor).split('||'))
            for _ in range(len(url)):
                url[_] = list((url[_]).split('/'))
            rezultat += 'Zadatak je dostupan na: <https://codeforces.com/group/' + GROUP_LINK + '/contest/'+url[0][0]+'/problem/'+url[0][1]+'>\n'
            for _ in range(1, len(url)):
                rezultat += 'Zadatak je također dostupan i ovdje: <https://codeforces.com/group/' + GROUP_LINK + '/contest/'+url[_][0]+'/problem/'+url[_][1]+'>\n'
            rezultat += "Tagovi: " + ", ".join((zadatci[(moguci[i])[1]].tags).split(',')) + "\n"
            vjerojatnost = max(1, (moguci[i])[0])
            vjerojatnost = math.log(vjerojatnost)/math.log(37) * 53
            vjerojatnost = max(0.0, 100 - vjerojatnost)
            rezultat += "Odgovara pretraživanju: " + str(round(vjerojatnost, 2)) + "%\n\n"
            if str(round(vjerojatnost, 2))=="0.0":
                break
            
        await ctx.send(rezultat)

    @commands.command(name="solveGLV", brief="U DM šalje editorial za neko natjecanje.", help="Za dani kod natjecanja, npr. 260626, u DM šalje link na editorial, ako editorial postoji u bazi...")
    async def solveGLV(self, ctx, id):
        global zadatci
        link_na_rjesenje = "None"
        for zad in zadatci:
            if id in zad.izvor:
                link_na_rjesenje = zad.ans
                if link_na_rjesenje!="None":
                    break
        if link_na_rjesenje == "None":
            await ctx.send("Nažalost u bazi podataka ne postoji editorial tog natjecanja!")
            return; 
        sendS = await ctx.send("Jesi li siguran da želiš link na rješenje natjecanja " + id + "?\nKao potvrdu, stavi 👍 ovu poruku!")
        await sendS.add_reaction('👍' )
        try:
            reaction, _ = await self.bot.wait_for('reaction_add', check=lambda r, u: r.emoji=='👍'  and r.message.id == sendS.id and u == ctx.author, timeout=60)
        except asyncio.TimeoutError:
            await sendS.remove_reaction('👍' ,self.bot.user)
            return;

        kanal = await ctx.author.create_dm()
        await kanal.send("Evo link: " + str(link_na_rjesenje))

