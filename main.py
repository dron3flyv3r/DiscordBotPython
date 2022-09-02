from dotenv import load_dotenv
import discord
import os
import torch
import read


########## LOADING PIZZA MODEL ##########
device = torch.device({torch.cuda.is_available(): 'cuda:0', torch.has_mps: 'mps'}.get(True, 'cpu'))
checkpoint = torch.load(r"best.pth.tar", map_location=device)

model = checkpoint['model']
classes = checkpoint['classes']
tran = checkpoint['transform']
########################################

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
client = discord.Client(intents=discord.Intents.all())

######### DISCORD BOT #########
roles = []
with open("roles.txt", "r") as f:
    for line in f:
        roles.append(line.strip().split(","))
ADMIN = ["UwU", "dev"]
###############################

@client.event
async def on_ready():
    Text = ""
    print("We have logged in as {0.user}".format(client))
    Channel = client.get_channel(1014891287809359882)
    await Channel.purge(limit=100)
    await Channel.send("Hello\nI'm a bot that can classify pizza images\nTo use me just send me a pizza image\nI will reply with my prediction\n\nI'm still in development so if you have any suggestions or find any bugs please notify the developer\n\n@drone#4581")
    
    rolCha = client.get_channel(1014972524917956628)
    await rolCha.purge(limit=100)
    
    for role in roles:
        Text += f"{role[0]} : {role[1]}\n"
        
    mes = await rolCha.send(Text)
    
    for role in roles:
        await mes.add_reaction(role[0])

    
@client.event
async def on_message(message):
    if not message.content.startswith('!'): return
    
    userName = str(message.author).split('#')[0]
    userMessage = message.content
    channel = message.channel
    role = message.author.top_role
    
    try: url = message.attachments[0].url 
    except: url = None
    
    print(f"username: {userName}, userMessage: {userMessage}, channel: {channel}, url: {url}, role: {role}")
    
    if message.author.name == client.user:
        return
        
    if message.channel.name in ["bot-chat", "ai-chat", "general-chat"]:
        match message.content.lower():
            
            case "!ping":
                await channel.send("Pong!")
                        
            case "!bot":
                await channel.send(f"Hello {userName} I'm just like you... a bot 😎")
            
            case "!rick":
                # quote a random rick quote
                random_quote = read.get_random_quote()
                await channel.send("")
                
            case "!":
                await channel.send("I think you forgot something")
            
            case "!help":
                await channel.send("!bot - tells you what I am\n!rick - tells you a quote from Rick and Morty\n!ping - pong\n!help - this message")

            case "!pizza":
                if url is None:
                    await channel.send("Please attach an image to your message 😊")
                else:
                    await channel.send(read.classify(model, url, tran, ["is a pizza🍕", "is not a pizza"], device))
    
    if message.channel.name == "general":
        
        match userMessage.lower().split(' ')[0]:
            case "!add":
                if message.author.top_role.name in ADMIN:
                    if len(userMessage.split(" ")) > 2:
                        roles.append([str(userMessage.split(" ")[1]).replace(" ", "").replace(",", ""), userMessage.split(",")[1], str(userMessage.split(",")[2]).replace(" ", "")])
                        print(roles)
                        await channel.send("Role added")
                    else:
                        await channel.send("Please use the following format: !add [emoji], [text], [role]\nExample: !add, 💛, Yello color, yello")
            
            case "!remove":
                if message.author.top_role.name in ADMIN:
                        for role in roles:
                            if role[2] == userMessage.split(" ")[1]:
                                roles.remove(role)
                                await channel.send("Role removed")
                                break
                        else:
                            await channel.send("Role not found [use the role name]")
            
            case "!roles":
                Text = ""
                for role in roles:
                    Text += f"{role[0]} : {role[1]}\n"
                mes = await channel.send(Text)
                
                for role in roles:
                    await mes.add_reaction(role[0])
            
            case "!save":
                if message.author.top_role.name in ADMIN:
                    with open("roles.txt", "w") as file:
                        for role in roles:
                            file.write(f"{role[0]},{role[1]},{role[2]}\n")
                    await channel.send("Roles saved")
                    
    if userMessage.lower().split(" ")[0] == "!clear":
        if message.author.top_role.name in ADMIN:
            clearNum = int(userMessage.split(" ")[1]) if len(userMessage.split(" ")) > 1 else 100
            try:
                await channel.purge(limit=clearNum+1)
            except Exception:
                await channel.send("Something went wrong😕, please notify the developer with the following message: " + str(Exception))
                
    if userMessage.lower() == "!roles" and not message.channel.name == "general":
        if message.author.top_role.name in ADMIN:
                Text = ""
                for role in roles:
                    Text += f"{role[0]} : {role[1]}\n"
                mes = await channel.send(Text)
                
                for role in roles:
                    await mes.add_reaction(role[0])

@client.event
async def on_reaction_add(reaction, user):
    if user.name == client.user.name: return
    Channel = client.get_channel(1014972524917956628)
    if reaction.message.channel.id != Channel.id:
        return
    try:
        for role in roles:
            if str(role[0]) == str(reaction):
                #await Channel.send(f"{user.mention} has been given the {role[2]} role")
                await user.add_roles(discord.utils.get(user.guild.roles, name=str(role[2])))
                break
    except Exception:
        await Channel.send("Something went wrong😕, please notify the developer (drone#4581) with the following message: " + str(Exception))

@client.event
async def on_reaction_remove(reaction, user):
    Channel = client.get_channel(1014972524917956628)
    if reaction.message.channel.id != Channel.id:
        return
    try:
        for role in roles:
            if str(role[0]) == str(reaction):
                    Role = discord.utils.get(user.guild.roles, name=role[2])
                    await user.remove_roles(Role)
                    break
    except Exception:
       await Channel.send("Something went wrong😕, please notify the developer (drone#4581) with the following message: " + str(Exception))  

client.run(TOKEN)