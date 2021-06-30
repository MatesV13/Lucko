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
    print('GLVforces se loada!')
    bot.add_cog(GLVforces_cog(bot))

def teardown(bot):
    print('GLVforces se unloada!')
    bot.remove_cog('GLVforces')

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


class Prijedlog (NamedTuple):
    autor_did: str = ""
    channel_did: str = ""
    ime: str = ""
    problem: str = ""
    tekst: str = ""
    ogranicenja: str = ""
    rjesenje: str = ""


pending = []
localbot = None
    
async def UPDATE_pending():
    global pending, localbot
    pnd = open("data_bases/pending.bot", "w")
    for prop in pending:
        pnd.write(str(prop))
    pnd.close()
    localbot.pending = pending


def get_prop(x):
    try:
        poruka = discord.Embed(title=x.ime, color=0x0ccf0c, description=x.problem)
        poruka.add_field(name="Ograničenja", value=x.ogranicenja, inline=False)
        if ";rjesenje" not in x.rjesenje:
            poruka.add_field(name="Rješenje", value=x.rjesenje, inline=False)
        return poruka
    except:
        return discord.Embed(title="Zadatak se ne može učitati", color=0x0000ff, description=("Čini se da se dogodila fatalna greška pri učitavanju izgleda zadatka..."))

