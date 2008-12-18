from pandac.PandaModules import *
from direct.gui.DirectGui import *
from direct.gui.DirectCheckBox import DirectCheckBox
import traceback

from core.pModelIdManager import modelIdManager
from core.pConfigDefs import *
from dgui.directWindow.src.directWindow import DirectWindow
from direct.showbase.DirectObject import DirectObject
from dgui.directSidebar import *

class BaseWrapper(DirectObject):
  def __init__(self, object, editorInstance):
    print "I: BaseWrapper.__init__:", object
    self.object = object
    self.mutableParameters = {
        'pX': ['float', 'getX', 'setX', None]
      , 'pY': ['float', 'getY', 'setY', None]
      , 'pZ': ['float', 'getZ', 'setZ', None]
      , 'H': ['float', 'getH', 'setH', None]
      , 'P': ['float', 'getP', 'setP', None]
      , 'R': ['float', 'getR', 'setR', None]
      , 'sX': ['float', 'getSx', 'setSx', None]
      , 'sY': ['float', 'getSy', 'setSy', None]
      , 'sZ': ['float', 'getSz', 'setSz', None]
      , 'color': ['vec4', 'getColor', 'setColor', 'hasColor']
      , 'colorScale': ['vec4', 'getColorScale', 'setColorScale', 'hasColorScale']
      , 'transparency': ['bool', 'getTransparency', 'setTransparency', 'hasTransparency' ]
      , 'nodeName': ['str', 'getName', 'setName', None ]
    }
    self.mutableParametersSorting = [
      [ 'pX', 'pY', 'pZ' ]
    , [ 'H', 'P', 'R' ]
    , [ 'sX', 'sY', 'sZ' ]
    , 'color'
    , 'colorScale'
    , 'transparency'
    , 'nodeName'
    ]
    self.buttonsWindow = None
    self.editorInstance = editorInstance
  
  def startEdit(self):
    print "I: dgui.BaseWrapper.startEdit"
    # the object is selected to be edited
    # creates a directFrame to edit this object
    self.createEditWindow()
    # it's getting slow with this
    #self.accept(EVENT_MODELCONTROLLER_FAST_REFRESH, self.updateAllEntires)
    self.accept(EVENT_MODELCONTROLLER_FULL_REFRESH, self.updateAllEntires)
  def stopEdit(self):
    print "I: dgui.BaseWrapper.stopEdit"
    # the object is deselected from being edited
    self.destroyEditWindow()
    self.ignore(EVENT_MODELCONTROLLER_FULL_REFRESH)
    self.ignore(EVENT_MODELCONTROLLER_FAST_REFRESH)
    self.ignoreAll()
  
  def createEditWindow(self):
    #print "I: baseWrapper.createEditWindow"
    if self.buttonsWindow is None:
      #sideFrame = DirectSidebar(frameSize=(0.8,0.4), pos=(-.05,0,0.1), align=ALIGN_RIGHT|ALIGN_BOTTOM, opendir=LEFT_OR_UP, orientation=VERTICAL, text='right-bottom')
      ySize = len(self.mutableParametersSorting)
      #print "ySize", ySize
      title='editWindow-%s' % str(self.object.getName())
      self.buttonsWindow = DirectSidebar(
        frameSize=(1.1,ySize*.11)
      , align=ALIGN_RIGHT|ALIGN_BOTTOM, opendir=LEFT_OR_UP, orientation=VERTICAL
      , text=title
      , toggleFunc=self.editorInstance.setObjectEditwindowToggled)
      self.parameterEntries = dict()
      
      self.buttonsWindow.toggleCollapsed(self.editorInstance.getObjectEditwindowToggled())
      
      dy = ySize*.11# + 0.75
      print "ySize", ySize
      for y in xrange(ySize):
        yParamName = self.mutableParametersSorting[y]
        #paramType, getter, setter = self.mutableParameters[yParamName]
        if type(self.mutableParametersSorting[y]) == list:
          # it's a horizontal list of parameters
          xSize = len(self.mutableParametersSorting[y])
          
          for x in xrange(xSize):
            xParamName = self.mutableParametersSorting[y][x]
            paramType, getter, setter, enabled = self.mutableParameters[xParamName]
            paramLabel = DirectLabel( text = xParamName
                                    , parent = self.buttonsWindow
                                    , scale=.05
                                    , pos = (.12+0.35*(x), 0, dy-0.1 - y*0.1)
                                    , text_align = TextNode.ARight )
            if paramType == 'str' or \
                paramType == 'float' or \
                paramType == 'int' or \
                paramType == 'vec4' or \
                paramType == 'vec2' or \
                paramType == 'vec3' or \
                paramType == 'point3':
              paramEntry = DirectEntry( text = ""
                                      , scale=.05
                                      , pos = (.17+0.35*(x), 0, dy-0.1 - y*0.1)
                                      , parent = self.buttonsWindow
                                      , initialText=""
                                      , numLines = 1
                                      , focus=0
                                      , width=4
                                      , focusOutCommand=self.setEntry
                                      , focusOutExtraArgs=[xParamName]
                                      , command=self.setEntry
                                      , extraArgs=[xParamName]
                                      , text_align = TextNode.ALeft)
            elif paramType == 'bool':
              paramEntry = DirectCheckButton( scale=.05
                                      , pos = (0.32, 0, dy-0.1 - y*0.1)
                                      , parent = self.buttonsWindow
                                      , focus=0
                                      , width=10
                                      , commandFunc=self.setEntry
                                      , extraArgs=[yParamName])
            else:
              print "W: BaseWrapper.createEditWindow: unknown entry type"
              print "  -", xParamName
              print "  -", paramType, getter, setter, enabled
              paramEntry = None
            self.parameterEntries[xParamName] = paramEntry
        else:
          paramType, getter, setter, enabled = self.mutableParameters[yParamName]
          paramLabel = DirectLabel( text = yParamName
                                  , parent = self.buttonsWindow
                                  , scale=.05
                                  , pos = (0.42, 0, dy-0.1 - y*0.1)
                                  , text_align = TextNode.ARight )
          if paramType == 'str' or \
              paramType == 'float' or \
              paramType == 'int' or \
              paramType == 'vec4' or \
              paramType == 'vec2' or \
              paramType == 'vec3' or \
              paramType == 'point3':
            paramEntry = DirectEntry( text = ""
                                    , scale=.05
                                    , pos = (0.47, 0, dy-0.1 - y*0.1)
                                    , parent = self.buttonsWindow
                                    , initialText=""
                                    , numLines = 1
                                    , focus=0
                                    , width=10
                                    , focusOutCommand=self.setEntry
                                    , focusOutExtraArgs=[yParamName]
                                    , command=self.setEntry
                                    , extraArgs=[yParamName]
                                    , text_align = TextNode.ALeft)
          elif paramType == 'bool':
            paramEntry = DirectCheckButton( scale=.05
                                    , pos = (0.52, 0, dy-0.08 - y*0.1)
                                    , parent = self.buttonsWindow
#                                    , focus=0
#                                    , width=10
                                    , command=self.setEntry
                                    , extraArgs=[yParamName])
          else:
            print "W: BaseWrapper.createEditWindow: unknown entry type"
            print "  -", yParamName
            print "  -", paramType, getter, setter, enabled
            paramEntry = None
          self.parameterEntries[yParamName] = paramEntry
      self.updateAllEntires()
  
  def destroyEditWindow(self):
    print "I: baseWrapper.destroyEditWindow"
    if self.buttonsWindow:
      for paramName, paramEntry in self.parameterEntries.items():
        paramType, getter, setter, enabled = self.mutableParameters[paramName]
        if paramType == 'str' or paramType == 'float' or paramType == 'int':
          paramEntry.removeNode()
          paramEntry.detachNode()
      self.buttonsWindow.detachNode()
      self.buttonsWindow.removeNode()
      self.buttonsWindow.destroy()
      del self.buttonsWindow

    self.buttonsWindow = None
  
  def setEntry(self, *parameters):
    if self.buttonsWindow:
      if len(parameters) == 2:
        paramValue, paramName=parameters
      elif len(parameters) == 1:
        paramName = parameters[0]
        paramValue = self.parameterEntries[paramName].get()
      else:
        return
      if self.parameterEntries.has_key(paramName):
        paramEntry = self.parameterEntries[paramName]
        paramType, getter, setter, enabled = self.mutableParameters[paramName]
        if paramType == 'float':
          try:
            floatVal = float(paramValue)
          except ValueError:
            floatVal = 0.0
          execCmd = 'self.object.%s( %.3f )' % (setter, floatVal)
          try:
            exec( execCmd )
          except:
            print "W: dgui.BaseWrapper.setEntry: command failed"
            print "  -", execCmd
            traceback.print_exc()
        elif paramType == 'str':
          execCmd = 'self.object.%s( str("%s") )' % (setter, paramValue)
          try:
            exec( execCmd )
          except:
            print "W: dgui.BaseWrapper.setEntry: command failed"
            print "  -", execCmd
        elif paramType == 'int':
          execCmd = 'self.object.%s( %i )' % (setter, int(paramValue))
          try:
            exec( execCmd )
          except:
            print "W: dgui.BaseWrapper.setEntry: command failed"
            print "  -", execCmd
            traceback.print_exc()
        elif paramType == 'vec2':
          execCmd = 'self.object.%s( Vec2(*%s) )' % (setter, str(paramValue))
          try:
            exec( execCmd )
          except:
            print "W: dgui.BaseWrapper.setEntry: command failed"
            print "  -", execCmd
            traceback.print_exc()
        elif paramType == 'point3':
          execCmd = 'self.object.%s( Point3(*%s) )' % (setter, str(paramValue))
          try:
            exec( execCmd )
          except:
            print "W: dgui.BaseWrapper.setEntry: command failed"
            print "  -", execCmd
            traceback.print_exc()
        elif paramType == 'vec3':
          execCmd = 'self.object.%s( Vec3(*%s) )' % (setter, str(paramValue))
          try:
            exec( execCmd )
          except:
            print "W: dgui.BaseWrapper.setEntry: command failed"
            print "  -", execCmd
            traceback.print_exc()
        elif paramType == 'vec4':
          execCmd = 'self.object.%s( Vec4(*%s) )' % (setter, str(paramValue))
          try:
            exec( execCmd )
          except:
            print "W: dgui.BaseWrapper.setEntry: command failed"
            print "  -", execCmd
            traceback.print_exc()
        elif paramType == 'bool':
          execCmd = 'self.object.%s( %i )' % (setter, paramValue)
          try:
            exec( execCmd )
          except:
            print "W: dgui.BaseWrapper.setEntry: command failed"
            print "  -", execCmd
            traceback.print_exc()
        else:
          print "W: BaseWrapper.setEntry: unknown type", paramType
        self.updateAllEntires()
      else:
        print "E: BaseWrapper.setEntry: unknown key", paramName
        print "  -", self.parameterEntries
  
  def updateAllEntires(self):
    if self.buttonsWindow:
      for paramName, [paramType, getter, setter, enabled] in self.mutableParameters.items():
        try:
          if paramType == 'float':
            execCmd = 'currentValue = self.object.%s()' % getter
            exec( execCmd )
            currentValue = '%.3f' % currentValue
            self.parameterEntries[paramName].enterText(str(currentValue))
          elif paramType == 'str' or paramType == 'int':
            execCmd = 'currentValue = self.object.%s()' % getter
            exec( execCmd )
            self.parameterEntries[paramName].enterText(str(currentValue))
          elif paramType == 'vec2':
            execCmd = 'v = self.object.%s()' % getter
            exec(execCmd)
            currentValue = "(%.2f, %.2f)" % (v.getX(), v.getY())
            self.parameterEntries[paramName].enterText(str(currentValue))
          elif paramType == 'point3' or paramType == 'vec3':
            execCmd = 'v = self.object.%s()' % getter
            exec(execCmd)
            currentValue = "(%.2f, %.2f, %.2f)" % (v.getX(), v.getY(), v.getZ())
            self.parameterEntries[paramName].enterText(str(currentValue))
          elif paramType == 'vec4':
            execCmd = 'v = self.object.%s()' % getter
            exec(execCmd)
            currentValue = "(%.2f, %.2f, %.2f, %.2f)" % (v.getX(), v.getY(), v.getZ(), v.getW())
            self.parameterEntries[paramName].enterText(str(currentValue))
          elif paramType == 'bool':
            execCmd = 'v = self.object.%s()' % getter
            exec(execCmd)
            self.parameterEntries[paramName]["indicatorValue"] = v
            self.parameterEntries[paramName].setIndicatorValue()
          else:
            print "W: BaseWrapper.updateAllEntires: unknown type", paramType
            #currentValue = ''
            #self.parameterEntries[paramName].enterText(str(currentValue))
        except:
          print "E: dgui.BaseWrapper.updateAllEntires: error in reading value"
          print "  -", paramName, paramType, getter, setter, enabled
          try:
            print "  -", currentValue
          except:
            pass
          traceback.print_exc()
        #if paramName is not None:
        #  if self.parameterEntries[paramName] is not None:
        #    self.parameterEntries[paramName].enterText(str(currentValue))
      
      # when the name changed, update the scenegraph
      if paramName == 'nodeName':
        messenger.send(EVENT_SCENEGRAPHBROWSER_REFRESH)


