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



@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))
    
@client.event
async def on_message(message):
    if message.content.startswith('!'): return
    
    username = str(message.author).split('#')[0]
    userMessage = message.content
    channel = message.channel
    
    try:
        url = message.attachments[0].url
    except:
        url = None
    
    print(f"username: {username}, userMessage: {userMessage}, channel: {channel}, url: {url}")
    
    if message.author.name == client.user:
        return
    
    if message.channel.name in ["bot-chat", "ai-chat"]:
        match userMessage.lower():
            
            case "!ping":
                await channel.send("Pong!")
                
    if message.channel.name == "ai-chat":
        match userMessage.lower():
            
            case "!pizza":
                if url is None:
                    await channel.send("Please attach an image to your message")
                await channel.send(read.classify(model, url, tran, ["is a pizza", "is not a pizza"], device))

client.run(TOKEN)