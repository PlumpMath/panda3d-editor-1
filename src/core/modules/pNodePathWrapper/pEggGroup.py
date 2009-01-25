__all__ = ['ObjectEggGroup', 'EggGroup_CollideFlags_Bitmask',
           'EggGroup_CollisionSolidType_Enum', 'EggGroup_DCSType_Enum',
           'EggGroup_BillboardType_Enum']

from pandac.PandaModules import *

from core.modules.pNodePathWrapper.pEggBase import *
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
      None ]
    self.mutableParameters['collide_flags'] = [ EggGroup_CollideFlags_Bitmask,
      self.eggGroup.getCollideFlags,
      self.eggGroup.setCollideFlags,
      None,
      None ]
    self.mutableParameters['dcs_type'] = [ EggGroup_DCSType_Enum,
      self.eggGroup.getDcsType,
      self.eggGroup.setDcsType,
      self.eggGroup.hasDcsType,
      None ]
    self.mutableParameters['billaboard_type'] = [ EggGroup_BillboardType_Enum,
      self.eggGroup.getBillboardType,
      self.eggGroup.setBillboardType,
      None,
      None ]
  
  def destroy(self):
    ObjectEggBase.destroy(self)
    self.eggGroup = None
    self.modelWrapper = None
