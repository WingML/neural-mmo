from pdb import set_trace as T
import numpy as np

import torch
from torch import nn
from torch.nn import functional as F

from forge.blade.io import stimulus

class Embedding(nn.Module):
   def __init__(self, var, dim):
      '''Pytorch embedding wrapper that subtracts the min'''
      super().__init__()
      self.embed = torch.nn.Embedding(var.range, dim)
      self.min = var.min

   def forward(self, x):
      return self.embed(x - self.min)

class Input(nn.Module):
   def __init__(self, cls, config):
      '''Embedding wrapper around discrete and continuous vals'''
      super().__init__()
      self.cls = cls
      if isinstance(cls, stimulus.node.Discrete):
         self.embed = Embedding(cls, config.EMBED)
      elif isinstance(cls, stimulus.node.Continuous):
         self.embed = torch.nn.Linear(1, config.EMBED)

   def forward(self, x):
      if isinstance(self.cls, stimulus.node.Discrete):
         x = x.long()
      elif isinstance(self.cls, stimulus.node.Continuous):
         x = x.float().unsqueeze(-1)
      x = self.embed(x)
      return x

class BiasedInput(nn.Module):
   def __init__(self, cls, config):
      '''Adds a bias to nn.Embedding
      This is useful for attentional models
      to learn a sort of positional embedding'''
      super().__init__()
      self.bias  = torch.nn.Embedding(1, config.HIDDEN)
      self.embed = Input(cls, config)

   def forward(self, x):
      return self.embed(x) + self.bias.weight
