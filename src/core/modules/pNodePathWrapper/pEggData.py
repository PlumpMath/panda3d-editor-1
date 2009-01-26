from pandac.PandaModules import *

from core.modules.pNodePathWrapper.pEggBase import *

class ObjectEggData(ObjectEggBase):
  className = 'EggData'
  def __init__(self, parent, modelWrapper, eggData):
    ObjectEggBase.__init__(self, parent, modelWrapper, 'EggData')
    self.eggData = eggData
    
    self.possibleFunctions = ['save']
  
  def save(self, filepath):
    print "I: ObjectEggData.save"
    #if self.editModule:
    #  print "  - saving"
    self.eggData.writeEgg(Filename(filepath))
    #  self.editModule.destroy()
    #  self.editModule = None
  
  #def update(self):
  #  return self.eggData
  
  def destroy(self):
    ObjectEggBase.destroy(self)
    self.eggData = None
    self.modelWrapper = None
