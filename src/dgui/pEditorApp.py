#!/usr/bin/env python

from dgui.interactiveConsole.interactiveConsole import pandaConsole, INPUT_GUI, OUTPUT_PYTHON
from dgui.filebrowser import FG
from dgui.scenegraphBrowser import SceneGraphBrowser
from dgui.directWindow.src.directWindow import DirectWindow
from dgui.interactiveConsole.interactiveConsole import *

from core.pConfigDefs import *

EDITOR_DGUI_TOGGLE_BUTTON = 'f11'

class EditorApp:
  def __init__( self ):
    self.enabled = False
  
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
      
      self.scenegraphBrowserWindow = DirectWindow( title='window1', pos = ( -1.33, .55), maxSize     = ( 1, 1.5 ) )
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
      
      buttonDefinitions = [ ['model', self.createNodePathWrapper, []]
                          , ['particlesystem', self.createPartcileNodeWrapper, []]
                          , ['spotlight', self.createSpotlightNodeWrapper, []]
                          , ['destroy model', self.destroyModel, []]
                          , ['load', self.loadEggModelsFile, ['testModelsFile']]
                          , ['save', self.saveEggModelsFile, ['testModelsFile']]
                          ]
      self.createInterface(buttonDefinitions)
      
      # some help text nodes
      self.helpText = list()
      self.helpText.append( addTitle("Panda3D: Simple scene editor") )
      helpTexts = [ "LeftMouse: select object to move, select again to rotate, select again to scale"
                  , "MittleMouse: press & drag to rotate camera, turn to zoom (or page_up/down)"
                  , "RightMouse: press & drag to move camera pivot"
                  , "%s: Toggle Editor On/off" % EDITOR_TOGGLE_BUTTON.upper()
                  , "F5: save scene      F9: load scene" ]
      for i in xrange( len(helpTexts) ):
        self.helpText.append( addInstructions(1.0-0.05*(i+1), helpTexts[i]) )
      for text in self.helpText:
        text.show()
      
      self.enabled = True
      
      messenger.send( EDITOR_TOGGLE_ON_EVENT )
      
      self.accept( EDITOR_DGUI_TOGGLE_BUTTON, self.toggle )
  
  def disable( self ):
    if self.enabled:
      self.ignoreAll()
      
      # hide the text
      for text in self.helpText:
        text.detachNode()
      
      self.sceneHelperModels.detachNode()
      
      self.scenegraphBrowserWindow.detachNode()
      
      self.ButtonsWindow.detachNode()
      
      self.enabled = False
      
      messenger.send( EDITOR_TOGGLE_OFF_EVENT )
      
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
    
    self.ButtonsWindow = DirectWindow( title='ButtonsWindow', pos = ( 0.83, 1.0 )
                                                , maxSize = ( 0.5, 0.5 )
                                                , minSize = ( 0.5, 0.5 )
                                     )
                                      #, pos = ( 0, 0)
                                      #, maxSize = ( 0.5, 0.5 )
                                      #, minSize = ( 0.5, 0.5 ) )
    myScrolledList = DirectScrolledList(
        #frameSize = (-1, 1, -1, 0),
        #frameColor = (1,0,0,0.5),
        pos = (0.25, 0, .4),
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
  
