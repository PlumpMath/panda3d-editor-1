import pickle

from pandac.PandaModules import *
from direct.gui.DirectGui import *

from core.pModelIdManager import modelIdManager
from core.pConfigDefs import *

DEBUG = False

BASEWRAPPER_DATA_TAG = 'BaseWrapper-params'

class BaseWrapper(NodePath):
  def onCreateInstance(self, parent, name='BaseWrapper'):
    # create instance of this class
    objectInstance = self(parent, name)
    return objectInstance
  onCreateInstance = classmethod(onCreateInstance)
  
  def loadFromEggGroup(self, eggGroup, parent, filepath):
    if DEBUG:
      print "I: NodePathWrapper.loadFromEggGroup:"
    objectInstance = self(parent)
    return objectInstance
  loadFromEggGroup = classmethod(loadFromEggGroup)
  
  def __init__(self, parent, name):
    if DEBUG:
      print "I: BaseWrapper.__init__:", parent, name
    
    # get a uniq id for this object
    self.id = modelIdManager.getId()
    # define a name for this object
    name = '%s-%s' % (name, self.id)
    NodePath.__init__(self, name)
    # store this object
    modelIdManager.setObject(self, self.id)
    # reparent this nodePath
    if parent is None:
      parent = render
    self.reparentTo(parent)
    self.editModeEnabled = False
  
  def destroy(self):
    self.detachNode()
    self.removeNode()
  
  def getSaveData(self, relativeTo):
    # the given name of this object
    name = self.getName()
    # convert the matrix, very ugly right now
    om = self.getMat()
    nm = Mat4D()
    for x in xrange(4):
      for y in xrange(4):
        nm.setCell( x, y, om.getCell(x,y) )
    # the matrix we define must be applied to the nodes in "local space"
    instance = EggGroup(name)
    instance.setGroupType(EggGroup.GTInstance)
    instance.setTransform3d( nm )
    # define the type of this object
    className = self.__class__.__name__
    instance.setTag(MODEL_WRAPPER_TYPE_TAG, className)
    
    # get all data to store in the eggfile
    parameters = dict()
    if self.hasColor():
      parameters['color'] = [self.getColor()[0], self.getColor()[1], self.getColor()[2], self.getColor()[3]]
    if self.hasColorScale():
      parameters['colorScale'] = [self.getColorScale()[0], self.getColorScale()[1], self.getColorScale()[2],  self.getColorScale()[3]]
    if self.hasTransparency():
      parameters['transparency'] = self.getTransparency()
    if len(parameters) > 0:
      # add the data to the egg-file
      comment = EggComment(BASEWRAPPER_DATA_TAG, str(parameters))
      instance.addChild(comment)
    return instance
  
  def loadFromData(self, eggGroup, filepath):
    #print "I: BaseWrapper.setFromData:", eggGroup
    data = dict()
    for child in eggGroup.getChildren():
      if type(child) == EggComment:
        if child.getName() == BASEWRAPPER_DATA_TAG:
          exec("data = %s" % child.getComment())
    if data.has_key('color'):
      self.setColor(VBase4(*data['color']))
    if data.has_key('transparency'):
      self.setTransparency(data['transparency'])
    if data.has_key('colorScale'):
      self.setColorScale(VBase4(*data['colorScale']))
    self.setName(eggGroup.getName())
  
  def enableEditmode(self):
    ''' enables the edit methods of this object
    makes it pickable etc.
    edit mode is enabled'''
    if not self.editModeEnabled:
      # make this a editable object
      self.setTag(ENABLE_SCENEGRAPHBROWSER_MODEL_TAG, '')
      self.setTag(EDITABLE_OBJECT_TAG, self.id)
      self.editModeEnabled = True
  def disableEditmode(self):
    ''' disables the edit methods of this object
    -> performance increase
    edit mode is disabled'''
    if self.editModeEnabled:
      self.clearTag(ENABLE_SCENEGRAPHBROWSER_MODEL_TAG)
      self.clearTag(EDITABLE_OBJECT_TAG)
      self.editModeEnabled = False
  
  def startEdit(self):
    # the object is selected to be edited
    # creates a directFrame to edit this object
    if not self.editModeEnabled:
      print "E: code.BaseWrapper.startEdit: object is not in editmode", self
  def stopEdit(self):
    # the object is deselected from being edited
    if not self.editModeEnabled:
      print "E: code.BaseWrapper.stopEdit: object is not in editmode", self
