import os 
import discord
from discord.ext import commands
import pandas
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import asyncio
from youtube_dl import YoutubeDL
from dotenv import load_dotenv
from pandas import *

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")


gauth = GoogleAuth()
gauth.LocalWebserverAuth()
drive = GoogleDrive(gauth)


youtube_dl_opts = {
        'format': 'bestaudio/best',
        'extractaudio': True,
        'audioformat': 'mp3',
        'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
        'restrictfilenames': True,
        'noplaylist': True,
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'auto',
        'source_address': '0.0.0.0',
    }


bot = commands.Bot(command_prefix='==')
@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.dnd ,activity=discord.Activity(type=discord.ActivityType.watching, name="you drive."))
    print("Bot is ready!")

def filetype(file):
    kms =file['title']
    if kms.endswith((".jpg",".png",".jpeg",".jfif",".gif",".zip")):
        kms = "🖼"
    elif kms.endswith((".docx",".pdf","xls","xlsx",".pptx",".html",".txt")):
        kms = "📜"
    elif kms.endswith(".py"):
        kms = "🐍"
    elif kms.startswith("https://www.youtube.com/watch?v="):
        kms= "⏯"
    else:
        kms = "📂"
        
    return kms

def embed_title(ctx,fol):
    embed=discord.Embed(title=f"📂 : {fol}",colour=discord.Colour.gold() )
    embed.set_author(name=ctx.author.display_name,icon_url=ctx.author.avatar_url)
    embed.add_field(name="No.", value="** **", inline=True)
    embed.add_field(name='Title:', value="** **", inline=True)
    embed.add_field(name='File Type:', value="** **", inline=True)
    return embed


def embed_fields(embed,file,x,kms):
    embed.add_field(name="---", value=f"{x})", inline=True)
    embed.add_field(name="---", value=(file['title']), inline=True)
    embed.add_field(name="---", value=kms, inline=True)
    dic[f"{x} id"]=file['id']
    dic[f"{x} title"]=file['title']


@bot.command(name="list")
async def list_command(ctx):
    
    global lis
    lis = [("root","MAIN")]

    fileList = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()

    global dic
    dic={}
    x=1

    fol = "MAIN"
    
    embed = embed_title(ctx,fol)
    embed.set_footer(text = f"Page: 1 / 1")

    for file in fileList:
        kms = filetype(file)
        embed_fields(embed,file,x,kms)
        x+=1
    
    await ctx.send(embed=embed)


global l
l=0
@bot.command(name="open")
async def open_(ctx, stuff=None):
    try:
        global message
        global l

        if l==1:
            await message.clear_reactions()
        
        if stuff==None:
            (val,fol)=lis[-1]
        else:
            istuff = int(stuff)
            val = dic[f"{istuff} id"]
            fol = dic[f"{istuff} title"]
        
        lis.append((val,fol))

        fileList = drive.ListFile({'q': f"'{val}' in parents and trashed=false"}).GetList()
        
        global np
        k= len(fileList)

        if k%7>0:
            np=k//7 + 1
        else:
            np=k//7   

        global cur_page
        cur_page = 1
        x= 7*(cur_page-1)+1

        
        embed = embed_title(ctx,fol)
        

        for file in (fileList[7*(cur_page-1):7*(cur_page)]):
            kms = filetype(file)
            embed_fields(embed,file,x,kms)
            x+=1

        embed.set_footer(text = f"Page: {cur_page}/{np}")

        message = await ctx.send(embed=embed)
        l=1
        

        if np>1:
            await message.add_reaction("◀️")
            await message.add_reaction("▶️")

            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in ["◀️", "▶️"]


            while True:
                try:
                    reaction, user = await bot.wait_for("reaction_add", timeout=60 , check=check)


                    if str(reaction.emoji) == "▶️" and cur_page != np:
                        cur_page += 1
                        x= 7*(cur_page-1)+1

                        embed = embed_title(ctx,fol)
                    
                        for file in (fileList[7*(cur_page-1):7*(cur_page)]):
                            kms = filetype(file)
                            embed_fields(embed,file,x,kms)
                            x+=1


                        embed.set_footer(text = f"Page: {cur_page}/{np}")
                        await message.edit(embed = embed)
                        await message.remove_reaction(reaction, user)
                    
                    elif str(reaction.emoji) == "◀️" and cur_page > 1:
                        cur_page -= 1
                        x= 7*(cur_page-1)+1

                        embed = embed_title(ctx,fol)
                        
                        for file in (fileList[7*(cur_page-1):7*(cur_page)]):
                            kms = filetype(file)
                            embed_fields(embed,file,x,kms)
                            x+=1

                        embed.set_footer(text = f"Page: {cur_page}/{np}")
                        await message.edit(embed = embed)
                        await message.remove_reaction(reaction, user)
                    else:
                        await message.remove_reaction(reaction, user)

                except asyncio.TimeoutError:
                    await message.clear_reactions()
                    break
    except:
        await ctx.send("Tf did you input you lil piece of shit.")


