from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import *
from core.pModelIdManager import modelIdManager

# the classname must match the filename (with a capital starting letter!)
class TestObjectExtension(DirectObject):
  def __init__(self, object):
    # you should store the object :-)
    self.object = object
    taskMgr.add(self.updateTask, 'updateTask-%s' % self.object.id)
    print "I: TestObjectExtension.__init__"
    print "  - searching for object", modelIdManager.getObject(self.object.id)
    print "  - number of objects in scene", len(modelIdManager.getAllModels())
    allModels = modelIdManager.getAllModels()
    for model in allModels:
      try:
        if model.getName() == 'teapot.egg.pz':
          print "  - found teapot", model
      except:
        print "ERRRRRORRRR: this is a bug in the code, delete seems not have run on all objects"
    
    self.accept('arrow_up', self.up)
    print "  - done"
  
  def destroy(self):
    taskMgr.remove('updateTask-%s' % self.object.id)
  
  def __del__(self):
    self.destroy()
  
  def updateTask(self, task):
    #print "I: TestObjectExtension.update", self
    if not task.isRemoved():
      try:
        self.object.setR( task.time * 20 )
        return task.cont
      except:
        print "ERRRRRORRRR: this is a bug in the code, delete seems not have run on all objects"
  
  def up(self):
    self.object.setX(self.object, 0.5)
  
