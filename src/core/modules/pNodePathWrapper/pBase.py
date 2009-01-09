__all__ = ['NodePathWrapperBase']

from pandac.PandaModules import *

from core.pConfigDefs import *
from core.modules.pNodePathWrapper.pEggData import *
from core.modules.pNodePathWrapper.pEggGroup import *
from core.modules.pNodePathWrapper.pEggTexture import *
from core.modules.pNodePathWrapper.pEggVertexPool import *
from core.modules.pNodePathWrapper.pEggPolygon import *

DEBUG = False

class NodePathWrapperBase:
  def __init__(self, editObject):
    self.editObject = editObject
    self.editModule = None
  
  def startEdit(self, objectPart):
    objectNode = self.editObject
    if type(objectPart) == EggData:
      print "I: ObjectEditor.startEdit: EggData"
      editModule = ObjectData(objectPart, objectNode)
    elif type(objectPart) == EggGroup:
      print "I: ObjectEditor.startEdit: EggGroup"
      editModule = ObjectEggGroup(objectPart, objectNode)
    elif type(objectPart) == EggTexture:
      print "I: ObjectEditor.startEdit: EggTexture"
      editModule = ObjectEggTexture(objectPart, objectNode)
    elif type(objectPart) == EggVertexPool:
      print "I: ObjectEditor.startEdit: EggTexture"
      editModule = ObjectEggVertexPool(objectPart, objectNode)
    elif type(objectPart) == EggPolygon:
      print "I: ObjectEditor.startEdit: EggTexture"
      editModule = ObjectEggPolygon(objectPart, objectNode)
    else:
      print "I: ObjectEditor.startEdit: unhandled type", type(objectPart)
    
    self.stopEdit()
    self.editModule = editModule
  
  def stopEdit(self):
    print "I: NodePathWrapperBase.stopEdit"
    if self.editModule:
      print "  - saving"
      self.getEditable()[0].writeEgg('test.egg')
      self.editModule.destroy()
      #self.editModule.stopEdit()
      self.editModule = None
    #if self.editModule:
    #  self.editModule.stopEdit()
  
  def getEditable(self):
    def recurse(eggParentData, depth=0):
      #print dir(eggParentData)
      l = list()
      if DEBUG:
        print "add", eggParentData
      l.append( eggParentData )
      if type(eggParentData) == EggData:
        if DEBUG:
          print " "*depth + "- " + "EggData"
        for eggChildData in eggParentData.getChildren():
          c = recurse(eggChildData, depth+1)
          l.extend(c)
      elif type(eggParentData) == EggGroup:
        if DEBUG:
          print " "*depth + "- " + "EggGroup"
        for eggChildData in eggParentData.getChildren():
          c = recurse(eggChildData, depth+1)
          l.extend(c)
      elif type(eggParentData) == EggPolygon:
        if DEBUG:
          print "*",
      elif type(eggParentData) == EggTexture:
        if DEBUG:
          print " "*depth + "- " + "EggTexture"
      elif type(eggParentData) == EggVertexPool:
        if DEBUG:
          print " "*depth + "- " + "EggVertexPool"
      elif type(eggParentData) == EggComment:
        if DEBUG:
          print " "*depth + "- " + "EggComment"
      elif type(eggParentData) == EggExternalReference:
        if DEBUG:
          print " "*depth + "- " + "EggExternalReference"
      elif type(eggParentData) == EggMaterial:
        if DEBUG:
          print " "*depth + "- " + "EggMaterial"
      else:
        if DEBUG:
          print " "*depth + "- " + "unparsed" + str(type(eggParentData))
        else:
          print "core.pNodePathWrapper.bBase.getEditable: unknown type:", str(type(eggParentData))
      return l
    
    eggData = EggData()
    eggData.read(self.editObject.modelFilepath)
    return recurse(eggData)
  

if __name__ == '__main__':
  filename = 'examples/models/smiley.egg.pz'
  #filename = 'examples/mytestscene.egg'
  eggData = EggData()
  print " --- reading "+filename+" ---"
  eggData.read(filename)
  getEggStructure(eggData)