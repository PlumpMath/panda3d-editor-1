from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import *
from core.pModelIdManager import modelIdManager

# the classname must match the filename (with a capital starting letter!)
class TestObjectExtension(DirectObject):
  def __init__(self, object):
    # this MUST be called, else this instance will be deleted immediately
    # after the init has finished
    #CodeNodeWrapper.__init__(self, name, parent)
    # now you can do whatever you want
    self.object = object
    taskMgr.add(self.updateTask, 'updateTask-%s' % self.object.id)
    print "I: TestObjectExtension.__init__"
    print "  - searching for object", modelIdManager.getObject(self.object.id)
    print "  - number of objects in scene", len(modelIdManager.getAllModels())
    
    self.accept('arrow_up', self.up)
    print "  - done"
  
  def __del__(self):
    #print "I: TestObjectExtension.__del__"
    self.destroy()
  
  def updateTask(self, task):
    #print "I: TestObjectExtension.update", self
    #base.cam.lens.isInView()
    self.object.setH( task.time * 5 )
    return task.cont
  
  def up(self):
    self.object.setX(self.object, 0.5)
  
  def destroy(self):
    print "I: TestObjectExtension.destroy"
    taskMgr.remove('updateTask-%s' % self.object.id)
