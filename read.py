import random
import torch
from PIL import Image
import requests

def classify(model, imgPath, trans=None, classes=[], device=torch.device("cpu")):
    
    try:
        model = model.eval()
        img = Image.open(requests.get(imgPath, stream=True).raw)
        img = img.convert("RGB")
        img = trans(img)
        img = img.unsqueeze(0)
        img = img.to(device)


        output = model(img)
        _, pred = torch.max(output, 1)
        procent = torch.sigmoid(output)
        
        return f"It {classes[pred.item()]} i'm {procent[0][pred[0]]*100:.2f}% sure"
    except Exception:
        return "Something went wrong😕, please notify the developer with the following message: " + str(Exception)


def get_random_quote():
    with open("quotes.txt", "r") as file:
        quotes = file.readlines()
    return quotes[random.randint(0, len(quotes)-1)]