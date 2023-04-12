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
        self.fc = nn.Linear(1000,3)
        self.bn = nn.BatchNorm2d(3)

    def forward(self, x):
        h= self.bn(x)
        h = self.feature(h)
        h = self.fc(h)
        return h
    
#iccardmodel/get_models.shを実行する
os.system('iccardmodel/get_models.sh')
#iccardmodel/iccard.ptが存在するか確認する
while True:
    if os.path.exists('iccardmodel/iccard.pt'):
        break
    time.sleep(1)

parent_dir = "iccardmodel"+os.sep
parent_dir = os.path.abspath(parent_dir)
net = Net().cpu().eval()
net.load_state_dict(torch.load(parent_dir+os.sep+'iccard.pt', map_location=torch.device('cpu')))

def predict(img):
    img = Image.fromarray(img)
    # image = Image.open(img).convert("RGB")
    data = transform(img)
    # 画像から配列に変換
    data = net(data.unsqueeze(0))
    data = F.softmax(data, dim=1)
    data = torch.argmax(data,dim=1)
    data = data.to('cpu').detach().numpy().copy()
    return get_label(data)

def get_label(lbl):
    return str(lbl)
