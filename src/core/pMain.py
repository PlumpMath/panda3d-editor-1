#!/usr/bin/env python

'''import sys,os
# define model path, required if this settings is missing in the Config.pp
from pandac.PandaModules import *
for path in ['.', './data/models']:
  getModelPath( ).appendPath( path )
  sys.path.append( path )'''

#loadPrcFileData("", "sync-video 0")

#if False:
#  loadPrcFileData("", "want-directtools #t")
#  loadPrcFileData("", "want-tk #t")

import pickle
import os, sys
import random

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


class EditorClass( DirectObject ):
  def __init__( self, parentNodePath ):
    print "editor.editorClass.__init__"
    self.parentNodePath = render
    
    self.enabled = False
    # enable the editor
    self.toggle( False ) # must be called with eighter False or True
  
  def toggle( self, state=None ):
    if state is None:
      state = not self.enabled
    
    if state:
      self.enableEditmode()
    else:
      self.disableEditmode()
    
    self.enabled = state
  
  def enableEditmode( self ):
    #print "I: main.enableEditmode"
    if not self.enabled:
      self.sceneHelperModels = NodePath( 'editor-helper-models' )
      self.sceneHelperModels.reparentTo( render )
      self.sceneHelperModels.setTag( EXCLUDE_SCENEGRAPHBROWSER_MODEL_TAG, '' )
      self.sceneHelperModels.setLightOff()
      # the axis model at 0/0/0
      axis = loader.loadModel( 'zup-axis.egg' )
      axis.reparentTo( self.sceneHelperModels )
      # a grid model
      gridNp = DirectGrid( parent=self.sceneHelperModels )
      
      if DISABLE_SHADERS_WHILE_EDITING:
        render.setShaderOff(10000)
      self.accept( 'f5', self.saveEggModelsFile, ['testModelsFile'] )
      self.accept( 'f9', self.loadEggModelsFile, ['testModelsFile'] )
      self.accept( 'f11', self.toggle )
      
      for model in modelIdManager.getAllModels():
        if model.hasTag( EDITABLE_OBJECT_TAG ):
          model.enableEditmode()
      
#      cameraController.enable()
      modelController.toggle( True )
      
      self.accept( EDITOR_TOGGLE_OFF_EVENT, self.toggle, [False] )
  
  def disableEditmode( self ):
    if self.enabled:
      if DISABLE_SHADERS_WHILE_EDITING:
        render.setShaderOff(-1)
      # drop what we have selected
      modelController.selectModel( None )
      # ignoreAll events
      self.ignoreAll()
      
      for model in modelIdManager.getAllModels():
        if model.hasTag( EDITABLE_OBJECT_TAG ):
          model.disableEditmode()
      
