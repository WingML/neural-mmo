from pdb import set_trace as T
import numpy as np

from itertools import chain 
from collections import defaultdict

from forge.blade.io.serial import Serial
from forge.blade.lib.log import BlobSummary

from forge.ethyr.experience import Rollout

class RolloutManager:
   '''Collects and batches rollouts for inference and training'''
   def __init__(self, config):
      self.inputs  = defaultdict(lambda: Rollout(config))
      self.outputs = defaultdict(lambda: Rollout(config))
      self.logs    = BlobSummary()

   @property
   def nUpdates(self):
      return self.logs.nUpdates

   @property
   def nRollouts(self):
      return self.logs.nRollouts

   def collectInputs(self, stims):
      '''Collects observation data to internal buffers'''
      #Finish rollout
      for key in stims.dones:
         assert key not in self.outputs

         #Already cleared as a partial traj
         if key not in self.inputs:
            continue

         rollout           = self.inputs[key]
         self.outputs[key] = rollout

         rollout.finish()
         del self.inputs[key]

         self.logs.blobs.append(rollout.blob)
         self.logs.nUpdates  += len(rollout)
         self.logs.nRollouts += 1

      #Update inputs 
      for key, reward in zip(stims.keys, stims.rewards):
         assert key not in self.outputs
         rollout = self.inputs[key]
         rollout.inputs(reward, key)

   def collectOutputs(self, atnArg, keys, atns, atnsIdx, values):
      '''Collects output data to internal buffers'''
      for key, atn, atnIdx, val in zip(keys, atns, atnsIdx, values):
         assert key in self.inputs
         assert not self.inputs[key].done
         self.inputs[key].outputs(atnArg, atn, atnIdx, val)

   def step(self):
      '''Returns log objects of all rollouts.

      Also resets the rollout counter.

      Returns:
         outputs, logs: rolloutdict, list of blob logging objects
      '''
      logs      = self.logs
      self.logs = BlobSummary()

      outputs      = self.outputs
      self.outputs = defaultdict(Rollout)

      return outputs, logs 
