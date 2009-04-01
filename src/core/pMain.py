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
from core.modules.pNodePathWrapper import *
# just to initialize the painter
from core.pTexturePainter import texturePainter

DEBUG = False


class EditorClass(DirectObject): #, FSM):
  def __init__(self, parent=None, gui=None):
    # First phase: load the configurations.
    if gui == "dgui":
      from dgui.pConfig import Config
    elif gui == "wxgui":
      from wxgui.pConfig import Config
    if gui is not None:
      Config.loadConfig()
    
    # Second phase: initialize the window manager (which starts ShowBase)
    from core.pWindow import WindowManager
    if gui == "dgui":
      WindowManager.startBase(showDefaultWindow = True, allowMultipleWindows = False)
    elif gui == "wxgui":
      WindowManager.startBase(showDefaultWindow = False, allowMultipleWindows = True)
    else:
      from direct.directbase import DirectStart
    
    if parent is None:
      parent = render
    
    self.editorGui = False
    self.guiType = gui
    
    self.editModeEnabled = False
    
    soundManager.enable()
    
    self.treeParent = SceneNodeWrapper.onCreateInstance(None, 'default.egg')
  
  def toggle(self, state=None):
    ''' this function creates instances of the editor
    this is also the function that a game may use to enable/disable the editor
    '''
    if state is None:
      state = not self.editorGui
    print "I: EditorClass.toggleEditor:", state
    
    if state:
      # Fourth phase: load one of the two interface layers.
      if self.guiType == "dgui":
        from dgui.pEditorApp import EditorApp
        self.editorGui = EditorApp(self)
        self.editorGui.enable()
      elif self.guiType == "wxgui":
        # wxGui needs to be opened before the editor, as it opens the window later
        from wxgui.pEditorApp import EditorApp
        self.editorGui = EditorApp(self)
    else:
      if self.guiType == "dgui":
        self.editorGui.disable()
        self.editorGui.destroy()
        self.editorGui = None
      elif self.guiType == "wxgui":
        print "E: EditorClass.toggleEditor: wxGui cannot be closed"
  
  def toggleEditmode(self, state=None):
    ''' this function should be called by the gui, not by a game
    '''
    if state is None:
      state = self.editModeEnabled
    
    if state:
      self.__enableEditor()
    else:
      self.__disableEditor()
  
  def __enableEditor(self):
    ''' the gui will call this function and enabled the core editor using it
    '''
    if self.guiType is not None:
      if self.editModeEnabled is False:
        print "I: core.EditorClass.__enableEditor:"
        
        WindowManager.getDefaultCamera().node().getLens().setFar(5000)
        
        self.sceneHelperModels = NodePath('editor-helper-models')
        self.sceneHelperModels.reparentTo(render)
        self.sceneHelperModels.setLightOff()
        
        # the axis model at 0/0/0
        axis = loader.loadModel( 'zup-axis.egg' )
        axis.reparentTo( self.sceneHelperModels )
        
        scenePicker.toggleEditmode(True)
        #print "I: core.EditorClass.enterWorldEditMode:", modelModificator.__class__.__name__
        modelModificator.toggleEditmode(True)
        
        # enable the texturePainter
        #texturePainter.enableEditor()
        
        # a grid model
        gridNp = DirectGrid(parent=self.sceneHelperModels)
        
        # enable editmode on the object tree
        self.treeParent.setEditmodeEnabled()
        
        # refresh the scenegraphbrowser
        #messenger.send(EVENT_SCENEGRAPH_REFRESH)
        messenger.send(EVENT_SCENEGRAPH_CHANGE_ROOT, [self.treeParent])
        
        messenger.send(EVENT_MODELCONTROLLER_SELECT_OBJECT, [None])
        messenger.send(EVENT_SCENEGRAPH_REFRESH)
        
        self.editModeEnabled = True
      else:
        print "I: core.EditorClass.__enableEditor: editmode already enabled"
    else:
      print "I: core.EditorClass.__enableEditor: editmode unavailable if no gui type defined"
  
  def __disableEditor(self):
    ''' the gui will call this function and disable the core editor using it
    '''
    if self.editModeEnabled:
      # disable editmode on the object tree
      self.treeParent.setEditmodeDisabled()
      # save the selected model to the texturePainter
      #objectEditor.setEditObject(modelController.getSelectedObject())
      # drop what we have selected
      modelController.selectObject(None)
      # disable the selecting of nodes
      scenePicker.toggleEditmode(False)
      modelModificator.toggleEditmode(False)
      
      #texturePainter.disableEditor()
      
      self.editModeEnabled = False
    else:
      print "I: core.EditorClass.__disableEditor: editmode already disabled"
  
  def getData(self):
    modelData = ''
    for model in self.modelList:
      modelData += ", [%s, %s, %s, %s] \n" %  ( model.modelName
                                              , str(model.getPos(render))
                                              , str(model.getHpr(render))
                                              , str(model.getScale(render)) )
    return modelData
  
  '''def saveEggModelsFile(self, filepath):
    # walk the render tree and save the egg-links
    self.treeParent.saveAs(filepath)'''
  
  def loadEggModelsFile(self, filepath):
    
    filebase, filetype = os.path.splitext(filepath)
    if filetype == '.egg':
      print "I: EditorClass.loadEggModelsFile: NodePath"
      self.destroyScene()
      self.treeParent = NodePathWrapper.onCreateInstance(None, filepath)
      #if self.editModeEnabled:
      #  self.treeParent.setEditmodeEnabled([NodePathWrapper])
    elif filetype == '.egs':
      print "I: EditorClass.loadEggModelsFile: SceneNode"
      self.destroyScene()
      self.treeParent = SceneNodeWrapper.onCreateInstance(None, filepath)
      #if self.editModeEnabled:
      #  self.treeParent.setEditmodeEnabled([SceneNodeWrapper, NodePathWrapper])
    else:
      print "I: EditorClass.loadEggModelsFile: Unknown", filetype
      return
    
    if self.editModeEnabled:
      self.treeParent.setEditmodeEnabled()
    else:
      print "I: EditorClass.loadEggModelsFile: edit mode is disabled"
    
    # refresh the scenegraphbrowser
    messenger.send(EVENT_SCENEGRAPH_CHANGE_ROOT, [self.treeParent])
    
    if self.editModeEnabled:
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
    
    ''' # check if there are still models in the scene, which have not been deleted
    print "D: core.EditorApp.destroyScene: found obj in modelIdManager"
    for obj in modelIdManager.getAllObjects():
      if type(obj) != NodePath:
        print "  -", obj
        #if node.getNodepath().hasTag(EDITABLE_OBJECT_TAG):
          #node.destroy()
          #del node
    '''
  
  def newScene(self, filepath):
    ''' create a new scene
    '''
    print "D: core.EditorApp.newScene:", filepath
    self.destroyScene()
    self.treeParent = SceneNodeWrapper.onCreateInstance(None, '')
    self.treeParent.saveAs(filepath)
    self.treeParent.setScene(filepath)
    if self.editModeEnabled:
      self.treeParent.setEditmodeEnabled()
    messenger.send(EVENT_SCENEGRAPH_CHANGE_ROOT, [self.treeParent])
    messenger.send(EVENT_MODELCONTROLLER_SELECT_OBJECT, [None])
