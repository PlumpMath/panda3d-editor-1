from direct.showbase.DirectObject import DirectObject

from pDirectTree import *

class ModelBrowser(DirectObject):
  def __init__(self, parent, filename,
               frameSize=(1,1),
               pos=(0,0,0),
               button1func=None,
               button2func=None,
               button3func=None,):
    self.browser = DirectTree(parent=parent, pos=pos, frameSize=frameSize)
    self.filename = filename
    self.button1funcCall=button1func
    self.button2funcCall=button2func
    self.button3funcCall=button3func
    self.nodeDict = dict()
    self.update()
  
  def button1func(self, treeItem):
    self.button1funcCall(treeItem.eggData)
  def button2func(self, treeItem):
    self.button2funcCall(treeItem.eggData)
  def button3func(self, treeItem):
    self.button3funcCall(treeItem.eggData)
  
  def rec(self, eggParentData, treeParent = None):
    if type(eggParentData) == EggPolygon:
      return
    name = type(eggParentData).__name__
    treeItem = DirectTreeItem(treeParent, name)
    treeItem.button1Func = self.button1func
    treeItem.button2Func = self.button2func
    treeItem.button3Func = self.button3func
    treeItem.eggData = eggParentData
    if type(eggParentData) in [EggData, EggGroup]:
      for eggChildData in eggParentData.getChildren():
        self.rec(eggChildData, treeItem)
    elif type(eggParentData) == EggPolygon:
      pass
    elif type(eggParentData) == EggTexture:
      pass
    elif type(eggParentData) == EggVertexPool:
      pass
    elif type(eggParentData) == EggComment:
      pass
    elif type(eggParentData) == EggExternalReference:
      pass
    else:
      pass
    return treeItem
  
  def update(self):
    eggData = EggData()
    eggData.read(self.filename)
    
    # update the scenegraph
    self.oldNodeDict = self.nodeDict.copy()
    self.nodeDict = dict()
    treeParent = self.rec(eggData, None)
    # destroy the contents of the nodeDict
    for treeNode in self.oldNodeDict.keys()[:]:
      #print "destryoing node", treeNode
      treeItem = self.oldNodeDict[treeNode]
      del treeItem.eggData
      treeItem.destroy()
      del self.oldNodeDict[treeNode]
    self.browser.treeStructure = treeParent
    self.browser.render()
    self.browser.update()

if __name__ == '__main__' and True:
  from direct.directbase import DirectStart
  from pandac.PandaModules import *
  
  def button1press(eggData):
    print eggData
  
  s = ModelBrowser(parent=aspect2d, filename='examples/jumpgate.egg', button1func=button1press)
  s.update()
  
  run()