@bot.command(name="close")
async def close_(ctx):
    try:
        if len(lis)<2:
            await ctx.send("Tf are you doing you lil piece of shit.")
        else:
            lis.pop(-1)
            (val,fol)=lis[-1]

            fileList = drive.ListFile({'q': f"'{val}' in parents and trashed=false"}).GetList()
            
            global np
            k= len(fileList)

            
            if k%7>0:
                np=k//7 + 1
            else:
                np=k//7   

            global cur_page
            cur_page = 1
            x= 7*(cur_page-1)+1

            embed = embed_title(ctx,fol)
            
            for file in (fileList[7*(cur_page-1):7*(cur_page)]):
                kms = filetype(file)
                embed_fields(embed,file,x,kms)
                x+=1

            global message
            embed.set_footer(text = f"Page: {cur_page}/{np}")
            message = await ctx.send(embed=embed)

            

            if np>1:
                await message.add_reaction("◀️")
                await message.add_reaction("▶️")

                def check(reaction, user):
                    return user == ctx.author and str(reaction.emoji) in ["◀️", "▶️"]


                while True:
                    try:
                        reaction, user = await bot.wait_for("reaction_add", timeout=60 , check=check)

                        if str(reaction.emoji) == "▶️" and cur_page != np:
                            cur_page += 1
                            x= 7*(cur_page-1)+1

                            embed = embed_title(ctx,fol)
                        
                            for file in (fileList[7*(cur_page-1):7*(cur_page)]):
                                kms = filetype(file)
                                embed_fields(embed,file,x,kms)
                                x+=1


                            embed.set_footer(text = f"Page: {cur_page}/{np}")
                            await message.edit(embed = embed)
                            await message.remove_reaction(reaction, user)
                        
                        elif str(reaction.emoji) == "◀️" and cur_page > 1:
                            cur_page -= 1
                            x= 7*(cur_page-1)+1

                            embed = embed_title(ctx,fol)
                            
                            for file in (fileList[7*(cur_page-1):7*(cur_page)]):
                                kms = filetype(file)
                                embed_fields(embed,file,x,kms)
                                x+=1

                            embed.set_footer(text = f"Page: {cur_page}/{np}")
                            await message.edit(embed = embed)
                            await message.remove_reaction(reaction, user)
                        else:
                            await message.remove_reaction(reaction, user)

                    except asyncio.TimeoutError:
                        await message.clear_reactions()
                        break
    except:
        await ctx.send("Tf did you input you lil piece of shit.")


@bot.command(name="pull")
async def pull_(ctx, stuff):
    try:
        istuff = int(stuff)
        val = dic[f"{istuff} id"]
        await ctx.send(f"https://drive.google.com/file/d/{val}/view?usp=sharing")
    except:
        await ctx.send("Tf did you input you lil piece of shit.")


@bot.command(name="push")
@commands.has_role('Passenger')
async def push(ctx , stuff =None):
    try:
        if stuff == None:
            file1 = drive.CreateFile({"parents": [{"kind": "drive#fileLink", "id": "root"}]})
        else:
            file1 = drive.CreateFile({"parents": [{"kind": "drive#fileLink", "id": dic[f"{stuff} id"]}]})
        file = ctx.message.attachments
        filen = str(file[0])
        filename = filen[77:]
        await file[0].save(filename)
        
        file1.SetContentFile(f"{filename}")
        file1.Upload()
        del file1
        os.remove(f"{filename}")
        await ctx.reply("File pushed.")
    except:
        await ctx.send("Tf did you input you lil piece of shit.")


@push.error
async def push_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.reply("Passenger role is a requirement to use this command!")


@bot.command(name="del")
@commands.has_role('Passenger')
async def del_(ctx,stuff):
    val = dic[f"{stuff} id"]
    fol = dic[f"{stuff} title"]
    file = drive.CreateFile({'id': val})
    file.Delete()
    await ctx.reply(f"{fol} deleted.")


@del_.error
async def push_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.reply("Passenger role is a requirement to use this command!")





