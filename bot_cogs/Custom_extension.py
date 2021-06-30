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

custom_commands = dict()

def ReloadCCommands():
    global custom_commands
    custom_commands.clear()
    with open("data_bases/ccommands.bot", 'r') as fp: 
        custom_commands = eval(fp.readline())

ReloadCCommands()

def UpdateCComands():
    global custom_commands
    f = open("data_bases/ccommands.bot", 'w')
    f.write(str(custom_commands))


def setup(bot):
    print('Custom se loada!')
    bot.add_cog(custom_cog(bot))

def teardown(bot):
    print('Custom se unloada!')
    bot.remove_cog("Custom")


class custom_cog(commands.Cog, name="Custom", description="Ovaj je cog samo za vas - nema ograničenja, nema provjeravanja... Go crazy!"):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_message(self, message):
        ctx = await self.bot.get_context(message)
        global custom_commands
        did_something=0
        if message.content.startswith('$'):
            ccommand = ((message.content.split())[0])[1:]
            if ccommand in custom_commands.keys():
                await ctx.send(custom_commands[ccommand])
            else:
                await ctx.send("You talking to me? Nezz za tu naredbu...")
    
    @commands.command(name='add_cc', brief="Dodaje custom naredbu", help='Dodaje custom naredbu\n;add_cc <ime> <tekst>')
    async def add_cc(self, ctx, ime, *, odgovor):
        if ime in custom_commands.keys():
            await ctx.send("Custom naredba se već koristi")
            return;
        for cm in self.bot.commands:
            if cm.name == ime:
                await ctx.send("Ova naredba već postoji kao stvarna naredba")
                return;
        custom_commands[ime] = odgovor
        UpdateCComands()
        await ctx.send("Naredba dodana! Možeš ju koristiti kao $" + ime + " -> " + odgovor)

    @commands.command(name='del_cc', brief="Miče custom naredbu", help='Miče custom naredbu\n;del_cc <ime>')
    async def del_cc(self, ctx, ime):
        if ime in custom_commands.keys():
            odgovor = custom_commands[ime]
            del custom_commands[ime]
            UpdateCComands()
            await ctx.send("Naredba obrisana! Zadnji put vidimo $" + ime + " -> " + odgovor)
        else:
            await ctx.send("Ne postoji navedena custom naredba")

    @commands.command(name='help_cc', brief="Vraća popis dostupnih naredbi", help='Vraća sve custom naredbe')
    async def help_cc(self, ctx):
        tekst = ""
        for x in custom_commands.keys():
            tekst += "`$" + x + "`\n"
        poruka = discord.Embed(title="Naredbe", color=0x6080ff, description=tekst)
        await ctx.send(embed=poruka)


