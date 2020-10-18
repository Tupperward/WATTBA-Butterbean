#Butterbean DiscordBot for WATTBA Discord 
#author: Tupperward
#content contributors: Smoltz, Jackapedia

#Thank you to Agnes(Smyrna) for providing guidance throughout the whole process

#Importing dependencies
import discord, os , random, psycopg2, asyncio
from discord.ext import commands, tasks
from discord.utils import get

from bobross import rossQuotes, embedRossIcon, pickRandomLine
from bovonto import embedBovontoIcon, pitches, makePitch, pickRandomLine
from tarot_data import tarotData
from config import config



#-----------Buttons!-----------#
bovontoSchedule = False

#-----------Intializing functions-----------#
client = commands.Bot(command_prefix='!', description='Butterborg is online.', add=True)

#-----------Intializing ready-----------#   
@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('-------')
    print('Resistance is futile.')

params = config()
conn = psycopg2.connect(**params)
cur = conn.cursor()

greetMessage = "Welcome to the WATTBA-sistance! Please take your time to observe our rules and, if you're comfortable, use the **!callme** command to tag yourself with your pronouns. Available pronouns are **!callme he/him**, **!callme she/her**, **!callme they/them**, **!callme xe/xem** and **!callme ze/zir** If you get tired of your pronouns you can remove them with **!imnot** \n\n There are several other roles you can **!join** too, like **!join streampiggies** to be notified of Eli's streams. Check them out by using **!listroles**. \n\n Oh, and feel free to get an inspirational Bob Ross quote any time with **!bobross**. \n\n This server also uses this bot for meme purposes. Be on the lookout for memes you can send using by sending **!bb** and the name of the meme. You can find a list of those memes with **!beanfo**"
timeyIcon = 'https://i.imgur.com/vtkIVnl.png'
unapprovedDeny = "Uh uh uh! {0} didn't say the magic word!\nhttps://imgur.com/IiaYjzH.gif"

#---------------- Helper functions ----------------
#Cleans up returned values from databases
def listToString(s):
    str1 = " "
    return (str1.join(s).replace(" ", ", "))

#Checks to determine if user is approved to add/remove to Butterbean
async def checkApprovedUsers(user):
    lookupString = "SELECT username FROM approved_users WHERE username LIKE  '%{}%';".format(user)
    cur.execute(lookupString)
    check = cur.fetchone()
    if not check is None:
        return True

# ---------------- Meme Management ----------------
#Message Send with !bb arg
@client.command()
async def bb(ctx, arg):
    params = config()
    conn = psycopg2.connect(**params)
    cur = conn.cursor()

    search = arg.lower()
    lookupString = "SELECT link FROM posts WHERE post_name LIKE '%{}%';".format(search)
    cur.execute(lookupString)
    response = cur.fetchone()
    conn.close()
    if response is None:
        await ctx.send("Sorry, this command doesn't exist.")
    else:
        split = response[0].replace("'",'')
        await ctx.send(split)

#Mods can add items to the list
@client.command()
async def add(ctx, key, val):
    params = config()
    conn = psycopg2.connect(**params)
    cur = conn.cursor()
    key = key.lower()

    if await checkApprovedUsers(ctx.message.author):
        lookupString = "INSERT INTO posts VALUES ('{0}','{1}');".format(key,val)
        cur.execute(lookupString)
        conn.commit()
        conn.close()
        await ctx.send("{} has been added to my necroborgic memories".format(key))
    else:
        await ctx.send(unapprovedDeny.format(ctx.message.author))

#Mods can remove items from the list
@client.command()
async def remove (ctx, key): 
    params = config()
    conn = psycopg2.connect(**params)
    cur = conn.cursor()
    key = key.lower()

    if await checkApprovedUsers(ctx.message.author):

        lookupString = "DELETE FROM posts WHERE post_name LIKE '%{}%';".format(key)
        cur.execute(lookupString)
        conn.commit()
        conn.close()
        await ctx.send("{} has been purged from my necroborgic memories".format(key))
    else:
        await ctx.send(unapprovedDeny.format(ctx.message.author))

#Lists all meme commands
@client.command()
async def beanfo(ctx):
    params = config()
    conn = psycopg2.connect(**params)
    cur = conn.cursor()
    
    cur.execute('SELECT post_name FROM posts;')
    info = cur.fetchall()
    finalList = []
    for i in info:
        finalList.append(i[0].replace("'",''))

    conn.close()
    await ctx.send(listToString(finalList))
    

# ---------------- New Member Welcome ----------------
#Welcomes a new member
@client.event
async def on_member_join( member):
    guild = member.guild
    if guild.system_channel is not None:
        eMessage = discord.Embed(description="{0.mention}! {1}".format(member, greetMessage))
        eMessage.set_author(name='Timey', icon_url=timeyIcon)
        await guild.system_channel.send(embed=eMessage)