@bot.command()
@commands.has_role('Passenger')
async def yt(ctx, link):
    if link.startswith("https://www.youtube.com/watch?v="):
        (val,fol)=lis[-1]
        fileList = drive.ListFile({'q': f"'{val}' in parents and trashed=false"}).GetList()
        fucksgiven =0
        l69 = []
        l420 = []
        with YoutubeDL(youtube_dl_opts) as ydl:
            info_dict = ydl.extract_info(link, download=False)
            video_title = info_dict.get('title', None)

        for file in fileList:
            filename = file['title']
            if filename == ("ytlinks.csv"):
                
                file = drive.CreateFile({'id':file['id']})
                file.GetContentFile('ytlinks.csv')
                data = read_csv("ytlinks.csv")
                l420 = data["title"].tolist()
                l69 = data["link"].tolist()
                l69.append(link)
                l420.append(video_title)
                dic =  {'title': l420 ,'link': l69}
                df = pandas.DataFrame(dic)
                df.to_csv("ytlinks.csv")
                file.SetContentFile("ytlinks.csv")
                file.Upload()
                del file
                os.remove("ytlinks.csv")
                fucksgiven = 1

        if fucksgiven == 0:
            file1 = drive.CreateFile({"parents": [{"kind": "drive#fileLink", "id": val}]})
            l69.append(link)
            l420.append(video_title)
            dic =  {'title': l420 ,'link': l69}
            df = pandas.DataFrame(dic)
            df.to_csv("ytlinks.csv")
            file1.SetContentFile("ytlinks.csv")
            os.remove("ytlinks.csv")
            file1.Upload()
            del file1
            

        await ctx.reply(f"Youtube link successfully added to 📁: {fol}")
    else:
        await ctx.reply("that\'s not a youtube link dumbass")



global g
g=0

@bot.command()
async def videos(ctx):

        global message
        global g
        if l==1:
                await message.clear_reactions()

        (val,fol)=lis[-1]
        fileList = drive.ListFile({'q': f"'{val}' in parents and trashed=false"}).GetList()
        fucksgiven =0

        for file in fileList:
            filename = file['title']
            if filename=="ytlinks.csv":
                file1 = drive.CreateFile({'id':file['id']})
                file1.GetContentFile('ytlinks.csv')
                data = read_csv("ytlinks.csv")
                l420 = data["title"].tolist()
                l69 = data["link"].tolist()
                del file1
                embed = embed_title(ctx,fol)

                k= len(l69)

                if k%7>0:
                    np=k//7 + 1
                else:
                    np=k//7   

                cur_page = 1
                x= 7*(cur_page-1)+1

                if np>1:
                    if cur_page<= np-1:
                        z=7*(cur_page)
                else:
                    z=k%7


                for i in range (7*(cur_page-1),z):
                    title = str(l420[i])
                    link = str(l69[i])
                    embed.add_field(name="---", value=f"{x})", inline=True)
                    embed.add_field(name="---", value=f'[{title}]( {link})' ,inline=True)
                    embed.add_field(name="---", value="⏯", inline=True)
                    x+=1

                message = await ctx.send(embed=embed)
                embed.set_footer(text = f"Page: {cur_page}/{np}")
                g=1

                if np>1:
                    await message.add_reaction("◀️")
                    await message.add_reaction("▶️")

                    def check(reaction, user):
                        return user == ctx.author and str(reaction.emoji) in ["◀️", "▶️"]


                    while True:
                        try:
                            reaction, user = await bot.wait_for("reaction_add", timeout=60 , check=check)

                            if str(reaction.emoji) == "▶️" and cur_page != np:
                                cur_page += 1
                                x= 7*(cur_page-1)+1

                                embed = embed_title(ctx,fol)

                                if np>1:
                                    if cur_page<= np-1:
                                        z=7*(cur_page)
                                    elif cur_page == np:
                                        z=7*(cur_page-1)+k%7
                                else:
                                    z=k%7
                                for i in range (7*(cur_page-1),z):

                                    title = str(l420[i])
                                    link = str(l69[i])
                                    embed.add_field(name="---", value=f"{x})", inline=True)
                                    embed.add_field(name="---", value=f'[{title}]( {link})' ,inline=True)
                                    embed.add_field(name="---", value="⏯", inline=True)
                                    x+=1


                                embed.set_footer(text = f"Page: {cur_page}/{np}")
                                await message.edit(embed = embed)
                                await message.remove_reaction(reaction, user)
                            
                            elif str(reaction.emoji) == "◀️" and cur_page > 1:
                                cur_page -= 1
                                x= 7*(cur_page-1)+1

                                embed = embed_title(ctx,fol)
                                
                                if np>1:
                                    if cur_page<= np-1:
                                        z=7*(cur_page)
                                    else:
                                        z=7*(cur_page-1)+k%7
                                else:
                                    z=k%7
                            
                                for i in range (7*(cur_page-1),z):
                                    title = str(l420[i])
                                    link = str(l69[i])
                                    embed.add_field(name="---", value=f"{x})", inline=True)
                                    embed.add_field(name="---", value=f'[{title}]( {link})' ,inline=True)
                                    embed.add_field(name="---", value="⏯", inline=True)
                                    x+=1

                                embed.set_footer(text = f"Page: {cur_page}/{np}")
                                await message.edit(embed = embed)
                                await message.remove_reaction(reaction, user)
                            else:
                                await message.remove_reaction(reaction, user)

                        except asyncio.TimeoutError:
                            await message.clear_reactions()
                            break

            fucksgiven = 1
        if fucksgiven ==0:
            await ctx.reply ("No videos in this folder.")


bot.run(TOKEN)
