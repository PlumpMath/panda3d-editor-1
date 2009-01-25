#!/usr/bin/env python
from direct.showbase.DirectObject import DirectObject
from direct.fsm.FSM import FSM
from pandac.PandaModules import *

# doesnt work, because the editor may be started before panda
#from core.modules import *
from core.pConfigDefs import *
from core.pModelController import modelController

from dgui.directSidebar import *
from dgui.pCameraController import cameraController
from dgui.pScenegraphBrowser import SceneGraphBrowser
from dgui.pTexturePainterGui import TexturePainterGui
from dgui.pMenuBarGui import MenuBarGui
from dgui.pConfigDefs import *

DGUI_SCENEGRAPHBROWSER_ACTIVE = True
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
    self.editorInstance = editorInstance
    self.objectEditorVisible = False
    self.lastSelectedModel = None
    
    self.texturePainterGui = TexturePainterGui(self)
    self.menuBarGui = MenuBarGui(self)
  
  def __del__(self):
    print "I: EditorApp.__del__: whoooot it works !!!!!!!!!!!!!!!!!!!!!!!!!!!"
  
  def enable(self):
    cameraController.enable()
    self.menuBarGui.enable()
    
    if DGUI_SCENEGRAPHBROWSER_ACTIVE:
      self.scenegraphBrowserWindow = DirectSidebar(
          frameSize=(1., 1.5),
          pos=Vec3(0,0,0.05),
          align=ALIGN_LEFT|ALIGN_BOTTOM,
          orientation=VERTICAL,
          text='scenegraph',
          frameColor=(0,0,0,.8),
      )
      # create SceneGraphBrowser and point it on aspect2d
      self.scenegraphBrowser = SceneGraphBrowser(
          parent=self.scenegraphBrowserWindow, # where to attach SceneGraphBrowser frame
          treeWrapperRoot=self.editorInstance.treeParent, # display children under this root node
          includeTag=ENABLE_SCENEGRAPHBROWSER_MODEL_TAG,
          button1func=modelController.selectObject,
          pos=(0,0,0),
          frameSize=(1,1.5)
        )
      self.scenegraphBrowser.accept(EVENT_SCENEGRAPH_REFRESH,self.scenegraphBrowser.update)
      self.accept( 'r', messenger.send, [EVENT_SCENEGRAPH_REFRESH] )
    
    # some help text nodes
    self.helpText = list()
    #self.helpText.append( addTitle("Panda3D: Simple scene editor") )
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
    
    self.accept(EVENT_MODELCONTROLLER_SELECTED_OBJECT_CHANGE, self.modelSelected)
    
    self.editorInstance.toggleEditmode(True)
  
  def disable(self, state=None):
    '''if state is None:
      if self.editorInstance.state == 'DisabledMode' or self.editorInstance.state == 'PlayMode':
        state = 'WorldEditMode'
      else:
        state = 'PlayMode'
    print "I: dgui.EditorApp.disable: toggling to", state'''
    
    #self.editorInstance.toggle(state)
    #self.request(self.editorInstance.state)
    
    self.editorInstance.toggleEditmode(False)
  
  def destroy(self):
    self.disable()
    
    # hide the text
    for text in self.helpText:
      text.detachNode()
    
    self.menuBarGui.disable()
    
    if DGUI_SCENEGRAPHBROWSER_ACTIVE:
      self.scenegraphBrowserWindow.destroy()
      self.scenegraphBrowserWindow.detachNode()
    
    #self.modelSelected(None)
    if self.editorObjectGuiInstance is not None:
      self.editorObjectGuiInstance.stopEdit()
    
    messenger.send( EDITOR_MODE_DISABLED )
    
    cameraController.disable()
  
  def setObjectEditwindowToggled(self, state):
    ''' saves the state of the object related window, so you dont have to
    close/open it every time, (it stays closed if it was before)'''
    self.objectEditorVisible = state
  def getObjectEditwindowToggled(self):
    return self.objectEditorVisible
  
  def modelSelected(self, model):
    ''' is called when a object is selected
    creates a corresponding editing sidebar for the object
    '''
    if self.lastSelectedObject != modelController.getSelectedObject():
      # selected model has been changed
      if self.editorObjectGuiInstance is not None:
        # destroy gui instance of old object
        self.editorObjectGuiInstance.stopEdit()
      
      # save the object as the new object
      self.lastSelectedObject = modelController.getSelectedObject()
      
      if modelController.getSelectedObject() is not None:
        # update menubar for object
        self.menuBarGui.update()
        
        # create gui instance of new object
        objType = modelController.getSelectedObject().__class__
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
          self.editorObjectGuiInstance = getattr(module, objType)(modelController.getSelectedObject(), self)
          self.editorObjectGuiInstance.startEdit()
        except TypeError:
          print "E: dgui.EditorApp.modelSelected: object", objType, modelController.getSelectedObject()
          traceback.print_exc()
      else:
        self.editorObjectGuiInstance = None
    else:
      # the same object is selected again
      pass
  
