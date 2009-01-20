from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import *
from core.pModelIdManager import modelIdManager

DEBUG = False

# the classname must match the filename (with a capital starting letter!)
class TestObjectExtension(DirectObject):
  def __init__(self, object):
    # you should store the object :-)
    self.object = object
    taskMgr.add(self.updateTask, 'updateTask-%s' % self.object.id)
    if DEBUG:
      print "I: TestObjectExtension.__init__"
      print "  - searching for object", modelIdManager.getObject(self.object.id)
      print "  - number of objects in scene", len(modelIdManager.getAllObjects())
    allNodes = modelIdManager.getAllObjects()
    for node in allNodes:
      try:
        if node.nodePath.getName() == 'teapot.egg.pz':
          if DEBUG:
            print "  - found teapot", node
      except:
        if DEBUG:
          print "E: TestObjectExtension.__init__: this is a bug in the code, delete seems not have run on all objects"
    
    self.accept('arrow_up', self.up)
    if DEBUG:
      print "  - done"
  
  def destroy(self):
    taskMgr.remove('updateTask-%s' % self.object.id)
  
  def __del__(self):
    self.destroy()
  
  def updateTask(self, task):
    #print "I: TestObjectExtension.update", self
    if not (hasattr(task, "isRemoved") and task.isRemoved()):
      try:
        self.object.setR( task.time * 20 )
        return task.cont
      except:
        if DEBUG:
          print "E: this is a bug in the code, delete seems not have run on all objects"
  
  def up(self):
    self.object.setX(self.object, 0.5)
  
