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
from core.pTexturePainter import texturePainter, getTextureAndStage

DEBUG = False

class EditorClass(DirectObject, FSM):
  def __init__(self, parentNodePath):
    FSM.__init__(self,'EditorClass')
    self.parentNodePath = render
    
    self.accept( 'DisabledEditMode', self.request, ['DisabledEditMode'] )
    self.accept( 'WorldEditMode', self.request, ['WorldEditMode'] )
    self.accept( 'ObjectEditMode', self.request, ['ObjectEditMode'] )
    
    self.request('DisabledEditMode')
  
  def enterDisabledEditMode(self):
    # drop what we have selected
    modelController.selectModel( None )
    # disable the selecting of nodes
    modelController.toggleEditmode(False)
    # disable edit mode on all nodes
    for model in modelIdManager.getAllModels():
      if model.hasTag(EDITABLE_OBJECT_TAG):
        model.disableEditmode()
  def exitDisabledEditMode(self):
    # enable editmode on all nodes
    for model in modelIdManager.getAllModels():
      try:    model.enableEditmode()
      except: pass # some objects are not wrappers (like arrows to move etc.)
    # allow selecting of nodes
    modelController.toggleEditmode(True)
  
  def enterWorldEditMode(self):
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
  
  def exitWorldEditMode(self):
    # save the selected model to the texturePainter
    texturePainter.selectPaintModel(modelController.getSelectedModel())
    
  
  def enterObjectEditMode(self):
    texturePainter.enableEditor()
    texStages = texturePainter.getStages()
    if len(texStages) > 0:
      texturePainter.startEdit(texStages[0][1])
    '''
    texStage = texturePainter.getTextureStage(0)
    if texStage is None:
      print "generating texStage"
      texturePainter.addStageByNameSize(name='test')
      texStage = texturePainter.getTextureStage(0)
    texturePainter.selectPaintStage(texStage)
    texturePainter.startEdit()
    '''
  def exitObjectEditMode(self):
    texturePainter.stopEdit()
    texturePainter.disableEditor()
  
  def toggle(self, state=None):
    if state is None:
      # switch to next mode
      if self.state == 'DisabledEditMode':
        state = 'WorldEditMode'
      elif self.state == 'WorldEditMode':
        state = 'ObjectEditMode'
      elif self.state == 'ObjectEditMode':
        state = 'DisabledEditMode'
      else:
        state = 'DisabledEditMode'
        print "W: EditorClass.toggle: unknown previous mode", self.state, "setting to", state
    
    if state in ['DisabledEditMode', 'WorldEditMode', 'ObjectEditMode']:
      self.request(state)
    else:
      self.request('DisabledEditMode')
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
  
  def loadEggModelsFile(self, filename):
    # read the eggData
    
    def loadRecursiveChildrens(eggParentData, parent, transform, filepath, loadedObjects):
      if type(eggParentData) == EggData:
        # search the childrens
        for childData in eggParentData.getChildren():
          # search the children
          parent, loadedObjects = loadRecursiveChildrens(childData, parent, transform, filepath, loadedObjects)
      
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
            # load the eggParentData using the module
            object = getattr(module, wrapperType).loadFromEggGroup(eggParentData, parent, filepath)
            # append loaded object to list
            loadedObjects.append([object, eggParentData])
          except:
            print "W: EditorClass.loadEggModelsFile: unknown or invalid entry"
            traceback.print_exc()
            print "W: --- start of invalid data ---"
            print eggParentData
            print "W: --- end of invalid data ---"
            object = parent.attachNewNode('%s-failed' % wrapperType)
          if object is not None:
            # apply the transformation on the object
            object.setMat(transform)
            transform = Mat4.identMat()
            # if it contains additional childrens recurse into them
            for childData in eggParentData.getChildren()[1:]:
              # search the children
              loadRecursiveChildrens(childData, object, transform, filepath, loadedObjects)
          else:
            print "E: core.EditorClass.loadEggModelsFile: no object returned (most likely error in module)"
            print "  -", wrapperType
        else:
          # search for childrens
          for childData in eggParentData.getChildren():
            # search the children
            parent, loadedObjects = loadRecursiveChildrens(childData, parent, transform, filepath, loadedObjects)
      else:
        if DEBUG:
          print "W: EditorApp.loadEggModelsFile.loadRecursiveChildrens:"
          print "   - skipping unkown eggData", type(eggParentData)
      
      return parent, loadedObjects
    
    if filename != None and filename != '' and filename != ' ':
      p3filename = Filename.fromOsSpecific(filename)
      p3filename.makeAbsolute()
      # destroy old models
      self.destroyAllModels()
      
      eggData = EggData()
      eggData.read(p3filename)
      
      # the absolute path of the file we load, referenced files are relative
      # to this path
      
      filepath = p3filename.getDirname()
      #filepath = str(Filename.fromOsSpecific(filepath))
      
      # add the path to the model-path
      from pandac.PandaModules import getModelPath
      getModelPath().appendPath(filepath)
      # read the eggData
      parent, loadedObjects = loadRecursiveChildrens(eggData, render, Mat4.identMat(), filepath, list())
      
      for objectInstance, eggData in loadedObjects:
        objectInstance.loadFromData( eggData, filepath )
      
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
