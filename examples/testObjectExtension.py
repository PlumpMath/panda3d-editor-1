from core.modules.pCodeNodeWrapper import CodeNodeWrapper
from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import *

# the classname can be chosen, it must be inherited from CodeNodeWrapper
class TestObjectExtension(CodeNodeWrapper, DirectObject):
  def __init__(self, name, parent):
    # this MUST be called, else this instance will be deleted immediately
    # after the init has finished
    CodeNodeWrapper.__init__(self, name, parent)
    # now you can do whatever you want
    taskMgr.add(self.updateTask, 'updateTask-%s' % self.id)
    print "I: TestObjectExtension.__init__:"
    print "  - self", self
    print "  - name", name
    print "  - parent", parent
    
    self.accept('arrow_up', self.up)
  
  def updateTask(self, task):
    #print "I: TestObjectExtension.update", self
    #base.cam.lens.isInView()
    self.setH( task.time * 5 )
    return task.cont
  
  def up(self):
    self.setX(self, 0.5)
  
  def destroy(self):
    taskMgr.remove('updateTask-%s' % self.id)
    CodeNodeWrapper.destroy(self)
  
  # DO NOT DEFINE THE FOLLOWING CLASS FUNCTIONS:
  # enableEditmode, disableEditmode
  # startEdit, stopEdit
  # getSaveData
  # destroy, loadFromEggGroup
  
  # DO NOT DEFINE THE FOLLOWING CLASS VARIABLES:
  # id, mutableParameters, mutableParametersSorting, buttonsWindow, model
  # modelCollisionNodePath

# only the name of the file will be imported
#testObjectExtension=TestObjectExtension()
