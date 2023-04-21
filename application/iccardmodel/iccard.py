import glob
import os, zipfile, io, re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import torch
import torch.utils.data
import torch.nn as nn
import torch.nn.functional as F
import torchvision
import torchmetrics
import time
import pytorch_lightning as pl

from torchmetrics.functional import accuracy
from pytorch_lightning.loggers import CSVLogger
from pytorch_lightning.callbacks import ModelCheckpoint
from PIL import Image
from torchvision import transforms,datasets
from torchvision.models import resnet18
from torchvision.models import mnasnet1_0
from torchvision.models import mobilenet_v2
from natsort import natsorted

transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])
class Net(pl.LightningModule):
    def __init__(self):
        super().__init__()
        self.feature =resnet18(pretrained=True)
        # self.feature =resnet34(pretrained=True)
        # self.feature =resnet50(pretrained=True)
        # self.feature =resnet101(pretrained=True)
        # self.feature =resnet152(pretrained=True)

        # self.feature  = torch.hub.load('pytorch/vision:v0.10.0', 'wide_resnet101_2', pretrained=True)

        # self.feature = mnasnet1_0(pretrained=True)
        # self.feature = mobilenet_v2(pretrained=True)
        self.fc = nn.Linear(1000,5)
        self.bn = nn.BatchNorm2d(3)

    def forward(self, x):
        h= self.bn(x)
        h = self.feature(h)
        h = self.fc(h)
        return h
    
#iccardmodel/get_models.shを実行する
print("---get_models.sh---")
os.system('iccardmodel/get_models.sh')
#iccardmodel/iccard.ptが存在するか確認する
timecnt = 0 
print("------------------pwd ------------------")
os.system('pwd')
while True:
    timecnt += 1
    if os.path.exists('iccardmodel/iccard.pt'):
        break
    if(timecnt > 60):
        break
    time.sleep(1)
print("---load model---")
print("------------------pwd ------------------")
os.system('pwd')
parent_dir = "iccardmodel"
parent_dir = os.path.abspath(parent_dir)
net = Net().cpu().eval()
print("---load statedict---")
net.load_state_dict(torch.load(parent_dir+os.sep+'iccard.pt', map_location=torch.device('cpu')))
print("---load statedict end---")
print("-----torch version")
print(torch.__version__)
def predict(img):
    print("---predict---")
    img = Image.fromarray(img)
    # image = Image.open(img).convert("RGB")
    print("---transform---")
    data = transform(img)
    print("---make net---")
    # 画像から配列に変換
    data = net(data.unsqueeze(0))
    print("---softmax---")
    data = F.softmax(data, dim=1)
    print("--argmax---")
    data = torch.argmax(data,dim=1)
    data = data.to('cpu').detach().numpy().copy()
    print("--getlabel---")
    return getLabel(data)

def getLabel(val):
    print(val)
    if 0==val:
       return "ICOCA"
    if 1==val:
       return "KOBEシニア元気ポイント"
    if 2==val:
       return "奈良市ポイント"
    if 3==val:
       return "その他"
    if 4==val:
       return "PITAPA"

