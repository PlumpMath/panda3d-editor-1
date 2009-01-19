__all__ = ['ObjectEggGroup', 'EggGroup_CollideFlags',
           'EggGroup_CollisionSolidType', 'EggGroup_DCSType',
           'EggGroup_BillboardType']

from pandac.PandaModules import *

from core.pConfigDefs import *
from core.modules.pNodePathWrapper.pEggBase import *

EggGroup_CollideFlags = Enum(
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

EggGroup_CollisionSolidType = Enum(
  CSTNone = EggGroup.CSTNone,
  CSTPlane = EggGroup.CSTPlane,
  CSTPolygon = EggGroup.CSTPolygon,
  CSTPolyset = EggGroup.CSTPolyset,
  CSTSphere = EggGroup.CSTSphere,
  CSTTube = EggGroup.CSTTube,
  CSTInvSphere = EggGroup.CSTInvSphere,
  CSTFloorMesh = EggGroup.CSTFloorMesh,
)

EggGroup_DCSType = Enum(
  DCUnspecified = EggGroup.DCUnspecified,
  DCNone = EggGroup.DCNone,
  DCLocal = EggGroup.DCLocal,
  DCNet = EggGroup.DCNet,
  DCDefault = EggGroup.DCDefault,
)

EggGroup_BillboardType = Enum(
  BTNone = EggGroup.BTNone,
  BTAxis = EggGroup.BTAxis,
  BTPointCameraRelative = EggGroup.BTPointCameraRelative,
  BTPointWorldRelative = EggGroup.BTPointWorldRelative,
)

class ObjectEggGroup(ObjectEggBase):
  def __init__(self, parent, modelWrapper, eggGroup):
    ObjectEggBase.__init__(self, parent, modelWrapper, 'EggGroup')
    # we need to work on the external eggGroup
    self.eggGroup = eggGroup
    # store the types of mutable parameters
    self.mutableParameters['collision_solid_type'] = [ EggGroup_CollisionSolidType,
      self.eggGroup.getCsType,
      self.eggGroup.setCsType,
      None,
      None ]
    self.mutableParameters['collide_flags'] = [ EggGroup_CollideFlags,
      self.eggGroup.getCollideFlags,
      self.eggGroup.setCollideFlags,
      None,
      None ]
    self.mutableParameters['dcs_type'] = [ EggGroup_DCSType,
      self.eggGroup.getDcsType,
      self.eggGroup.setDcsType,
      self.eggGroup.hasDcsType,
      None ]
    self.mutableParameters['billaboard_type'] = [ EggGroup_BillboardType,
      self.eggGroup.getBillboardType,
      self.eggGroup.setBillboardType,
      None,
      None ]
  
  def destroy(self):
    ObjectEggBase.destroy(self)
    self.eggGroup = None
    self.modelWrapper = None
  
  def getParameters(self):
    parameters = dict()
    for name, [valueType, getFunc, setFunc, hasFunc, clearFunc] in self.mutableParameters.items():
      parameters[name] = getFunc()
    print "I: ObjectEggGroup.getData:", parameters
    return parameters
  
  def setParameters(self, parameters):
    print "I: ObjectEggGroup.setData:", parameters
    for name, value in parameters.items():
      if name in self.mutableParameters:
        [valueType, getFunc, setFunc, hasFunc, clearFunc] = self.mutableParameters[name]
        setFunc(parameters[name])
