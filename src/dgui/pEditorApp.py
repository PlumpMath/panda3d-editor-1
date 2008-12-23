#!/usr/bin/env python
from direct.showbase.DirectObject import DirectObject
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectButton import DirectButton
from direct.gui.DirectScrolledList import DirectScrolledList
from direct.fsm.FSM import FSM
from pandac.PandaModules import *

from dgui.filebrowser import FG
from dgui.scenegraphBrowser import SceneGraphBrowser
from dgui.directWindow.src.directWindow import DirectWindow
from dgui.pCameraController import cameraController
from dgui.directSidebar import *

from core.pConfigDefs import *
from core.pModelController import modelController
from core.pTexturePainter import texturePainter, getTextureAndStage

EDITOR_DGUI_TOGGLE_BUTTON = 'tab'
EDITOR_DGUI_DISABLE_BUTTON = 'f11'

DEBUG = False

import types
def parents( c, seen=None ):
    """Python class base-finder"""
    if type( c ) == types.ClassType:
        if seen is None:
            seen = {}
        seen[c] = None
        items = [c]
        for base in c.__bases__:
            if not seen.has_key(base):
                items.extend( parents(base, seen))
        return items
    else:
        return list(c.__mro__)

# Function to put instructions on the screen.
def addInstructions(pos, msg, mutable=False):
    return OnscreenText(text=msg, style=1, fg=(1,1,1,1),
      pos=(-1.3, pos), align=TextNode.ALeft, scale = .05, mayChange=mutable)

# Function to put title on the screen.
def addTitle(text):
    return OnscreenText(text=text, style=1, fg=(1,1,1,1),
                  pos=(1.3,-0.95), align=TextNode.ARight, scale = .07)

