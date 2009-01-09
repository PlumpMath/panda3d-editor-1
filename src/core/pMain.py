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
#from core.pCameraController import cameraController
from core.pModelIdManager import modelIdManager
from core.pConfigDefs import *
# this is a bugfixed / slightly changed version of DirectGrid
from core.pGrid import DirectGrid
from core.pMouseHandler import mouseHandler
from core.pSoundManager import soundManager
from core.pObjectEditor import objectEditor
from core.modules import *

DEBUG = False

class EditorClass(DirectObject, FSM):
  def __init__(self, parentNodePath):
    FSM.__init__(self,'EditorClass')
    self.parentNodePath = render
    
    self.accept( 'PlayMode', self.request, ['PlayMode'] )
    self.accept( 'WorldEditMode', self.request, ['WorldEditMode'] )
    self.accept( 'ObjectEditMode', self.request, ['ObjectEditMode'] )
    
    self.request('DisabledMode')
  
  def enterDisabledMode(self):
    pass
  def exitDisabledMode(self):
    for model in modelIdManager.getAllModels():
      try:    model.enableEditmode()
      except: pass # some objects are not wrappers (like arrows to move etc.)
  
  def enterPlayMode(self):
    soundManager.enable()
    # disable edit mode on all nodes
    for model in modelIdManager.getAllModels():
      if model.hasTag(EDITABLE_OBJECT_TAG):
        model.disableEditmode()
  def exitPlayMode(self):
    for model in modelIdManager.getAllModels():
      try:    model.enableEditmode()
      except: pass # some objects are not wrappers (like arrows to move etc.)
  
  def enterWorldEditMode(self):
    soundManager.enable()
    
    self.sceneHelperModels = NodePath('editor-helper-models')
    self.sceneHelperModels.reparentTo(render)
    self.sceneHelperModels.setLightOff()
    
    # the axis model at 0/0/0
    axis = loader.loadModel( 'zup-axis.egg' )
    axis.reparentTo( self.sceneHelperModels )
    
    # a grid model
    gridNp = DirectGrid(parent=self.sceneHelperModels)
    
    # refresh the scenegraphbrowser
    messenger.send(EVENT_SCENEGRAPHBROWSER_REFRESH)
    
    modelController.toggleEditmode(True)
  
  def exitWorldEditMode(self):
    # save the selected model to the texturePainter
    objectEditor.setEditObject(modelController.getSelectedModel())
    # drop what we have selected
    modelController.selectModel(None)
    # disable the selecting of nodes
    modelController.toggleEditmode(False)
  
  def enterObjectEditMode(self):
    objectEditor.enableEditor()
  
  def exitObjectEditMode(self):
    objectEditor.disableEditor()
  
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
    
    def saveRecursiveChildrens(parent, eggParentData, relativeTo):
      for child in parent.getChildren():
        # save the childs data
        modelData = None
        if child.hasTag(ENABLE_SCENEGRAPHBROWSER_MODEL_TAG):
          objectId = child.getTag(EDITABLE_OBJECT_TAG)
          object = modelIdManager.getObject(objectId)
          modelData = object.getSaveData(relativeTo)
          eggParentData.addChild(modelData)
        # if there is data of the model walk the childrens
        if modelData:
          # search childrens
          saveRecursiveChildrens(child, modelData, relativeTo)
    
    # create a eggData to save the data
    eggData = EggData()
    eggData.setCoordinateSystem(1)
    # start reading the childrens of render
    relativeTo = Filename(filepath).getDirname()
    relativeTo = str(Filename.fromOsSpecific(relativeTo))
    saveRecursiveChildrens(render, eggData, relativeTo)
    # save the egg file
    eggData.writeEgg(Filename(filepath))
  
  def loadEggModelsFile(self, filepath):
    # read the eggData
    
    if filepath != None and filepath != '' and filepath != ' ':
      self.destroyAllModels()
      
      filetype = os.path.splitext(filepath)
      parentModel = SceneNodeWrapper.onCreateInstance(render, filepath)
      
      if self.getCurrentOrNextState() == 'WorldEditMode':
        # enable the editing on the objects when editing is enabled
        for model in modelIdManager.getAllModels():
          try:
            model.enableEditmode()
          except:
            pass # some objects are not part of the scene (like arrows to move etc.)
        # select no model
        modelController.selectModel(None)
      
      # refresh the scenegraphbrowser
      messenger.send(EVENT_SCENEGRAPHBROWSER_REFRESH)
  
  def destroyModel(self):
    selectedObject = modelController.getSelectedModel()
    modelController.selectModel(None)
    if selectedObject is not None:
      selectedObject.destroy()
      del selectedObject
    
    # refresh the scenegraphbrowser
    messenger.send(EVENT_SCENEGRAPHBROWSER_REFRESH)
  
  def destroyAllModels(self):
    # delete all loaded models
    modelController.selectModel(None) 
    for model in modelIdManager.getAllModels():
      if model.hasTag(EDITABLE_OBJECT_TAG):
        model.destroy()
        del model