class GLVforces_cog(commands.Cog, name="GLVforces", description="Podrška za Autore natjecanja i predlaganje problema"):
    def __init__(self, bot):
        global localbot
        self.bot = bot
        localbot = bot
        global pending
        pending = bot.pending
        

    @commands.command(name='propose', brief="Predloži zadatak", help='Predloži zadatak. \nKroz daljnji postupak će te navoditi bot! Slijedi upute')
    async def propose(self, ctx):
        global pending
        if ctx.channel.name!="main" and ctx.channel.category.name!="Prijedlozi":
            await ctx.send("Ovu naredbu ne možeš koristiti ovdje! Možeš ju koristiti samo u kanalu 'main' u kategoriji 'Prijedlozi'!")
            return;

        kategorija = ctx.channel.category
        kanal = await kategorija.create_text_channel("Prijedlog " + str(random.randint(100000, 999999)))
        await kanal.edit(name=("Prijedlog - " + str(ctx.author) + " - " + str(kanal.id)))
        
        await kanal.set_permissions(ctx.guild.default_role, read_messages=False, send_messages=False)
        await kanal.set_permissions(ctx.author, read_messages=True, send_messages=True)
        role = discord.utils.get(ctx.guild.roles, name="GLVoniAutori")
        await kanal.set_permissions(role, read_messages=True, send_messages=True)

        prop = Prijedlog(str(ctx.author.id), str(kanal.id), ("Prijedlog - " + str(ctx.author) + " - " + str(kanal.id)), "Problemski dio zadatka još nije dodan. Dodaj ga koristeći `;problem`", "Tekst zadatka još nije dodan. Dodaj ga koristeći `;tekst`", "Ograničenja zadatka još nisu dodana. Dodaj ih koristeći `;ogranicenja`", "Rješenje zadatka još nije dodano. Dodaj ga koristeći `;rjesenje`")
        pending.append(prop)
        await UPDATE_pending()
        await ctx.message.delete()        
        
        help_poruka = "Id ovog prijedloga je '" + str(kanal.id) + "'\n\n"
        help_poruka += 'Najprije svom zadatku moraš dati ime! \nZa to koristi naredbu ;ime <ime>\n\n'
        help_poruka += 'Zatim dodaj **jednostavan opis** problema koji želiš zadati, bez popratnog teksta. \n'
        help_poruka += 'Ovaj dio pomaže administratorima odrediti težinu i rješenje problema. \nKoristi ;problem <cijeli problem>\n'
        help_poruka += 'Ukoliko već imaš ideju za tekst, **možeš** ga dodati pomoću ;tekst <cijeli tekst>\n\n'
        help_poruka += 'Također, nemoj zaboraviti dodati ograničenja! Koristi ;ogranicenja <sve o ogranicenjima>\n\n'
        help_poruka += 'Ako želiš, možeš nam ostaviti i rješenje svog zadatka (samo opis, ne kod) - koristi ;rjesenje <rješenje>\n\n'
        help_poruka += 'Dakle, da bi prijedlog problema bio uzet u obzir, molim te napiši poruke koje započinju s ;ime, ;problem i ;ogranicenja, te možeš napisati ;tekst i ;rjesenje.\n'
        help_poruka += 'Svaka poruka mora biti poslana odvojeno!\n\n'
        help_poruka += 'Ako u bilo kojem trenutku misliš da nisi zadovoljan s nekim dijelom, možeš ga prepraviti ponovnim korištenjem naredbe.\nTakvi popravci moraju sadržavati cijeloviti tekst jer će se oni snimiti **preko** originala!\n\n'
        help_poruka += 'Izgled svog prijedloga možeš pogledati koristeći ;zadatak\n'
        help_poruka += 'Ako trebaš pomoć gnjavi '
        role = discord.utils.get(ctx.guild.roles, name="GLVoniAutori")
        await kanal.send(help_poruka + role.mention)
        

    @commands.command(name='ime', brief="Mijenja ime zadatka", help='Mijenja ime zadatka. Mora biti korišteno u kanalu u kojem se odvija predlaganje zadatka')
    async def ime(self, ctx, *, input):
        global pending
        chid = ctx.channel.id
        idx = -1
        for i in range (len(pending)):
            prop = pending[i]
            if prop.channel_did==str(chid):
                idx = i
        if idx==-1:
            await ctx.send("Ne možeš koristiti ovu naredbu u ovome kanalu!")
            return;

        pending[i] = pending[i]._replace(ime=input)
        try:
            await ctx.channel.edit(name=(input+" - "+str(ctx.author)))
        except:
            await ctx.send("Fakat si mogo malo skratit ime.")
        await UPDATE_pending()

    @commands.command(name='problem', brief="Mijenja uži tekst zadatka", help='Mijenja uži tekst zadatka. Mora biti korišteno u kanalu u kojem se odvija predlaganje zadatka')
    async def problem(self, ctx, *, input):
        global pending
        chid = ctx.channel.id
        idx = -1
        for i in range (len(pending)):
            prop = pending[i]
            if prop.channel_did==str(chid):
                idx = i
        if idx==-1:
            await ctx.send("Ne možeš koristiti ovu naredbu u ovome kanalu!")
            return;

        pending[i] = pending[i]._replace(problem=input)
        await UPDATE_pending()

    @commands.command(name='tekst', brief="Mijenja tekst zadatka", help='Mijenja tekst zadatka. \nMora biti korišteno u kanalu u kojem se odvija predlaganje zadatka')
    async def tekst(self, ctx, *, input):
        global pending
        chid = ctx.channel.id
        idx = -1
        for i in range (len(pending)):
            prop = pending[i]
            if prop.channel_did==str(chid):
                idx = i
        if idx==-1:
            await ctx.send("Ne možeš koristiti ovu naredbu u ovome kanalu!")
            return;

        pending[i] = pending[i]._replace(tekst=input)
        await UPDATE_pending()

    @commands.command(name='ogranicenja', brief="Mijenja ogranicenja zadatka", help='Mijenja ogranicenja zadatka. \nMora biti korišteno u kanalu u kojem se odvija predlaganje zadatka\nVodi se načelom da bi gornja granica složenosti (bez konstanta) trebala biti oko 2e6-5e6')
    async def ogranicenja (self, ctx, *, input):
        global pending
        chid = ctx.channel.id
        idx = -1
        for i in range (len(pending)):
            prop = pending[i]
            if prop.channel_did==str(chid):
                idx = i
        if idx==-1:
            await ctx.send("Ne možeš koristiti ovu naredbu u ovome kanalu!")
            return;

        pending[i] = pending[i]._replace(ogranicenja=input)
        await UPDATE_pending()

    @commands.command(name='rjesenje', brief="Mijenja rješenje zadatka", help='Mijenja rješenje zadatka. \nMora biti korišteno u kanalu u kojem se odvija predlaganje zadatka\nNE KOMPLICIRAJ DI NE TREBA!')
    async def rjesenje(self, ctx, *, input):
        global pending
        chid = ctx.channel.id
        idx = -1
        for i in range (len(pending)):
            prop = pending[i]
            if prop.channel_did==str(chid):
                idx = i
        if idx==-1:
            await ctx.send("Ne možeš koristiti ovu naredbu u ovome kanalu!")
            return;

        pending[i] = pending[i]._replace(rjesenje=input)
        await UPDATE_pending()

    @commands.command(name='zadatak', brief="Vraća izgled zadatka", help='Vraća izgled zadatka koji se predlaže u danom kanalu!')
    async def zadatak(self, ctx):
        global pending
        chid = ctx.channel.id
        idx = -1
        for i in range (len(pending)):
            prop = pending[i]
            if prop.channel_did==str(chid):
                idx = i
        if idx==-1:
            await ctx.send("Ne možeš koristiti ovu naredbu u ovome kanalu!")
            return;

        await ctx.send(embed=(get_prop(pending[idx])))
        
        
    @commands.command(name='end_propose', brief="Kraj predlaganja zadatka", help='Kraj predlaganja zadatka!\nNajčešće implicira da je zadatak izabran od administratora, ili je zadatak odbačen.\nAutor može ostaviti commit poruku, te će autor zadatka i Autor dobiti kopiju zadatka u DM, te će se kanal obrisati')
    async def end_propose(self, ctx, *, input=""):
        global pending
        chid = ctx.channel.id
        idx = -1
        for i in range (len(pending)):
            prop = pending[i]
            if prop.channel_did==str(chid):
                idx = i
        if idx==-1:
            await ctx.send("Ne možeš koristiti ovu naredbu u ovome kanalu!")
            return;
        prop = pending[idx]

        if str(ctx.author.id)==prop.autor_did:
            Autor = ctx.author
            DM = await Autor.create_dm()
            await DM.send("Sam si odlučio obrisati svoj zadatak " + prop.ime + "\nEvo još jednom tvoj napredak; za uspomenu ako ništa drugo...")
            await DM.send(embed=get_prop(prop))
        else:
            Autor = ctx.author
            DM = await Autor.create_dm()
            await DM.send("Odlučio si završiti zadatak " + prop.ime + "\nEvo zadatka:")
            await DM.send(embed=get_prop(prop))
            
            Autor = await self.bot.fetch_user(prop.autor_did)
            DM = await Autor.create_dm()
            await DM.send(str(ctx.author) + " je odlučio završiti predlaganje tvog zadatak " + prop.ime + "\n(Pri završavanju ostavio je i poruku: '"+input+"')\nEvo zadatka:")
            await DM.send(embed=get_prop(prop))

        await ctx.channel.delete()
        pending.remove(prop)
        await UPDATE_pending()
