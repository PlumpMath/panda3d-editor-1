# ------------------------------------------------------------------------------
# Copyright (c) 2009, Reto Spoerri
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
# * Neither the name of the <ORGANIZATION> nor the names of its contributors
#   may be used to endorse or promote products derived from this software
#   without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF
# THE POSSIBILITY OF SUCH DAMAGE.
# ------------------------------------------------------------------------------

__all__ = ['ObjectEggGroup', 'EggGroup_CollideFlags_Bitmask',
           'EggGroup_CollisionSolidType_Enum', 'EggGroup_DCSType_Enum',
           'EggGroup_BillboardType_Enum']

from pandac.PandaModules import *

from core.modules.pNodePathWrapper.pObjectEggBase import *
from core.pConfigDefs import *

EggGroup_CollideFlags_Bitmask = Bitmask(
  CFNone = EggGroup.CFNone,
  CFDescend = EggGroup.CFDescend,
  CFEvent = EggGroup.CFEvent,
  CFKeep = EggGroup.CFKeep,
  CFSolid = EggGroup.CFSolid,
  CFCenter = EggGroup.CFCenter,
  CFTurnstile = EggGroup.CFTurnstile,
  CFLevel = EggGroup.CFLevel,
  CFIntangible = EggGroup.CFIntangible,
)

EggGroup_CollisionSolidType_Enum = Enum(
  CSTNone = EggGroup.CSTNone,
  CSTPlane = EggGroup.CSTPlane,
  CSTPolygon = EggGroup.CSTPolygon,
  CSTPolyset = EggGroup.CSTPolyset,
  CSTSphere = EggGroup.CSTSphere,
  CSTTube = EggGroup.CSTTube,
  CSTInvSphere = EggGroup.CSTInvSphere,
  CSTFloorMesh = EggGroup.CSTFloorMesh,
)

EggGroup_DCSType_Enum = Enum(
  DCUnspecified = EggGroup.DCUnspecified,
  DCNone = EggGroup.DCNone,
  DCLocal = EggGroup.DCLocal,
  DCNet = EggGroup.DCNet,
  DCDefault = EggGroup.DCDefault,
)

EggGroup_BillboardType_Enum = Enum(
  BTNone = EggGroup.BTNone,
  BTAxis = EggGroup.BTAxis,
  BTPointCameraRelative = EggGroup.BTPointCameraRelative,
  BTPointWorldRelative = EggGroup.BTPointWorldRelative,
)

class ObjectEggGroup(ObjectEggBase):
  className = 'EggGroup'
  def __init__(self, parent, modelWrapper, eggGroup):
    ObjectEggBase.__init__(self, parent, modelWrapper, 'EggGroup')
    # we need to work on the external eggGroup
    self.eggGroup = eggGroup
    # store the types of mutable parameters
    self.mutableParameters['collision_solid_type'] = [ EggGroup_CollisionSolidType_Enum,
        self.eggGroup.getCsType,
        self.eggGroup.setCsType,
        None,
        None,
        False ]
    self.mutableParameters['collide_flags'] = [ EggGroup_CollideFlags_Bitmask,
        self.eggGroup.getCollideFlags,
        self.eggGroup.setCollideFlags,
        None,
        None,
        False ]
    self.mutableParameters['dcs_type'] = [ EggGroup_DCSType_Enum,
        self.eggGroup.getDcsType,
        self.eggGroup.setDcsType,
        self.eggGroup.hasDcsType,
        None,
        False ]
    self.mutableParameters['billaboard_type'] = [ EggGroup_BillboardType_Enum,
        self.eggGroup.getBillboardType,
        self.eggGroup.setBillboardType,
        None,
        None,
        False ]
  
  def destroy(self):
    ObjectEggBase.destroy(self)
    self.eggGroup = None
    self.modelWrapper = None
