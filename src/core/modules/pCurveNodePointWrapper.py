from direct.showbase.DirectObject import DirectObject

from core.modules.pVirtualNodeWrapper import VirtualNodeWrapper
from core.pConfigDefs import *

class CurveNodePointWrapper(VirtualNodeWrapper, DirectObject):
  def __init__(self, parent, name='CurveElement'):
    print "I: CurveNodePointWrapper.__init__"
    curveNodeModel = 'data/models/misc/sphere.egg'
    VirtualNodeWrapper.__init__(self, parent, name, curveNodeModel)
  
  def startEdit(self):
    VirtualNodeWrapper.startEdit(self)
    # if the modificator is done, update the visuals of the curve
    self.accept(EVENT_MODELCONTROLLER_FULL_REFRESH, self.getParent().update)
    # refresh is to slow to update automatically
    #self.accept(EVENT_MODELCONTROLLER_FAST_REFRESH, self.getParent().update)
  
  def stopEdit(self):
    VirtualNodeWrapper.stopEdit(self)
    self.ignoreAll()
  
  def destroy(self):
    VirtualNodeWrapper.destroy(self)
