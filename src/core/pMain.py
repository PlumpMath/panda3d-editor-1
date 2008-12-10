#!/usr/bin/env python

import pickle
import os, sys
import random
import traceback

from direct.task.Task import Task
from pandac.PandaModules import *
from direct.showbase.DirectObject import DirectObject

#from editorObjects import *
from core.pModelController import modelController
#from core.pCameraController import cameraController
from core.pModelIdManager import modelIdManager
from core.pConfigDefs import *
# this is a bugfixed / slightly changed version of DirectGrid
from core.pGrid import DirectGrid
from core.pMouseHandler import mouseHandler

DEBUG = False

class EditorClass(DirectObject):
  def __init__(self, parentNodePath):
    self.parentNodePath = render
    
    self.enabled = False
    # enable the editor
    self.toggle( False ) # must be called with eighter False or True
  
  def toggle(self, state=None):
    if state is None:
      state = not self.enabled
    
    if state:
      self.enableEditmode()
    else:
      self.disableEditmode()
    
    self.enabled = state
  
  def enableEditmode(self):
    if not self.enabled:
      self.sceneHelperModels = NodePath('editor-helper-models')
      self.sceneHelperModels.reparentTo(render)
      self.sceneHelperModels.setTag(EXCLUDE_SCENEGRAPHBROWSER_MODEL_TAG, '')
      self.sceneHelperModels.setLightOff()
      
      # the axis model at 0/0/0
      axis = loader.loadModel( 'zup-axis.egg' )
      axis.reparentTo( self.sceneHelperModels )
      
      # a grid model
      gridNp = DirectGrid(parent=self.sceneHelperModels)
      
      if DISABLE_SHADERS_WHILE_EDITING:
        render.setShaderOff(10000)
      
      for model in modelIdManager.getAllModels():
        if model.hasTag( EDITABLE_OBJECT_TAG ):
          model.enableEditmode()
      
      modelController.toggle(True)
      
      self.accept(EDITOR_TOGGLE_OFF_EVENT, self.toggle, [False])
      
      # refresh the scenegraphbrowser
      messenger.send(EVENT_SCENEGRAPHBROWSER_REFRESH)
  
  def disableEditmode(self):
    if self.enabled:
      if DISABLE_SHADERS_WHILE_EDITING:
        render.setShaderOff(-1)
      # drop what we have selected
      modelController.selectModel( None )
      # ignoreAll events
      self.ignoreAll()
      
      for model in modelIdManager.getAllModels():
        if model.hasTag(EDITABLE_OBJECT_TAG):
          model.disableEditmode()
      
      modelController.toggle(False)
    
    self.accept( EDITOR_TOGGLE_ON_EVENT, self.toggle, [True] )
  
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
      for child in parent.getChildrenAsList():
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
    relativeTo = os.path.dirname(filepath)
    if DEBUG:
      print "I: EditorClass.saveEggModelsFile: relativeTo:", relativeTo, filepath
    saveRecursiveChildrens(render, eggData, relativeTo)
    # save the egg file
    eggData.writeEgg(Filename(filepath))
  
  def loadEggModelsFile(self, filename):
    # read the eggData
    
    def loadRecursiveChildrens(eggParentData, parent, transform, filepath):
      if type(eggParentData) == EggData:
        # search the childrens
        for childData in eggParentData.getChildren():
          # search the children
          parent = loadRecursiveChildrens(childData, parent, transform, filepath)
      
      elif type(eggParentData) == EggGroup:
        
        # a eggGroup modifies the matrix of the model
        if type(eggParentData) == EggGroup:
          # convert the matrix from double to single
          mat4d = eggParentData.getTransform3d()
          mat4 = Mat4()
          for x in xrange(4):
              for y in xrange(4):
                  mat4.setCell(x, y, mat4d.getCell(x,y))
          # multiply the matrix for later applial onto model
          transform = mat4 * transform
        
        if eggParentData.hasTag(MODEL_WRAPPER_TYPE_TAG):
          wrapperType = eggParentData.getTag(MODEL_WRAPPER_TYPE_TAG)
          wrapperTypeDecap = wrapperType[0].lower() + wrapperType[1:]
          try:
            # import the module responsible for handling the data
            module = __import__('core.modules.p%s' % wrapperType, globals(), locals(), [wrapperType], -1)
            print "I: EditorClass.loadEggModelsFile"
            print "  - parent:", parent
            print "  - filepath:", filepath
            print "  - module:", wrapperType
            # load the eggParentData using the module
            object = getattr(module, wrapperType).loadFromEggGroup(eggParentData, parent, filepath)
          except:
            print "I: EditorClass.loadEggModelsFile: unknown or invalid entry"
            traceback.print_exc()
            print "I: --- start of invalid data ---"
            print eggParentData
            print "I: --- end of invalid data ---"
            object = parent.attachNewNode('%s-failed' % wrapperType)
          if object is not None:
            # apply the transformation on the object
            object.setMat(transform)
            transform = Mat4.identMat()
            # if it contains additional childrens recurse into them
            for childData in eggParentData.getChildren()[1:]:
              # search the children
              loadRecursiveChildrens(childData, object, transform, filepath)
          else:
            print "E: core.EditorClass.loadEggModelsFile: no object returned (most likely error in module)"
            print "  -", wrapperType
        else:
          if DEBUG:
            print "eggParentData.getTag: has no tag"
          # search for childrens
          for childData in eggParentData.getChildren():
            # search the children
            parent = loadRecursiveChildrens(childData, parent, transform, filepath)
      else:
        if DEBUG:
          print "W: EditorApp.loadEggModelsFile.loadRecursiveChildrens:"
          print "   - skipping unkown eggData", type(eggParentData)
      
      return parent
    
    if filename != None and filename != '' and filename != ' ':
      # destroy old models
      self.destroyAllModels()
      
      eggData = EggData()
      eggData.read(Filename(filename))
      
      # the absolute path of the file we load, referenced files are relative
      # to this path
      filepath = os.path.dirname(os.path.abspath(filename))
      
      # add the path to the model-path
      print "I: EditorApp.loadEggModelsFile: adding to model-path:", filepath
      from pandac.PandaModules import getModelPath
      getModelPath().appendPath(filepath)
      # read the eggData
      loadRecursiveChildrens(eggData, render, Mat4.identMat(), filepath)
      
      if self.enabled:
        # enable the editing on the objects when editing is enabled
        for model in modelIdManager.getAllModels():
          if model.hasTag(EDITABLE_OBJECT_TAG):
            model.enableEditmode()
        # select no model
        modelController.selectModel(None)
      
      # refresh the scenegraphbrowser
      messenger.send(EVENT_SCENEGRAPHBROWSER_REFRESH)
  
  def destroyModel(self):
    #print "editor.editorClass.destroyModel"
    selectedObject = modelController.getSelectedModel()
    modelController.selectModel(None)
    if selectedObject is not None:
      selectedObject.destroy()
      del selectedObject
    
    # refresh the scenegraphbrowser
    messenger.send(EVENT_SCENEGRAPHBROWSER_REFRESH)
  
  def destroyAllModels(self):
    if DEBUG:
      print "editor.editorClass.destroyAllModels"
    # delete all loaded models
    modelController.selectModel(None) 
    for model in modelIdManager.getAllModels():
      if model.hasTag(EDITABLE_OBJECT_TAG):
        model.destroy()
        del model
    print modelIdManager.getAllModels()
