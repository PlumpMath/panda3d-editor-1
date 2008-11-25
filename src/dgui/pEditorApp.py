#!/usr/bin/env python
from direct.showbase.DirectObject import DirectObject
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectButton import DirectButton
from direct.gui.DirectScrolledList import DirectScrolledList

from dgui.interactiveConsole.interactiveConsole import pandaConsole, INPUT_GUI, OUTPUT_PYTHON
from dgui.filebrowser import FG
from dgui.scenegraphBrowser import SceneGraphBrowser
from dgui.directWindow.src.directWindow import DirectWindow
from dgui.interactiveConsole.interactiveConsole import *
from dgui.pCameraController import cameraController

from core.pConfigDefs import *
from core.pModelController import modelController

EDITOR_DGUI_TOGGLE_BUTTON = 'f11'

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
    #cameraController = CameraController()
  
  def toggle( self, state=None ):
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
        #print "nodeSelected", np
        modelController.selectNodePath( np )
      
      def nodeRightClicked(np): # don't forget to receive the selected node (np)
        print np.getName(),'RIGHT CLICKED, DO SOMETHING !'
      
      self.scenegraphBrowserWindow = DirectWindow( title='window1'
                                                 , pos = ( -1.33, .55)
                                                 , virtualSize = (1, 1.5) )
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
                 selectTag=[ENABLE_SCENEGRAPHBROWSER_MODEL_TAG],   # only nodes which have the tag(s) are selectable. You could use multiple tags.
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
      console = pandaConsole( INPUT_GUI|OUTPUT_PYTHON, locals() )
      console.toggle()
      
      buttonDefinitions = [ ['model', self.crateFilebrowserModelWrapper, ['NodePathWrapper']]
                          , ['particlesystem', self.crateFilebrowserModelWrapper, ['ParticleSystemWrapper']]
                          , ['spotlight', self.createModelWrapper, ['SpotLightNodeWrapper']]
                          , ['directionallight', self.createModelWrapper, ['DirectionalLightNodeWrapper']]
                          , ['ambientlight', self.createModelWrapper, ['AmbientLightNodeWrapper']]
                          , ['pointlight', self.createModelWrapper, ['PointLightNodeWrapper']]
                          , ['codeNode', self.crateFilebrowserModelWrapper, ['CodeNodeWrapper']]
                          , ['destroy model', self.editorInstance.destroyModel, []]
                          , ['load', self.loadEggModelsFile, []]
                          , ['save', self.saveEggModelsFile, []] ]
      self.createInterface(buttonDefinitions)
      
      # some help text nodes
      self.helpText = list()
      self.helpText.append( addTitle("Panda3D: Simple scene editor") )
      helpTexts = [ "LeftMouse: select object to move, select again to rotate, select again to scale"
                  , "MittleMouse: press & drag to rotate camera, turn to zoom (or page_up/down)"
                  , "RightMouse: press & drag to move camera pivot"
                  , "%s: Toggle Editor On/off" % EDITOR_DGUI_TOGGLE_BUTTON.upper()
                  , "F5: save scene      F9: load scene" ]
      for i in xrange( len(helpTexts) ):
        self.helpText.append( addInstructions(1.0-0.05*(i+1), helpTexts[i]) )
      for text in self.helpText:
        text.show()
      
      cameraController.enable()
      
      messenger.send(EDITOR_TOGGLE_ON_EVENT)
      
      self.editorObject = None
      self.accept(EVENT_MODELCONTROLLER_SELECT_MODEL, self.createObjectEditor)
      
      self.accept('f5', self.saveEggModelsFile)
      self.accept('f9', self.loadEggModelsFile)
      self.accept('f11', self.toggle)
    
    self.accept(EDITOR_DGUI_TOGGLE_BUTTON, self.toggle)
  
  def saveEggModelsFile(self):
    print "I: EditorApp.saveEggModelsFile:"
    FG.openFileBrowser()
    FG.accept('selectionMade', self.saveEggModelsFileCallback)
  def saveEggModelsFileCallback(self, filename):
    print "I: EditorApp.saveEggModelsFileCallback:", filename
    self.editorInstance.saveEggModelsFile(filename)
  
  def loadEggModelsFile(self):
    print "I: EditorApp.loadEggModelsFile:"
    FG.openFileBrowser()
    FG.accept('selectionMade', self.loadEggModelsFileCallback)
  def loadEggModelsFileCallback(self, filename):
    print "I: EditorApp.loadEggModelsFileCallback:", filename
    self.editorInstance.loadEggModelsFile(filename)
  
  def createObjectEditor(self, object):
    print "I: EditorApp.createObjectEditor:", object.__class__.__name__
    if object == self.editorObject:
      # same object is selected again
      print "  - same object"
    else:
      print "  - other object"
      if self.editorObject is not None:
        # destroy the current editorObject
        print "  - is destroying old editor"
      print "  - creating new editor"
  
  def crateFilebrowserModelWrapper(self, type):
    exec("from core.modules.p%s import %s" % (type, type))
    modelParent = modelController.getSelectedModel()
    FG.openFileBrowser()
    exec("FG.accept('selectionMade', %s.onCreateInstance, [modelParent])" % (type))
  
  def createModelWrapper(self, type):
    exec("from core.modules.p%s import %s" % (type, type))
    modelParent = modelController.getSelectedModel()
    exec("%s.onCreateInstance( modelParent )" % type)
  
  def disable( self ):
    if self.enabled:
      self.ignoreAll()
      
      # hide the text
      for text in self.helpText:
        text.detachNode()
      
      self.scenegraphBrowserWindow.detachNode()
      
      self.ButtonsWindow.detachNode()
      
      messenger.send( EDITOR_TOGGLE_OFF_EVENT )
      
      cameraController.disable()
      
      self.accept( EDITOR_DGUI_TOGGLE_BUTTON, self.toggle )

  def createInterface( self, buttonDefinitions ):
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
    
    height = itemHeight * len(buttonDefinitions)
    self.ButtonsWindow = DirectWindow( title='ButtonsWindow', pos = ( 0.83, 1.0 )
                                                , virtualSize = ( 0.5, height )
                                     )
    myScrolledList = DirectScrolledList(
        #frameSize = (-1, 1, -1, 0),
        #frameColor = (1,0,0,0.5),
        pos = (0.25, 0, -.1 ),
        items = buttons,
        scale = 0.5,
        parent = self.ButtonsWindow,
        numItemsVisible = len(buttons),
        forceHeight = itemHeight,
        #itemFrame_frameSize = (-0.2, 0.2, -0.37, 0.11),
        #itemFrame_pos = (0.35, 0, 0.4),
        incButton_scale = (0, 0, 0),
        decButton_scale = (0, 0, 0),
        )
  