#If needed, will resend the welcome message
@client.command()
async def resend(ctx):
    eMessage = discord.Embed(description="{0}".format(greetMessage))
    eMessage.set_author(name='Timey', icon_url=timeyIcon)
    await ctx.send(embed=eMessage)


# ---------------- Sending random messages ----------------
#Bob Ross quote
@client.command()
async def bobross (ctx):
# Posts quotes of Bob Ross
    await ctx.send(embed=pickRandomLine(name='Bob Ross',icon=embedRossIcon, lines= rossQuotes))



#Just sends a damn Bovonto pitch
@client.command()
async def bovonto (ctx):
    await ctx.send(embed=pickRandomLine(name='Bovonto Bot',icon=embedBovontoIcon,lines=pitches))

#---------------- Role management functions ----------------
#Adds a pronoun specific role
@client.command()
async def callme (ctx, genderName):
    user = ctx.message.author
    genderId = get(ctx.guild.roles, name=genderName)
    #This checks the list of roles on the server and the order they're in. Do not fuck with the order on the server or this will fuck up.
    upperDemarc = get(ctx.guild.roles, name='he/him'); lowerDemarc = get(ctx.guild.roles, name='Catillac Cat')
    if genderId > upperDemarc or genderId <= lowerDemarc:
        await ctx.send('<:rudy:441453959215972352> Oooooh, {0} isn\'t as sneaky as they think they are. '.format(user.mention))
    elif genderId <= upperDemarc and genderId > lowerDemarc:
        userRoles = ctx.author.roles
        if genderId in userRoles:
            await ctx.send('<:rudy:441453959215972352> You already have {0} pronouns.'.format(genderName))
        if genderId not in userRoles:
            await user.add_roles(genderId)
            await ctx.send('<:heathsalute:482273509951799296> Comrade {0} wants to be called {1}.'.format(user.mention, genderName))

#Removes a pronoun specific role          
@client.command()
async def imnot(ctx, oldRole):
    user = ctx.message.author
    roleToRemove = get(ctx.guild.roles, name=oldRole)
    userRoles = ctx.author.roles
    await user.remove_roles(roleToRemove)
    await ctx.send('<:heathsalute:482273509951799296> Comrade {0} no longer wants to be called {1}.'.format(user.mention, oldRole))
    if roleToRemove not in userRoles:
        await ctx.send("<:rudy:441453959215972352> You never picked those pronouns.")

#Adds a non-pronoun specific role
@client.command()
async def join(ctx, newRole):
    user = ctx.message.author
    roleToAdd = get(ctx.guild.roles, name=newRole.lower())
    lowerDemarc = get(ctx.guild.roles, name='Catillac Cat')
    if roleToAdd >= lowerDemarc:
        await ctx.send("<:rudy:441453959215972352> That's not what this is for.")
    else:
        await user.add_roles(roleToAdd)
        await ctx.send('<:heathsalute:482273509951799296> {0} has joined {1}!'.format(user.mention, newRole))

#Removes a non-pronoun specific role
@client.command()
async def leave(ctx, oldRole):
    user = ctx.message.author
    roleToRemove = get(ctx.guild.roles, name=oldRole.lower())
    userRoles = ctx.author.roles
    await user.remove_roles(roleToRemove)
    await ctx.send('{0} is no longer a member of {1}.'.format(user.mention, oldRole))
    if roleToRemove not in userRoles:
        await ctx.send("<:rudy:441453959215972352> You were never in that role.")

#Lists unformatted all roles.  
@client.command()
async def listroles(ctx):
    rolesStr = ''
    roles = ctx.guild.roles
    for i in roles:
        rolesStr += " " + str(i) +","
    await ctx.send(rolesStr)

#Creates a looped task to execute the Bovonto pitches regularly
while bovontoSchedule == True:
   client.loop.create_task(makePitch())

#---------------- Tarot functions ----------------
# single card draw
@client.command(brief='Single card tarot draw', help='Draws a random card from a 78 card Rider-Waite tarot deck, including reversed cards.')
async def tarot(ctx):
    if '__template' in tarotData:
        await ctx.send('Oops, someone needs to put a proper tarot deck into my brain first!')
    else:
        if 'deck' in tarotData:
            card_index = random.randint(0, len(tarotData['deck'])-1)
            card = tarotData['deck'][card_index]
            emb = discord.Embed(type='rich', title=card['title'], description=card['meaning'], url=card['url'])
            emb.add_field(name='Keywords', value=', '.join(card['keywords']) )
            emb.add_field(name='Yes/No?', value=card['yesno'])
            emb.set_image(url=card['image'])
            emb.set_footer(text='Images © Labyrinthos LLC')
            await ctx.send('{0.display_name}, you have drawn: '.format(ctx.message.author), embed=emb)
        else:
            await ctx.send('Oops, I do not seem to have a valid tarot deck loaded, sorry!')


#Actually running the damn thing
client.run(os.environ['BOT_TOKEN'])