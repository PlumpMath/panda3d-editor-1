#!/usr/bin/env python
from direct.showbase.DirectObject import DirectObject
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectButton import DirectButton
from direct.gui.DirectScrolledList import DirectScrolledList
from pandac.PandaModules import *

from dgui.interactiveConsole.interactiveConsole import pandaConsole, INPUT_GUI, OUTPUT_PYTHON
from dgui.filebrowser import FG
from dgui.scenegraphBrowser import SceneGraphBrowser
from dgui.directWindow.src.directWindow import DirectWindow
from dgui.interactiveConsole.interactiveConsole import *
from dgui.pCameraController import cameraController
from dgui.directSidebar import *

from core.pConfigDefs import *
from core.pModelController import modelController

EDITOR_DGUI_TOGGLE_BUTTON = 'f11'

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

class EditorApp(DirectObject):
  def __init__( self, editorInstance ):
    self.enabled = False
    self.accept( EDITOR_DGUI_TOGGLE_BUTTON, self.toggle )
    self.editorInstance = editorInstance
    self.shaderAuto = False
    self.objectEditorVisible = False
  
  def toggle( self, state=None ):
    if DEBUG:
      print "I: EditorApp.toggle", state
    if state is None:
      state = not self.enabled
    
    if state:
      self.enable()
    else:
      self.disable()
    self.enabled = state
  
  def enable( self ):
    if not self.enabled:
      def nodeSelected(np): # don't forget to receive the selected node (np)
        if DEBUG:
          print "nodeSelected", np
        modelController.selectNodePath( np )
      
      def nodeRightClicked(np): # don't forget to receive the selected node (np)
        if DEBUG:
          print np.getName(),'RIGHT CLICKED, DO SOMETHING !'
      
      '''self.scenegraphBrowserWindow = DirectWindow( title='szenegraph'
                                                 , pos = ( -1.33, .55)
                                                 , virtualSize = (1, 1.5) )'''
      self.scenegraphBrowserWindow = DirectSidebar(
        frameSize=(1.07, 1.5)
      , pos=Vec3(0,0,0.0)
      , align=ALIGN_LEFT|ALIGN_BOTTOM
      , orientation=VERTICAL
      , text='szenegraph')
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
                 exclusionTag=[EXCLUDE_SCENEGRAPHBROWSER_MODEL_TAG],
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
      
      # enable console
      #console = pandaConsole( INPUT_GUI|OUTPUT_PYTHON, locals() )
      #console.toggle()
      
      sceneButtonDefinitions = [ 
        ['load', self.loadEggModelsFile, []]
      , ['save', self.saveEggModelsFile, []]
      ]
      self.createInterface(sceneButtonDefinitions, 'scene', align=ALIGN_LEFT|ALIGN_TOP, pos=Vec3(0.05,0,0))
      settingsButtonDefinitions = [
        ['pix-light', self.toggleShaderAuto, []]
      ]
      self.createInterface(settingsButtonDefinitions, 'settings', align=ALIGN_LEFT|ALIGN_TOP, pos=Vec3(0.45,0,0))
      editButtonDefinitions = [
        ['model', self.crateFilebrowserModelWrapper, ['NodePathWrapper']]
      , ['particlesystem', self.crateFilebrowserModelWrapper, ['ParticleSystemWrapper']]
      , ['spotlight', self.createModelWrapper, ['SpotLightNodeWrapper']]
      , ['directionallight', self.createModelWrapper, ['DirectionalLightNodeWrapper']]
      , ['ambientlight', self.createModelWrapper, ['AmbientLightNodeWrapper']]
      , ['pointlight', self.createModelWrapper, ['PointLightNodeWrapper']]
      , ['codeNode', self.crateFilebrowserModelWrapper, ['CodeNodeWrapper']]
      , ['GeoMipTerrain', self.crateFilebrowserModelWrapper, ['GeoMipTerrainNodeWrapper']]
      , ['destroy model', self.editorInstance.destroyModel, []]
      ]
      self.createInterface(editButtonDefinitions, 'edit', align=ALIGN_RIGHT|ALIGN_TOP, pos=Vec3(-.05,0,0))
      
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
      
      cameraController.enable()
      
      messenger.send(EDITOR_TOGGLE_ON_EVENT)
      
      self.editorObjectGuiInstance = None
      self.lastSelectedObject = None
      self.accept(EVENT_MODELCONTROLLER_SELECT_MODEL_CHANGE, self.createObjectEditor)
      
      self.accept('f5', self.saveEggModelsFile)
      self.accept('f9', self.loadEggModelsFile)
      self.accept('f11', self.toggle)
    
    self.accept(EDITOR_DGUI_TOGGLE_BUTTON, self.toggle)
    self.accept(EVENT_MODELCONTROLLER_SELECT_MODEL_CHANGE, self.modelSelected)
  
  def setObjectEditwindowToggled(self, state):
    ''' saves the state of the object related window, so you dont have to
    close/open it every time, (it stays closed if it was before)'''
    print "objectEditwindowToggled", state
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
    try:
      print "I: EditorApp.modelSelected", model
      print "  -", modelController.getSelectedModel()
      print "  -", modelController.getSelectedModel().__class__.__name__
      if self.lastSelectedObject != modelController.getSelectedModel():
        print "  - new object selected"
        # selected model has been changed
        if self.editorObjectGuiInstance is not None:
          print "  - destryoing old selected gui"
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
          #try:
          self.editorObjectGuiInstance = getattr(module, objType)(modelController.getSelectedModel(), self)
          #except:
          #  print "E: EditorApp.modelSelected: object", objType
          #  traceback.print_exc()
          self.editorObjectGuiInstance.startEdit()
        else:
          self.editorObjectGuiInstance = None
      else:
        print "  - same object selected"
        # the same object is selected again
        pass
    except:
      print "E: EditorApp.modelSelected: object", model
      traceback.print_exc()
  
  def saveEggModelsFile(self):
    if DEBUG:
      print "I: EditorApp.saveEggModelsFile:"
    FG.openFileBrowser()
    FG.accept('selectionMade', self.saveEggModelsFileCallback)
  def saveEggModelsFileCallback(self, filepath):
    if DEBUG:
      print "I: EditorApp.saveEggModelsFileCallback:", filename
    if filepath != None and filepath != '' and filepath != ' ':
      filepath = Filename.fromOsSpecific(filepath).getFullpath()
      self.editorInstance.saveEggModelsFile(filepath)
  
  def loadEggModelsFile(self):
    if DEBUG:
      print "I: EditorApp.loadEggModelsFile:"
    FG.openFileBrowser()
    FG.accept('selectionMade', self.loadEggModelsFileCallback)
  def loadEggModelsFileCallback(self, filepath):
    if DEBUG:
      print "I: EditorApp.loadEggModelsFileCallback:", filename
    if filepath != None and filepath != '' and filepath != ' ':
      filepath = Filename.fromOsSpecific(filepath).getFullpath()
      self.editorInstance.loadEggModelsFile(filepath)
  
  def createObjectEditor(self, object):
    if DEBUG:
      print "I: EditorApp.createObjectEditor:", object.__class__.__name__
    if object == self.editorObject:
      # same object is selected again
      if DEBUG:
        print "  - same object"
    else:
      if DEBUG:
        print "  - other object"
      if self.editorObject is not None:
        # destroy the current editorObject
        if DEBUG:
          print "  - is destroying old editor"
      if DEBUG:
        print "  - creating new editor"
  
  def crateFilebrowserModelWrapper(self, objectType):
    # open the file browser to select a object
    FG.openFileBrowser()
    FG.accept('selectionMade', self.onCrateFilebrowserModelWrapper, [objectType])
  def onCrateFilebrowserModelWrapper(self, objectType, filepath):
    if filepath != None and filepath != '' and filepath != ' ':
      filepath = Filename.fromOsSpecific(filepath).getFullpath()
      print "I: EditorApp.onCrateFilebrowserModelWrapper:", objectType, filepath
      modelParent = modelController.getSelectedModel()
      module = __import__("core.modules.p%s" % objectType, globals(), locals(), [objectType], -1)
      exec("objectInstance = module.%s.onCreateInstance(modelParent, filepath)" % (objectType))
      if objectInstance is not None:
        objectInstance.enableEditmode()
      messenger.send( EVENT_SCENEGRAPHBROWSER_REFRESH )
      modelController.selectModel( objectInstance )
  
  def createModelWrapper(self, type):
    # create the actual wrapper of the object
    module = __import__("core.modules.p%s" % type, globals(), locals(), [type], -1)
    modelParent = modelController.getSelectedModel()
    exec("objectInstance = module.%s.onCreateInstance(modelParent)" % type)
    if objectInstance is not None:
      objectInstance.enableEditmode()
    messenger.send( EVENT_SCENEGRAPHBROWSER_REFRESH )
    modelController.selectModel( objectInstance )
  
  def disable( self ):
    if self.enabled:
      self.ignoreAll()
      
      # hide the text
      for text in self.helpText:
        text.detachNode()
      
      #self.modelSelected(None)
      if self.editorObjectGuiInstance is not None:
        self.editorObjectGuiInstance.stopEdit()
      
      self.scenegraphBrowserWindow.detachNode()
      
      self.ButtonsWindow.detachNode()
      
      messenger.send( EDITOR_TOGGLE_OFF_EVENT )
      
      cameraController.disable()
      
      self.accept( EDITOR_DGUI_TOGGLE_BUTTON, self.toggle )
  
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
    
    height = 0.1+(itemHeight - 0.06) * len(buttonDefinitions)
    self.ButtonsWindow  = DirectSidebar(
        frameSize=(0.35, height)
      , pos=pos
      , align=align
      , text=title)
    print height
    
    myScrolledList = DirectScrolledList(
        pos = Vec3(.175, 0, height-0.05 ),
        items = buttons,
        scale = 0.5,
        parent = self.ButtonsWindow,
        numItemsVisible = len(buttons),
        forceHeight = itemHeight,
        incButton_scale = (0, 0, 0),
        decButton_scale = (0, 0, 0),
        )
  
