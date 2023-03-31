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
# #全体
transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

class Net(pl.LightningModule):
    def __init__(self):
        super().__init__()
        # self.feature =resnet18(pretrained=True)
        self.feature  = torch.hub.load('pytorch/vision:v0.10.0', 'wide_resnet101_2', pretrained=True)

        # self.feature = mnasnet1_0(pretrained=True)
        # self.feature = mobilenet_v2(pretrained=True)
        self.fc = nn.Linear(1000,2)
        self.bn = nn.BatchNorm2d(20),

    def forward(self, x):
        # h= self.bn(x)
        h = self.feature(x)
        h = self.fc(h)
        return h


    def training_step(self, batch, batch_idx):
        x, t = batch
        y = self(x)
        loss = F.cross_entropy(y, t)
        self.log('train_loss', loss, on_step=True, on_epoch=True, prog_bar=True)
        self.log('train_acc', accuracy(y.softmax(dim=-1), t), on_step=True, on_epoch=True, prog_bar=True)
        return loss


    def validation_step(self, batch, batch_idx):
        x, t = batch
        y = self(x)
        loss = F.cross_entropy(y, t)
        self.log('val_loss', loss, on_step=False, on_epoch=True)
        self.log('val_acc', accuracy(y.softmax(dim=-1), t), on_step=False, on_epoch=True)
        return loss


    def test_step(self, batch, batch_idx):
        x, t = batch
        y = self(x)
        loss = F.cross_entropy(y, t)
        self.log('test_loss', loss, on_step=False, on_epoch=True)
        self.log('test_acc', accuracy(y.softmax(dim=-1), t), on_step=False, on_epoch=True)
        return loss


    def configure_optimizers(self):
        optimizer = torch.optim.SGD(self.parameters(), lr=0.01)
        return optimizer




def predict(img):
    parent_dir = "yoloface"+os.sep+"model-weights"+os.sep
    parent_dir = os.path.abspath(parent_dir)
    print("sexweight:"+parent_dir)
    net = Net().cpu().eval()
    net.load_state_dict(torch.load(parent_dir+os.sep+'sex.pt', map_location=torch.device('cpu')))
    img = Image.fromarray(img)
    # image = Image.open(img).convert("RGB")
    image = transform(img)
    # 画像から配列に変換
    data = np.asarray(image)
    data = torch.tensor(data)
    data = net(data.unsqueeze(0))
    data = F.softmax(data, dim=1)
    data = torch.argmax(data,dim=1)
    data = data.to('cpu').detach().numpy().copy()
    return get_label(data)

def get_label(lbl):
    print("----------lbl")
    print(lbl[0])
    if lbl[0] == 0:
        return 'male'
    if lbl[0] == 1:
        return 'female'
    return 'other'