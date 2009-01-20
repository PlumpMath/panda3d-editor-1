from pandac.PandaModules import *

from core.modules.pNodePathWrapper.pEggBase import *

class ObjectEggData(ObjectEggBase):
  def __init__(self, parent, modelWrapper, eggData):
    ObjectEggBase.__init__(self, parent, modelWrapper, 'EggData')
    self.eggData = eggData
  
  def save(self, filepath):
    print "I: ObjectEggData.save"
    #if self.editModule:
    #  print "  - saving"
    self.eggData.writeEgg(filepath)
    #  self.editModule.destroy()
    #  self.editModule = None
  
  def destroy(self):
    ObjectEggBase.destroy(self)
    self.eggData = None
    self.modelWrapper = None
