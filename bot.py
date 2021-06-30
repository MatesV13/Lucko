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

VERZIJA_ = "v2.37_2106(dev_alpha)"

print("Program started at", int(time.time()), file=open("data_bases/bot.err", 'w'))
#sys.stderr = open("data_bases/bot.err", 'a')
print("Program started at", int(time.time()), file=open("data_bases/bot.mv", 'w'))
#sys.stdout = open("data_bases/bot.mv", 'a')

print("Program started at", int(time.time()), file=open('data_bases/internet.debug', 'w'))
def printdeb(data):
    with open('data_bases/internet.debug', 'a') as f:
        print(data, file=f, flush=True)

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

zadatci = []
contests = []

CF_problemset = []
CF_ratings = [[] for _ in range (50)]

class User (NamedTuple):
    ime: str = "Null"         ### discord username
    did: str = "Null"          ### discord id
    CF: str = "Null"           ### CF username
    CSES: str = "Null"       ### CSES username
    AT: str = "Null"          ### AT username
    solve: list = []         ### zadatci = 2 ako nije pokušavano / 1 ako je pokušavano / 0 ako je riješeno

korisnici = []

class Speed (NamedTuple):
    did: str = ""
    osobe: None = []
    zadatci: None = []
    rezultati: None = []
    trajanje: int = 90
    kod: int = 0
    raspodijela: str = ""

Dostupni_Speedovi = []

class Prijedlog (NamedTuple):
    autor_did: str = ""
    channel_did: str = ""
    ime: str = ""
    problem: str = ""
    tekst: str = ""
    ogranicenja: str = ""
    rjesenje: str = ""


pending = []

##########################################################################################################################################################################################

with open("data_bases/secret.bot") as fp:         
    TOKEN = fp.readline().replace('\n','')
    KEY = fp.readline().replace('\n','') 
    SECRET = fp.readline().replace('\n','')
    GROUP_LINK = fp.readline().replace('\n', '')
print(str(int(time.time())) + " - loaded SECRET")


PREFIKS_cmd = ';'
intents = discord.Intents.default()
intents.members = True
intents.presences = True
bot = commands.Bot(command_prefix=PREFIKS_cmd, intents=intents, help_command = None)
print("Working " + str(int(time.time())))


##########################################################################################################################################################################################


async def reloadZadatciBot():
    global zadatci
    global contests
    global bot
    zadatci = []
    contests = []
    with open("data_bases/zadatci.bot") as fp: 
        Lines = fp.readlines()
        for contest_id in Lines[0].split('#'):
            try:
                contests.append(int(contest_id))
            except:
                continue
        Lines = Lines[1:]
        for line in Lines:
            podatci = list(line.split('#'))
            if len(podatci)!=6: continue
            iduci_zadatak = Zadatak(podatci[0], float(podatci[1]), podatci[2], podatci[3], podatci[4], podatci[5].replace('\n', ''))
            zadatci.append(iduci_zadatak)
        fp.close()
    bot.contests = contests
    bot.zadatci = zadatci
    print(str(int(time.time())) + " - loaded ZADATCI - " + str(len(zadatci)) + " zadataka.")



async def reloadKorisniciBot():
    global korisnici
    korisnici = []
    with open("data_bases/korisnici.bot") as fp: 
        Lines = fp.readlines() 
        for line in Lines:
            podatci = list(line.split('&'))
            novi_user = User(podatci[0], podatci[1], podatci[2], podatci[3], podatci[4], ([int(i) for i in (podatci[5].replace('\n', ''))]))
            while len(novi_user.solve)<len(zadatci):
                novi_user.solve.append(2)
            korisnici.append(novi_user)
        fp.close()
    bot.korisnici = korisnici
    print(str(int(time.time())) + " - loaded KORISNICI - " + str(len(korisnici)) + " korisnika.")
    


