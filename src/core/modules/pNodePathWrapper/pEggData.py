from pandac.PandaModules import *

from core.modules.pNodePathWrapper.pEggBase import *

class ObjectEggData(ObjectEggBase):
  className = 'EggData'
  def __init__(self, parent, modelWrapper, eggData):
    ObjectEggBase.__init__(self, parent, modelWrapper, 'EggData')
    self.eggData = eggData
    
    self.setFilepath(self.modelWrapper.modelFilepath)
    
    self.possibleFunctions = ['save', 'saveAs']
  
  def save(self):
    #filename = self.modelWrapper.modelFilepath
    self.saveAs(self.getFilepath())
  
  def saveAs(self, filepath):
    print "I: ObjectEggData.saveAs:", filepath
    self.eggData.writeEgg(Filename(filepath))
  
  def destroy(self):
    ObjectEggBase.destroy(self)
    self.eggData = None
    self.modelWrapper = None