class EditorApp(DirectObject, FSM):
  def __init__( self, editorInstance ):
    FSM.__init__(self,'EditorApp')
    self.enabled = False
    self.editorInstance = editorInstance
    self.shaderAuto = False
    self.objectEditorVisible = False
    self.lastSelectedModel = None
    self.request('DisabledEditMode')
  
  def toggle(self, state=None):
    ''' toggle between world and object edit mode
    '''
    if state is None:
      if self.editorInstance.state == 'WorldEditMode':
        state = 'ObjectEditMode'
      elif self.editorInstance.state == 'ObjectEditMode':
        state = 'WorldEditMode'
      else:
        state = 'WorldEditMode'
    print "I: dgui.EditorApp.toggle: toggling to", state
    
    self.editorInstance.toggle(state)
    self.request(self.editorInstance.state)
    
    self.accept(EDITOR_DGUI_TOGGLE_BUTTON, self.toggle)
    self.accept(EDITOR_DGUI_DISABLE_BUTTON, self.disable)
  
  def disable(self, state=None):
    if state is None:
      if self.editorInstance.state == 'DisabledEditMode':
        state = 'WorldEditMode'
      else:
        state = 'DisabledEditMode'
    print "I: dgui.EditorApp.disable: toggling to", state
    
    self.editorInstance.toggle(state)
    self.request(self.editorInstance.state)
  
  def enterDisabledEditMode(self):
    cameraController.disable()
  def exitDisabledEditMode(self):
    cameraController.enable()
  
  def enterWorldEditMode(self):
    def nodeSelected(np): # don't forget to receive the selected node (np)
      modelController.selectNodePath( np )
    
    def nodeRightClicked(np): # don't forget to receive the selected node (np)
      if DEBUG:
        print np.getName(),'RIGHT CLICKED, DO SOMETHING !'
    
    self.scenegraphBrowserWindow = DirectSidebar(
      frameSize=(1.07, 1.5)
    , pos=Vec3(0,0,0.0)
    , align=ALIGN_LEFT|ALIGN_BOTTOM
    , orientation=VERTICAL
    , text='scenegraph')
    # create SceneGraphBrowser and point it on aspect2d
    self.scenegraphBrowser = SceneGraphBrowser(
               parent=self.scenegraphBrowserWindow, # where to attach SceneGraphBrowser frame
               root=render, # display children under this root node
               command=nodeSelected, # user defined method, executed when a node get selected,
                                     # with the selected node passed to it
               contextMenu=nodeRightClicked,
               # selectTag and noSelectTag are used to filter the selectable nodes.
               # The unselectable nodes will be grayed.
               # You should use only selectTag or noSelectTag at a time. Don't use both at the same time.
               selectTag=[ENABLE_SCENEGRAPHBROWSER_MODEL_TAG, EDITABLE_OBJECT_TAG],   # only nodes which have the tag(s) are selectable. You could use multiple tags.
               #noSelectTag=['noSelect','dontSelectMe'], # only nodes which DO NOT have the tag(s) are selectable. You could use multiple tags.
               # nodes which have exclusionTag wouldn't be displayed at all
               frameSize=(1,1.4),
               font=None, titleScale=.05, itemScale=.035, itemTextScale=1.2, itemTextZ=0,
               rolloverColor=(1,.8,.2,1),
               collapseAll=0, # initial tree state
               suppressMouseWheel=1,  # 1 : blocks mouse wheel events from being sent to all other objects.
                                      #     You can scroll the window by putting mouse cursor
                                      #     inside the scrollable window.
                                      # 0 : does not block mouse wheel events from being sent to all other objects.
                                      #     You can scroll the window by holding down the modifier key
                                      #     (defined below) while scrolling your wheel.
               modifier='control'  # shift/control/alt
               )
    self.scenegraphBrowser.accept(EVENT_SCENEGRAPHBROWSER_REFRESH,self.scenegraphBrowser.refresh)
    self.accept( 'r', messenger.send, [EVENT_SCENEGRAPHBROWSER_REFRESH] )
    
    sceneButtonDefinitions = [ 
      ['load', self.loadEggModelsFile, []]
    , ['save', self.saveEggModelsFile, []]
    ]
    self.sceneButtons = self.createInterface(sceneButtonDefinitions, 'scene', align=ALIGN_LEFT|ALIGN_TOP, pos=Vec3(0.05,0,0))
    settingsButtonDefinitions = [
      ['pix-light', self.toggleShaderAuto, []]
    ]
    self.settingsButtons = self.createInterface(settingsButtonDefinitions, 'settings', align=ALIGN_LEFT|ALIGN_TOP, pos=Vec3(0.45,0,0))
    nodeButtonDefinitions = [
      ['model', self.createFilebrowserModelWrapper, ['NodePathWrapper']]
    , ['particlesystem', self.createFilebrowserModelWrapper, ['ParticleSystemWrapper']]
    , ['codeNode', self.createFilebrowserModelWrapper, ['CodeNodeWrapper']]
    , ['GeoMipTerrain', self.createFilebrowserModelWrapper, ['GeoMipTerrainNodeWrapper']]
    , ['sound', self.createFilebrowserModelWrapper, ['SoundNodeWrapper']]
    ]
    self.nodeButtons = self.createInterface(nodeButtonDefinitions, 'nodes', align=ALIGN_RIGHT|ALIGN_TOP, pos=Vec3(-.85,0,0))
    lightButtonDefinitions = [
      ['spotlight', self.createModelWrapper, ['SpotLightNodeWrapper']]
    , ['directionallight', self.createModelWrapper, ['DirectionalLightNodeWrapper']]
    , ['ambientlight', self.createModelWrapper, ['AmbientLightNodeWrapper']]
    , ['pointlight', self.createModelWrapper, ['PointLightNodeWrapper']]
    ]
    self.lightButtons = self.createInterface(lightButtonDefinitions, 'lights', align=ALIGN_RIGHT|ALIGN_TOP, pos=Vec3(-.45,0,0))
    editButtonDefinitions = [
      ['duplicate', self.duplicateModelWrapper, []]
    , ['destroy', self.editorInstance.destroyModel, []]
    ]
    self.editButtons = self.createInterface(editButtonDefinitions, 'edit', align=ALIGN_RIGHT|ALIGN_TOP, pos=Vec3(-.05,0,0))
    
    # some help text nodes
    self.helpText = list()
    self.helpText.append( addTitle("Panda3D: Simple scene editor") )
    helpTexts = [ "LeftMouse: select object to move, select again to rotate, select again to scale"
                , "MittleMouse: press & drag to rotate camera, turn to zoom (or page_up/down)"
                , "RightMouse: press & drag to move camera pivot"
                , "%s: Toggle Editor On/off (currently buggy)" % EDITOR_DGUI_TOGGLE_BUTTON.upper()
                , "F5: save scene      F9: load scene" ]
    helpTexts = []
    for i in xrange( len(helpTexts) ):
      self.helpText.append( addInstructions(1.0-0.05*(i+1), helpTexts[i]) )
    for text in self.helpText:
      text.show()
    
    messenger.send(EDITOR_MODE_WORLD_EDIT)
    
    self.editorObjectGuiInstance = None
    self.lastSelectedObject = None
    self.accept(EVENT_MODELCONTROLLER_SELECT_MODEL_CHANGE, self.createObjectEditor)
    
    self.accept(EVENT_MODELCONTROLLER_SELECT_MODEL_CHANGE, self.modelSelected)
  
  def exitWorldEditMode(self):
    # hide the text
    for text in self.helpText:
      text.detachNode()
    
    #self.modelSelected(None)
    if self.editorObjectGuiInstance is not None:
      self.editorObjectGuiInstance.stopEdit()
    
    self.scenegraphBrowserWindow.destroy()
    self.scenegraphBrowserWindow.detachNode()
    
    self.sceneButtons.destroy()
    self.sceneButtons.detachNode()
    self.settingsButtons.destroy()
    self.settingsButtons.detachNode()
    self.nodeButtons.destroy()
    self.nodeButtons.detachNode()
    self.lightButtons.destroy()
    self.lightButtons.detachNode()
    self.editButtons.destroy()
    self.editButtons.detachNode()
    
    messenger.send( EDITOR_MODE_DISABLED )
  
  def enterObjectEditMode(self):
    texturePainter.enableEditor()
    model = modelController.previouslySelectedModel
    if model:
      texStages = getTextureAndStage(model)
      if len(texStages) > 0:
        texturePainter.startEdit(model, texStages[0][1])
  
  def exitObjectEditMode(self):
    texturePainter.stopEdit()
    texturePainter.disableEditor()
  
  def duplicateModelWrapper(self):
    originalModel = modelController.getSelectedModel()
    objectInstance = originalModel.makeCopy(originalModel)
    if objectInstance is not None:
      objectInstance.enableEditmode()
    #objectInstance.loadFromData( originalModel.getSaveData('.') )
    messenger.send( EVENT_SCENEGRAPHBROWSER_REFRESH )
    modelController.selectModel( objectInstance )
  
  def setObjectEditwindowToggled(self, state):
    ''' saves the state of the object related window, so you dont have to
    close/open it every time, (it stays closed if it was before)'''
    self.objectEditorVisible = state
  def getObjectEditwindowToggled(self):
    return self.objectEditorVisible
  
  def toggleShaderAuto(self, state=None):
    if state is None:
      state = not self.shaderAuto
    self.shaderAuto = state
    if self.shaderAuto:
      render.setShaderAuto()
    else:
      render.setShaderOff()
  
  def modelSelected(self, model):
    #try:
      if self.lastSelectedObject != modelController.getSelectedModel():
        # selected model has been changed
        if self.editorObjectGuiInstance is not None:
          # destroy gui instance of old object
          self.editorObjectGuiInstance.stopEdit()
        
        # save the object as the new object
        self.lastSelectedObject = modelController.getSelectedModel()
        
        if modelController.getSelectedModel() is not None:
          # create gui instance of new object
          objType = modelController.getSelectedModel().__class__
          # the codenode inherits from the real class we use...
          # but we need the name of the internal class, 
          bases = list()
          for base in objType.__bases__:
            bases.append(base.__name__)
          if 'CodeNodeWrapper' in bases:
            objType = 'CodeNodeWrapper'
          else:
            objType = objType.__name__
          module = __import__("dgui.modules.p%s" % objType, globals(), locals(), [objType], -1)
          try:
            self.editorObjectGuiInstance = getattr(module, objType)(modelController.getSelectedModel(), self)
          except TypeError:
            print "E: dgui.EditorApp.modelSelected: object", objType, modelController.getSelectedModel()
            traceback.print_exc()
          self.editorObjectGuiInstance.startEdit()
        else:
          self.editorObjectGuiInstance = None
      else:
        # the same object is selected again
        pass
    #except:
    #  print "E: EditorApp.modelSelected: object", model
    #  traceback.print_exc()
  
  def saveEggModelsFile(self):
    FG.openFileBrowser()
    FG.accept('selectionMade', self.saveEggModelsFileCallback)
  def saveEggModelsFileCallback(self, filepath):
    if filepath != None and filepath != '' and filepath != ' ':
      filepath = Filename.fromOsSpecific(filepath).getFullpath()
      self.editorInstance.saveEggModelsFile(filepath)
  
  def loadEggModelsFile(self):
    FG.openFileBrowser()
    FG.accept('selectionMade', self.loadEggModelsFileCallback)
  def loadEggModelsFileCallback(self, filepath):
    if filepath != None and filepath != '' and filepath != ' ':
      filepath = Filename.fromOsSpecific(filepath).getFullpath()
      self.editorInstance.loadEggModelsFile(filepath)
  
  def createObjectEditor(self, object):
    if object == self.editorObject:
      # same object is selected again
      pass
    else:
      if self.editorObject is not None:
        # destroy the current editorObject
        pass
  
  def createFilebrowserModelWrapper(self, objectType):
    # open the file browser to select a object
    FG.openFileBrowser()
    FG.accept('selectionMade', self.onCreateFilebrowserModelWrapper, [objectType])
  def onCreateFilebrowserModelWrapper(self, objectType, filepath):
    if filepath != None and filepath != '' and filepath != ' ':
      filepath = Filename.fromOsSpecific(filepath).getFullpath()
      modelParent = modelController.getSelectedModel()
      module = __import__("core.modules.p%s" % objectType, globals(), locals(), [objectType], -1)
      #exec("objectInstance = module.%s.onCreateInstance(modelParent, filepath)" % (objectType))
      objectInstance = getattr(module, objectType).onCreateInstance(modelParent, filepath)
      if objectInstance is not None:
        objectInstance.enableEditmode()
      messenger.send( EVENT_SCENEGRAPHBROWSER_REFRESH )
      modelController.selectModel( objectInstance )
  
  def createModelWrapper(self, type):
    # create the actual wrapper of the object
    module = __import__("core.modules.p%s" % type, globals(), locals(), [type], -1)
    modelParent = modelController.getSelectedModel()
    #exec("objectInstance = module.%s.onCreateInstance(modelParent)" % type)
    objectInstance = getattr(module, type).onCreateInstance(modelParent)
    if objectInstance is not None:
      objectInstance.enableEditmode()
    messenger.send( EVENT_SCENEGRAPHBROWSER_REFRESH )
    modelController.selectModel( objectInstance )
  
  def createInterface( self, buttonDefinitions, title, align, pos ):
    buttons = list()
    for name, functionCall, extraArgs in buttonDefinitions:
      button = DirectButton(text = (name, name, name, name),
                      text_scale=0.1, borderWidth = (0.01, 0.01),
                      relief=2,
                      command=functionCall,
                      extraArgs=extraArgs,
                      frameSize=(-0.3,0.3,-.02,.08))
      buttons.append( button )
    itemHeight = 0.11
    
    height = 0.03+(itemHeight - 0.055) * len(buttonDefinitions)
    buttonsWindow  = DirectSidebar(
        frameSize=(0.35, height)
      , pos=pos
      , align=align
      , text=title)
    
    myScrolledList = DirectScrolledList(
        pos = Vec3(.175, 0, height-0.05 ),
        items = buttons,
        scale = 0.5,
        parent = buttonsWindow,
        numItemsVisible = len(buttons),
        forceHeight = itemHeight,
        incButton_scale = (0, 0, 0),
        decButton_scale = (0, 0, 0),
        )
    
    return buttonsWindow