#      cameraController.disable()
      modelController.toggle( False )
    
    self.accept( EDITOR_TOGGLE_ON_EVENT, self.toggle, [True] )
  
  def getData( self ):
    modelData = ''
    for model in self.modelList:
      modelData += ", [%s, %s, %s, %s] \n" %  ( model.modelName
                                              , str(model.getPos(render))
                                              , str(model.getHpr(render))
                                              , str(model.getScale(render)) )
    return modelData
  
  # open a dialogue to select a file
  '''def selectModelName( self ):
    FG.openFileBrowser()
    FG.accept('selectionMade', self.selectModelNameFinished)
  def selectModelNameFinished( self, filename ):
    # check if model file is in pandaModelPath
    from pandac.PandaModules import getModelPath
    pandaPath = None
    filename = str(Filename.fromOsSpecific(filename))
    for searchPath in str(getModelPath()).split():
        if searchPath in filename:
            pandaPath = searchPath
            print "I: model found in pandaModelPath %s" % pandaPath
            break
    if pandaPath is None:
        pandaPath = '/'.join(filename.split('/')[:-1])
        print "W: adding %s to pandaModelPath" % pandaPath
        from pandac.PandaModules import getModelPath, getTexturePath, getSoundPath
        getModelPath( ).appendPath( pandaPath )
        getTexturePath( ).appendPath( pandaPath )
        getSoundPath( ).appendPath( pandaPath )
    filename = filename.replace( pandaPath, '.' )
#    print "new model selected", filename
    self.helpText[-2].setText( "selected model: %s" % filename )
    self.modelFilename = filename'''
  
  def saveEggModelsFile( self, filename ):
    # walk the render tree and save the egg-links
    
    def saveRecursiveChildrens( parent, eggParentData, relativeTo ):
      for child in parent.getChildrenAsList():
        # save the childs data
        modelData = None
        if child.hasTag(ENABLE_SCENEGRAPHBROWSER_MODEL_TAG):
          objectId = child.getTag( EDITABLE_OBJECT_TAG )
          object = modelIdManager.getObject( objectId )
          modelData = object.getSaveData( relativeTo )
          eggParentData.addChild(modelData)
        # if there is data of the model walk the childrens
        if modelData:
          # search childrens
          saveRecursiveChildrens( child, modelData, relativeTo )
    
    # create a eggData to save the data
    eggData = EggData()
    eggData.setCoordinateSystem(1)
    # start reading the childrens of render
    relativeTo = os.getcwd()
    saveRecursiveChildrens( render, eggData, relativeTo )
    # save the egg file
    eggData.writeEgg(Filename(filename+".egg"))
  
  def loadEggModelsFile( self, filename ):
    # read the eggData
    
    def loadRecursiveChildrens( eggParentData, parent, transform ):
      #print type(eggParentData)#, dir(eggParentData)
      if type(eggParentData) == EggData:
        # search the childrens
        for childData in eggParentData.getChildren():
          # search the children
          parent = loadRecursiveChildrens( childData, parent, transform )
      
      elif type(eggParentData) == EggGroup:
        
        # a eggGroup modifies the matrix of the model
        if type(eggParentData) == EggGroup:
          # convert the matrix from double to single
          mat4d = eggParentData.getTransform3d()
          mat4 = Mat4()
          for x in xrange(4):
              for y in xrange(4):
                  mat4.setCell( x, y, mat4d.getCell(x,y) )
          # multiply the matrix for later applial onto model
          transform = mat4 * transform
        
        if eggParentData.hasTag( MODEL_WRAPPER_TYPE_TAG ):
          wrapperType = eggParentData.getTag( MODEL_WRAPPER_TYPE_TAG )
          wrapperTypeDecap = wrapperType[0].lower() + wrapperType[1:]
          #print "eggParentData.getTag:", wrapperType, wrapperTypeDecap
          execStmt = "from core.modules.p%s import %s" % (wrapperType, wrapperType) #(wrapperTypeDecap, wrapperType)
          exec execStmt in locals()
          execStmt = "object = "+wrapperType+".loadFromEggGroup(eggParentData, parent)"
          exec execStmt in locals()
          object.setMat( transform )
          transform = Mat4().identMat()
          #modelController.selectModel( object )
          # if it contains additional childrens recurse into them
          for childData in eggParentData.getChildren()[1:]:
            # search the children
            loadRecursiveChildrens( childData, object, transform )
        else:
          print "eggParentData.getTag: has no tag"
          # search for childrens
          for childData in eggParentData.getChildren():
            # search the children
            parent = loadRecursiveChildrens( childData, parent, transform )
      
      else:
        print "W: main.loadEggModelsFile.loadRecursiveChildrens:"
        print "   - skipping unkown eggData", type(eggParentData)
      
      return parent
    
    # destroy old models
    self.destroyAllModels()
    
    eggData = EggData()
    eggData.read(Filename(filename+".egg"))
    
    loadRecursiveChildrens( eggData, render, Mat4.identMat() )
    
    if self.enabled:
      # enable the editing on the objects when editing is enabled
      for model in modelIdManager.getAllModels():
        if model.hasTag( EDITABLE_OBJECT_TAG ):
          model.enableEditmode()
      # select no model
      modelController.selectModel( None )
      # refresh the scenegraphbrowser
      messenger.send( EVENT_SCENEGRAPHBROWSER_REFRESH )
  
  def destroyModel( self ):
    #print "editor.editorClass.destroyModel"
    selectedObject = modelController.getSelectedModel()
    modelController.selectModel( None )
    if selectedObject is not None:
      selectedObject.destroy()
      del selectedObject
    
    self.scenegraphBrowser.refresh()
  
  def destroyAllModels( self ):
    print "editor.editorClass.destroyAllModels"
    # delete all loaded models
    modelController.selectModel( None ) 
    for model in modelIdManager.getAllModels():
      if model.hasTag( EDITABLE_OBJECT_TAG ):
        model.destroy()
        del model
    print modelIdManager.getAllModels()
