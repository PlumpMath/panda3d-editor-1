#!/usr/bin/env python

import pickle
import os, sys
import random
import traceback

from direct.task.Task import Task
from pandac.PandaModules import *
from direct.showbase.DirectObject import DirectObject
from direct.fsm.FSM import FSM

#from editorObjects import *
from core.pModelController import modelController
from core.pScenePicker import *
from core.pModelModificator import *
#from core.pCameraController import cameraController
from core.pModelIdManager import modelIdManager
from core.pConfigDefs import *
# this is a bugfixed / slightly changed version of DirectGrid
from core.pGrid import DirectGrid
from core.pMouseHandler import mouseHandler
from core.pSoundManager import soundManager
from core.pObjectEditor import objectEditor
from core.modules import *
from core.pTreeNode import *
from core.modules.pSceneNodeWrapper import *

DEBUG = False


class EditorClass(DirectObject, FSM):
  def __init__(self, parentNodePath):
    FSM.__init__(self,'EditorClass')
    
    self.accept( 'PlayMode', self.request, ['PlayMode'] )
    self.accept( 'WorldEditMode', self.request, ['WorldEditMode'] )
    self.accept( 'ObjectEditMode', self.request, ['ObjectEditMode'] )
    
    self.request('DisabledMode')
    
    #self.treeParent = TreeParentNode(parentNodePath)
    self.treeParent = SceneNodeWrapper.onCreateInstance(None, 'default.egg')
  
  def enterDisabledMode(self):
    pass
  def exitDisabledMode(self):
    self.treeParent.enableEditmode(True)
  
  def enterPlayMode(self):
    soundManager.enable()
    # disable edit mode on all nodes
    self.treeParent.disableEditmode()
  def exitPlayMode(self):
    self.treeParent.enableEditmode(True)
  
  def enterWorldEditMode(self):
    print "I: core.EditorClass.enterWorldEditMode:"
    soundManager.enable()
    
    self.sceneHelperModels = NodePath('editor-helper-models')
    self.sceneHelperModels.reparentTo(render)
    self.sceneHelperModels.setLightOff()
    
    # the axis model at 0/0/0
    axis = loader.loadModel( 'zup-axis.egg' )
    axis.reparentTo( self.sceneHelperModels )
    
    scenePicker.toggleEditmode(True)
    #print "I: core.EditorClass.enterWorldEditMode:", modelModificator.__class__.__name__
    modelModificator.toggleEditmode(True)
    
    # a grid model
    gridNp = DirectGrid(parent=self.sceneHelperModels)
    
    # refresh the scenegraphbrowser
    #messenger.send(EVENT_SCENEGRAPH_REFRESH)
    messenger.send(EVENT_SCENEGRAPH_CHANGE_ROOT, [self.treeParent])
    
    messenger.send(EVENT_MODELCONTROLLER_SELECT_OBJECT, [None])
    messenger.send(EVENT_SCENEGRAPH_REFRESH)
  
  def exitWorldEditMode(self):
    # save the selected model to the texturePainter
    objectEditor.setEditObject(modelController.getSelectedObject())
    # drop what we have selected
    modelController.selectObject(None)
    # disable the selecting of nodes
    scenePicker.toggleEditmode(False)
    modelModificator.toggleEditmode(False)
  
  def toggle(self, state=None):
    if state is None:
      # switch to next mode
      if self.state == 'DisabledMode':
        state = 'WorldEditMode'
      elif self.state == 'PlayMode':
        state = 'WorldEditMode'
      elif self.state == 'WorldEditMode':
        state = 'ObjectEditMode'
      elif self.state == 'ObjectEditMode':
        state = 'PlayMode'
      else:
        state = 'PlayMode'
        print "W: EditorClass.toggle: unknown previous mode", self.state, "setting to", state
    
    if state in ['DisabledMode', 'PlayMode', 'WorldEditMode', 'ObjectEditMode']:
      self.request(state)
    else:
      self.request('PlayMode')
      print "W: EditorClass.toggle: unknown requested mode", state, ", setting to", self.state
  
  def getData(self):
    modelData = ''
    for model in self.modelList:
      modelData += ", [%s, %s, %s, %s] \n" %  ( model.modelName
                                              , str(model.getPos(render))
                                              , str(model.getHpr(render))
                                              , str(model.getScale(render)) )
    return modelData
  
  def saveEggModelsFile(self, filepath):
    # walk the render tree and save the egg-links
    self.treeParent.save(filepath)
  
  def loadEggModelsFile(self, filepath):
    # read the eggData
    
    if filepath != None and filepath != '' and filepath != ' ':
      self.destroyScene()
      
      filetype = os.path.splitext(filepath)
      self.treeParent = SceneNodeWrapper.onCreateInstance(None, filepath)
      
      if self.getCurrentOrNextState() == 'WorldEditMode':
        self.treeParent.enableEditmode(True)
      
      # refresh the scenegraphbrowser
      messenger.send(EVENT_SCENEGRAPH_CHANGE_ROOT, [self.treeParent])
      
      if self.getCurrentOrNextState() == 'WorldEditMode':
        # select no model -> will select sceneRoot
        modelController.selectObject(None)
  
  def destroyModel(self):
    selectedObject = modelController.getSelectedObject()
    if selectedObject is not None:
      if selectedObject == self.treeParent:
        print "W: core.EditorClass: should not destroy root object"
        return
      modelController.selectObject(None)
      
      MEMLEAK_CHECK = False
      if MEMLEAK_CHECK:
        tmp = [selectedObject]
      
      # delete recursively
      for object in selectedObject.getRecChildren():
        if MEMLEAK_CHECK:
          tmp.append(object)
        object.destroy()
        del object
      
      selectedObject.destroy()
      del selectedObject
      
      # refresh the scenegraphbrowser
      messenger.send(EVENT_SCENEGRAPH_REFRESH)
      
      if MEMLEAK_CHECK:
        import gc
        gc.collect()
        gc.collect()
        for t in tmp:
          print "W: EditorClass.destroyModel: MEMLEAK_CHECK"
          print "  - type:          ", t.__class__.__name__
          print "  - instance:      ", t
          print "  - num references:", len(gc.get_referrers(t))
          for ref in gc.get_referrers(t):
            print "    -", ref
  
  def destroyScene(self):
    # delete the whole scene
    messenger.send(EVENT_SCENEGRAPH_CHANGE_ROOT, [None])
    messenger.send(EVENT_MODELCONTROLLER_SELECT_OBJECT, [None])
    print "destroyScene:childs", self.treeParent.getChildren()
    self.treeParent.destroy()
    del self.treeParent
    
    print "D: core.EditorApp.destroyScene: found obj in modelIdManager"
    for obj in modelIdManager.getAllObjects():
      if type(obj) != NodePath:
        print "  -", obj
        #if node.nodePath.hasTag(EDITABLE_OBJECT_TAG):
          #node.destroy()
          #del node