async def reloadCFProblemset():
    global CF_problemset
    global CF_ratings
    ReQuEsT = requests.get("https://codeforces.com/api/problemset.problems")
    if ReQuEsT.status_code!=200:
        print(str(int(time.time())) + " - reloadCFProblemset() FAILED - codeforces proably crashed")
        return;
    CF_problemset = (ReQuEsT.json())["result"]["problems"]
    problem_idx = 0
    while problem_idx < len(CF_problemset):
        problem = CF_problemset[problem_idx]
        if ("rating" not in problem) or ("*special" in problem["tags"]):
            CF_problemset.remove(problem)
        else: problem_idx+=1
            
    bot.CF_problemset = CF_problemset
    
    CF_ratings = [[] for _ in range (40)]
    for i in range(len(CF_problemset)):
        problem = CF_problemset[i]
        CF_ratings[problem["rating"]//100].append(i)

    bot.CF_ratings = CF_ratings
    print(str(int(time.time())) + " - loaded CF problemset - " + str(len(CF_problemset)) + " zadataka.")

    
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
    bot.dostupni_speedovi = Dostupni_Speedovi
    print(str(int(time.time())) + " - loaded SPEEDOVI - " + str(len(Dostupni_Speedovi)) + " speedova.")


async def reloadPendingBot():
    global pending
    pnd = open("data_bases/pending.bot", "r")
    global pending
    for line in pnd.readlines():
        pending.append(eval(line))
    pnd.close()
    bot.pending = pending


##########################################################################################################################################################################################

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
 
async def UPDATE_USER(username):
    global korisnici
    if username=="Null": return
    idx = -1
    for i in range(len(korisnici)):
        if korisnici[i].CF == username:
            idx = i
    if idx==-1: return;
    for id in contests:
        response = await CF_UPIT(username, id)
        if response['status']!='OK':
            print("Greška pri pristupanju: user:'" + username + "' ; contest_id:'" + str(id) + "'")
            continue
        for sub in response['result']:
            kod = str((sub['problem'])['contestId']) + '/' + ((sub['problem'])['index'])
            for i in range(len(zadatci)):
                if kod in zadatci[i].izvor:
                    korisnici[idx].solve[i]=min(korisnici[idx].solve[i], 0 if sub['verdict']=='OK' else 1)
            
async def UPDATE_FILE():
    global korisnici
    f = open("data_bases/korisnici.bot", "w")
    for user in korisnici:
        linija = user.ime + '&' + user.did + '&' + user.CF + '&' + user.CSES + '&' + user.AT + '&'
        for i in user.solve:
            linija+=str(i)
        f.write(linija + '\n')
    f.close()
    bot.korisnici = korisnici
    return;
    
async def UPDATE_USERS():
    global korisnici
    for user in korisnici:
        await UPDATE_USER(user.CF)
    await UPDATE_FILE()
    print(str(int(time.time())) + " Updated - KORISNICI")
    return;

async def UPDATE_SF():
    global Dostupni_Speedovi
    sff = open("data_bases/speed.bot", "w")
    for SF in Dostupni_Speedovi:
        while len(SF.osobe) > len(SF.rezultati):
            SF.osobe.remove(SF.osobe[-1])
        print(SF, file = sff)
    sff.close()
    bot.dostupni_speedovi = Dostupni_Speedovi
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
    bot.contests = contests
    bot.zadatci = zadatci
    return;

async def UPDATE_PENDING():
    global pending
    pnd = open("data_bases/pending.bot", "w")
    for prop in pending:
        pnd.write(str(prop))
    pnd.close()
    bot.pending = pending

async def UpdateDataBases():
    await UPDATE_USERS()
    await UPDATE_SF()
    await UPDATE_ZADATCI()
    await UPDATE_PENDING()
    print("UpdateDataBases!")

async def ReloadDataBases():
    await reloadZadatciBot()
    await reloadKorisniciBot()
    await reloadCFProblemset()
    await reloadSpeedBot()
    await reloadPendingBot()
    print("ReloadedDataBases")
    return;

async def push_to_file():
    (sys.stderr).flush()
    (sys.stdout).flush()
    return;
    
##########################################################################################################################################################################################
            
async def IsBotAdmin (ctx):
    try:
        role = discord.utils.get(ctx.guild.roles, name="BotAdmin")
        if not(role in ctx.author.roles):
            await ctx.send("Sorry, nisi moj šef! :stuck_out_tongue_winking_eye: \nČini se da nemaš potrebne ovlasti da učiniš ovo...")
            return 0;
        else: return 1;
    except:
        return 0;

async def IsBotAdminBool (ctx):
    try:
        role = discord.utils.get(ctx.guild.roles, name="BotAdmin")
        if (role in ctx.author.roles): return 1;   
        else: return 0;
    except:
        return 0;

##########################################################################################################################################################################################

@bot.event
async def on_command_error(ctx, error):
    poruka = "Oh ne! Dogodila se greška pri korištenju zadnje naredbe koju si koristio! " + ctx.author.mention + "\nGreška: " + str(error) + "\n"
    Guild = ctx.guild
    if not(Guild is None):
        role = discord.utils.get(Guild.roles, name="BotAdmin")
        poruka += "Ako ti greška nije jasna, koristi ;help ili kontaktiraj nekog s ulogom " + role.mention + " !"
    await ctx.send(poruka)

@bot.event
async def on_connect():
    printdeb("Bot conntected to Discord at " + str(int(time.time())))

@bot.event
async def on_ready():
    global VERZIJA_
    for guild in bot.guilds:
        print(f'{bot.user} (id: {bot.user.id}) je spojen na {guild.name}(id: {guild.id})')
        if guild.system_channel!=None:
            try:
                message = await guild.system_channel.fetch_message(guild.system_channel.last_message_id)
                assert (message is not None) and (VERZIJA_ in message.content)
                printdeb("Bot called on_ready, but it is already at current version")
            except:
                await (guild.system_channel).send(bot.user.mention + ' je spojen na mrežu, jači no ikada! :partying_face: \nTrenutna verzija je '+ VERZIJA_) 


@bot.event
async def on_resumed():
    printdeb("Bot reconntected to Discord at " + str(int(time.time())))

@bot.event
async def on_disconnect():
    printdeb("Bot disconntected from Discord at " + str(int(time.time())))

@bot.event
async def on_member_join(member):
    pozdrav = "Pozdrav! Ja sam Lucko, bot za discord!\n"
    pozdrav += "Ako te zanimaju naredbe, možeš ih vidjeti koristeći ;help\n"
    pozdrav += "Ne zaboravi promjeniti nick u svoje stvarno ime! :wink:\n"
    pozdrav += "Ako imaš pitanja, kontaktiraj MatesV13#3137 ili nekog drugog s ulogom BotAdmin!"
    pozdrav += "O, i nemoj zaboraviti spojiti svoj CF acc sa discordom - pogledaj detalje naredbe ;link"
    channel = await member.create_dm()
    await channel.send(pozdrav)
    try:
        role = discord.utils.get(member.guild.roles, name="Učenici")
        await member.add_roles(role)
    except:
        ireallydontcareaboutthisexcept=True
    novi_korisnik = User(normalize(str(member)), str(member.id), "Null", "Null", "Null", ([2 for _ in range(len(zadatci))]))
    korisnici.append(novi_korisnik)
    UPDATE_FILE()


########################### Debug naredbe!

class debug_cog(commands.Cog, name="Debug", description="Samo za Admine bota, uglavnom služi za rad s bazama podataka"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='debug', brief="Vraća zapisnike sustava", help='Vraća zapise iz sustavnih datoteka - bot.err (greške), bot.mv (općenito), internet.debug (internet i povezivanje)\nPrima "Da"/"Ne" argumente želiš li zapisnike iz pojedine datoteke\nArgument summary je koliko zadnjih linija trebaš - vjerojatno je zadnjih 20 solidno u većini slučajeva...')
    async def debug(self, ctx, errors_err='Ne', data_mv='Ne', internet_debug='Ne', summary="20"):
        if not (await IsBotAdmin(ctx)): return;
        summary = int(summary)
        await push_to_file()   
        channel = await ctx.author.create_dm()

        if errors_err=='Da':
            await channel.send("### bot.err")
            with open('data_bases/bot.err', 'r') as debugf:
                 data = debugf.readlines()
                 for line in data[-summary:]:
                     await channel.send(line[:-1] + "   \\")
            await channel.send("=== bot.err")

        if data_mv=='Da':
            await channel.send("### bot.mv")
            with open('data_bases/bot.mv', 'r') as debugf:
                 data = debugf.readlines()
                 for line in data[-summary:]:
                     await channel.send(line[:-1] + "   \\")
            await channel.send("=== bot.mv")

        if internet_debug=='Da':
            await channel.send("### internet.debug")
            with open('data_bases/internet.debug', 'r') as debugf:
                 data = debugf.readlines()
                 for line in data[-summary:]:
                     await channel.send(line[:-1] + "   \\")
            await channel.send("=== internet.debug")

    @commands.command(name='update_user', brief="Provjerava što su korisnici riješili", help='Updatea bazu podataka. Može potrajati... \n;update_user all updatea cijelu bazu podataka - potrebna uloga BotAdmin\n;update_user me updatea samo korisnika koji je to zatražio \n;update_user <username> updatea sve korisnike kojima je neko korisničko ime (bilo discord, CF, ATcoder ili CSES) jednako <username>')
    async def update_user(self, ctx, koga="me"):
        if koga=="all":
            if not (await IsBotAdmin(ctx)): return;
            async with ctx.typing():
                await UPDATE_USERS()
            await ctx.send("Updateano!")
        elif koga=="me":
            USER = User()
            for korisnik in korisnici:
                if korisnik.did==str(ctx.author.id):
                    USER = korisnik
            if USER.ime == "Null":
                korisnici.append(User(normalize(str(ctx.author)), str(ctx.author.id), "Null", "Null", "Null", ([2 for _ in range(len(zadatci))])))
            UPDATE_USER(USER)
            await ctx.send("Updateano!")
        else:
            USER = User()
            for korisnik in korisnici:
                if (korisnik.ime.split('#'))[0]==koga or korisnik.ime==koga or korisnik.CF==koga or korisnik.CSES==koga or korisnik.AT==koga:
                    USER = korisnik
                    await UPDATE_USER(USER)
            if USER.ime == "Null":
                await ctx.send("Korisničko ime nije pronađeno! :cry:\nProvjeri da korisnik zaista postoji na serveru!")
            else:
                await ctx.send("Updateano!")
        await UPDATE_FILE()

    @commands.command(name='update_data', brief="Gura lokalnu verziju u bazu podataka", help='Updatea bazu podataka. Može potrajati... Potrebna je uloga BotAdmina\n;update_data users updatea korisnici.bot (efektivno isti kao ;update_user all)\n;update_data speed updatea speed.bot.\nNe preporuča se jer može obrisati trenutne pokušaje rješavanja speedforcesa\n;update_data zadatci updatea zadatci.bot\n;update_data pending updatea pending.bot\n;update_data all updatea cijelu bazu podataka (tj. sve prethodno navedeno)')
    async def update_data(self, ctx, sto):
        if not (await IsBotAdmin(ctx)): return;
        await ctx.send("Trebat će mi sekunda...")
        async with ctx.typing():
            if sto=="users" or sto=="all":
                await UPDATE_USERS()
                await ctx.send("Korisnici updateani!")
            if sto=="speed" or sto=="all":
                await UPDATE_SF()
                await ctx.send("Speedforcesi updateani!")
            if sto=="zadatci" or sto=="all":
                await UPDATE_ZADATCI()
                await ctx.send("Zadatci updateani!")
            if sto=="pending" or sto=="all":
                await UPDATE_PENDING()
                await ctx.send("Pending updateani!")
        await ctx.send("Update uspješan!")

    @commands.command(name='reload', brief="Briše radnu verziju podataka i učitava one iz baze podataka", help='Poziva funkciju koja učitava podatke iz baze podataka (piše preko radne verzije). Argumenti su:\nSpeedBot - reload speed.bot\nCFProblemset - reload codeforces problemset\nKorisniciBot - reload korisnici.bot\nZadatciBot - reload zadatci.bot\nPendingBot - reload pending.bot\nALL - reload sve navedeno')
    async def reload(self, ctx, sto):
        if not (await IsBotAdmin(ctx)): return;
        async with ctx.typing():
            if sto=="SpeedBot":
                await reloadSpeedBot()
                await ctx.send("reloaded speed.bot")
            elif sto=="CFProblemset":
                await reloadCFProblemset()
                await ctx.send("reloaded codeforces problemset")
            elif sto=="KorisniciBot":
                await reloadKorisniciBot()
                await ctx.send("reloaded korisnici.bot")
            elif sto=="ZadatciBot":
                await reloadZadatciBot()
                await ctx.send("reloaded zadatci.bot")
            elif sto=="PendingBot":
                await reloadPendingBot()
                await ctx.send("reloaded pending.bot")
            elif sto=="ALL":
                await ReloadDataBases()
                await ctx.send("ALL reloaded!")
            else:
                await ctx.send("Ključna riječ nije prepoznata...")
        await ctx.send("Reload uspješan!")

    @commands.command(name='update_bot', brief='Aktivira promjene u cogovima', help="Kao argument prima naziv coga (tj. ekstenzije) iz skupa\n['Admin', 'CF', 'Custom', 'GLV', 'GLVforces', 'Lockout', 'Speed']\nPričekaj poruku o uspješnosti učitavanja.\n\nUkoliko učitavanje ne uspije, u botu ostaje učitan stara verzija.")
    async def update_bot(self, ctx, what="All"):
        if not (await IsBotAdmin(ctx)): return;

        await ctx.send("Update zapoceo!")
        if what=="Admin" or what=="All":
            self.bot.reload_extension('bot_cogs.Admin_extension')
            await ctx.send("Admin_extension je uspješno učitan!")
        if what=="CF" or what=="All":
            self.bot.reload_extension('bot_cogs.CF_extension')
            await ctx.send("CF_extension je uspješno učitan!")
        if what=="Custom" or what=="All":
            self.bot.reload_extension('bot_cogs.Custom_extension')
            await ctx.send("Custom_extension je uspješno učitan!")
        if what=="GLV" or what=="All":
            self.bot.reload_extension('bot_cogs.GLV_extension')
            await ctx.send("GLV_extension je uspješno učitan!")
        if what=="GLVforces" or what=="All":
            self.bot.reload_extension('bot_cogs.GLVforces_extension')
            await ctx.send("GLVforces_extension je uspješno učitan!")
        if what=="Lockout" or what=="All":
            self.bot.reload_extension('bot_cogs.Lockout_extension')
            await ctx.send("Lockout_extension je uspješno učitan!")
        if what=="Speed" or what=="All":
            self.bot.reload_extension('bot_cogs.Speed_extension')
            await ctx.send("Speed_extension je uspješno učitan!")
            
        await ctx.send("Update uspješan!")


    @commands.command(name='kill', brief="Gasi bota", help='Gasi bota te se brine da su sve baze podataka uredno spremljene!')
    async def kill(self, ctx):
        if not (await IsBotAdmin(ctx)): return;
        global VERZIJA_
        sendS = await ctx.send("Jesi li siguran da želiš završiti program?\nKao potvrdu, stavi :thumbsup: na u poruku! Trenutna verzija je " + VERZIJA_)
        await sendS.add_reaction('👍' )
        try:
            reaction, _ = await bot.wait_for('reaction_add', check=lambda r, u: r.emoji=='👍'  and r.message.id == sendS.id and u == ctx.author, timeout=60)
        except asyncio.TimeoutError:
            await ctx.send("Prošlo je previše vremena, pa je zahtjev zanemaren i bot se neće ugasiti...")
            await sendS.remove_reaction('👍' , bot.user)
            return;
        
        await ctx.send("Samo sekundicu da sve dovršim...")
        try:
            async with ctx.typing():
                await UpdateDataBases()
                await push_to_file()
        except:
            sendS = await ctx.send("Čini se da trenutno imam problema sa spremanjem nekih datoteka...\nŽeliš li me svejedno ugasiti? Kao potvrdu, stavi :thumbsup: na u poruku!")
            await sendS.add_reaction('👍' )
            try:
                reaction, _ = await bot.wait_for('reaction_add', check=lambda r, u: r.emoji=='👍'  and r.message.id == sendS.id and u == ctx.author, timeout=60)
            except asyncio.TimeoutError:
                await ctx.send("Prošlo je previše vremena, pa je zahtjev zanemaren i bot se neće ugasiti...")
                await sendS.remove_reaction('👍' , bot.user)
                return;
        
        print("kill called at " + str(int(time.time())) + " by " + normalize(str(ctx.author)) + "(id=" + str(ctx.author.id) + ")")
        await ctx.send("Do sljedećeg druženja! :heart:")
        await bot.close()
        await client.close()
        sys.exit()

@bot.command(name="help", help="Fascinantno da ne znaš kako help funkcionira\nLjubi te Mathej :heart:")
async def help(ctx, input=""):
    global PREFIKS_cmd
    if len(bot.cogs)==0:
        poruka = discord.Embed(title="GENIJE", color=0x0000ff, description=("Možda bi bilo dobro da netko pokrene bota?\nKoristi `"+PREFIKS_cmd+"START`"))
        await ctx.send(embed=poruka)
        return;
        
    DODATCI = ["Codeforces", "Custom", "GLVoni", "Speedforces", "Lockout", "Admin", "Debug", "GLVforces"];
    if len(input)==0:
        poruka = discord.Embed(title="Naredbe", color=0x6080ff, description=("Koristi `"+PREFIKS_cmd+"help <ime naredbe>` za više informacija o pojedinoj naredbi"))
        for ime in DODATCI[0:(8 if (await IsBotAdminBool(ctx)) else 5)]:
            try:
                cog = bot.get_cog(ime)
                naredbe = f' - {cog.description}\n\n' 
                for naredba in cog.get_commands():
                    naredbe += f'\t`{PREFIKS_cmd}{naredba.name}` - {naredba.brief}\n'
                poruka.add_field(name=cog.qualified_name, value=naredbe, inline=False)
            except:
                naredbe = ""
        await ctx.send(embed=poruka)
        
    else:
        naredba = bot.get_command(input)
        if naredba is None:
            poruka = discord.Embed(color=0xeeee00, description=("Čini se da ne postoji naredba "+PREFIKS_cmd+input+"\nProvjeri slovkanje ili se obrati tehničkoj podršci! :heart:"))
            await ctx.send(embed=poruka)
        else:
            opis = ""
            if len(naredba.clean_params):
                opis = "Argumenti (redom po unosu):\n"
            for key, value in (naredba.clean_params).items():
                if '=' in str(value):
                    opis += "Opcionalni argument [" + str(value) + "]\n"
                else:
                    opis += "Obavezan argument <" + str(value) + ">\n"
            opis += "\n" + naredba.help
            poruka = discord.Embed(title=(PREFIKS_cmd+input), color=0xFFA000, description=opis)
            await ctx.send(embed=poruka)
    return;

@bot.command(name='START')
async def START(ctx):
    await ctx.send("Pokušavam učitati sve potrebno!")
    await ReloadDataBases()
    try:
        bot.add_cog(debug_cog(bot))
        bot.load_extension('bot_cogs.Admin_extension')    
        bot.load_extension('bot_cogs.GLV_extension')
        bot.load_extension('bot_cogs.CF_extension')
        bot.load_extension('bot_cogs.Lockout_extension')
        bot.load_extension('bot_cogs.Speed_extension')
        bot.load_extension('bot_cogs.GLVforces_extension')
        bot.load_extension('bot_cogs.Custom_extension')
        await ctx.send("Sve je učitano!")
        print("Sve baze uspješno učitane!")
        bot.remove_command("START")
    except:
        await ctx.send("Bot **NIJE** uspješno učitan... \nGreška glasi: " + str(sys.exc_info()[0]) + "\nDaj odi reci Mateju da je glup...")
bot.run(TOKEN)
