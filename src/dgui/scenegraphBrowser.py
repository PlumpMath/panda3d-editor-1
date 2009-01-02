from pDirectTree import *
from direct.showbase.DirectObject import DirectObject

class SceneGraphBrowser(DirectObject):
  def __init__(self, parent, treeRoot, includeTag,
               frameSize=(1,1),
               pos=(0,0,0),
               button1func=None,
               button2func=None,
               button3func=None,):
    self.browser = DirectTree(parent=parent, pos=pos, frameSize=frameSize)
    self.treeRoot = treeRoot
    self.includeTag = includeTag
    self.button1funcCall=button1func
    self.button2funcCall=button2func
    self.button3funcCall=button3func
    self.nodeDict = dict()
    self.update()
  
  def button1func(self, treeItem):
    self.button1funcCall(treeItem.sceneNp)
  def button2func(self, treeItem):
    self.button2funcCall(treeItem.sceneNp)
  def button3func(self, treeItem):
    self.button3funcCall(treeItem.sceneNp)
  
  def rec(self, nodePath=None, treeParent=None):
    """Used internally to recursively add the children of a nodepath to the scene graph browser."""
    name = nodePath.getName()
    if nodePath.hasTag(self.includeTag) or nodePath == self.treeRoot:
      if not nodePath in self.oldNodeDict:
        treeItem = TreeItem(treeParent, name)
        treeItem.sceneNp = nodePath
        treeItem.button1Func=self.button1func
        treeItem.button2Func=self.button1func
        treeItem.button3Func=self.button1func
      else:
        treeItem = self.oldNodeDict[nodePath]
        treeItem.setParent(treeParent)
        treeItem.clearChildrens()
        del self.oldNodeDict[nodePath] # remove it from the old dict
      self.nodeDict[nodePath] = treeItem
      
      for c in xrange(nodePath.getNumChildren()):
        childNodePath = nodePath.getChild(c)
        self.rec(childNodePath, treeItem)
      return treeItem
  
  def update(self):
    # update the scenegraph
    self.oldNodeDict = self.nodeDict.copy()
    self.nodeDict = dict()
    treeParent = self.rec(self.treeRoot, None)
    # destroy the contents of the nodeDict
    for treeNode in self.oldNodeDict.keys()[:]:
      #print "destryoing node", treeNode
      treeItem = self.oldNodeDict[treeNode]
      del treeItem.np
      treeItem.destroy()
      del self.oldNodeDict[treeNode]
    self.browser.treeStructure = treeParent
    self.browser.render()
    self.browser.update()

if __name__ == '__main__' and True:
  from direct.directbase import DirectStart
  from pandac.PandaModules import *
  def createNestedSmileys(parent,depth,branch,color):
    parent.setColor(color,1000-depth)
    for d in range(depth):
      scale=.55
      kidSmileys=lilsmileyGeom.instanceUnderNode(parent,'kid_Smileys_'+str(id(parent)))
      kidSmileys.setX(d+1)
      kidSmileys.setScale(scale)
      kidSmileys.setR(60*((d%2)*2-1))
      color=color*.8
      color.setW(1)
      for b in range(branch):
        z=b-(branch-1)*.5
        kidSmiley=lilsmileyGeom.instanceUnderNode(kidSmileys,'smileyBranch_%i-%i' %(id(kidSmileys),b))
        kidSmiley.setPos(1,0,z*scale)
        kidSmiley.setScale(scale)
        kidSmiley.setR(-z*30)
        createNestedSmileys(kidSmiley,depth-1,branch,color)
  
  # some 3d nodes
  teapot=loader.loadModel('teapot')
  teapot.reparentTo(render)
  panda=loader.loadModel('zup-axis')
  panda.reparentTo(render)
  panda.setScale(.22)
  panda.setPos(4.5,-5,0)
  
  # some 2d nodes
  lilsmiley1=loader.loadModelCopy('misc/lilsmiley')
  lilsmiley1.reparentTo(aspect2d)
  lilsmileyGeom=lilsmiley1.find('**/poly')
  createNestedSmileys(lilsmiley1,3,2,Vec4(0,1,0,1))
  lilsmiley1.setX(render2d,-.7)
  lilsmiley1.setScale(.5)
  
  camera.setPos(11.06, -16.65, 8.73)
  camera.setHpr(42.23, -25.43, -0.05)
  camera.setTag('noSelect','')
  base.setBackgroundColor(.2,.2,.2,1)
  base.disableMouse()
  
  s = SceneGraphBrowser()
  
  import time, random, gc
  lastTime = time.time()
  modelList = list()
  for i in xrange(3):
    modelList.append(panda.copyTo( render ))
  while True:
    taskMgr.step()
    if time.time() - lastTime > 0.5:
      lastTime = time.time()
      numDel = random.randint(0, len(modelList)-1)
      #print "deleting", numDel
      for i in range(numDel, 0, -1):
        modelList[i].detachNode()
        modelList[i].removeNode()
        del modelList[i]
      numCreate = random.randint(0, 5)
      #print "creating", numCreate
      for i in xrange(numCreate):
        modelList.append(panda.copyTo( render ))
      s.update()
      gc.collect()
      gc.collect()
      print len(gc.get_objects())