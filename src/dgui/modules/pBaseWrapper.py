from pandac.PandaModules import *
from direct.gui.DirectGui import *
from direct.gui.DirectCheckBox import DirectCheckBox
import traceback

from core.pModelIdManager import modelIdManager
from core.pConfigDefs import *
from dgui.directWindow.src.directWindow import DirectWindow
from direct.showbase.DirectObject import DirectObject

class BaseWrapper(DirectObject):
  def __init__( self, object ):
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
      , 'colorScale': ['vec4', 'getColorScale', 'getColorScale', 'hasColorScale']
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
      ySize = len(self.mutableParametersSorting)
      #print "ySize", ySize
      self.buttonsWindow = DirectWindow( title='editWindow-%s' % str(self.object.getName())
                                       , pos = ( .23, -1+(ySize+1)*.11 )
                                       , virtualSize = (1.0,ySize*.11) )
      self.parameterEntries = dict()
      
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
                                    , pos = (.05+0.35*(x), 0, -0.1 - y*0.1)
                                    , text_align = TextNode.ARight )
            if paramType == 'str' or paramType == 'float' or paramType == 'int' or paramType == 'vec4':
              paramEntry = DirectEntry( text = ""
                                      , scale=.05
                                      , pos = (.10+0.35*(x), 0, -0.1 - y*0.1)
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
                                      , pos = (0.25, 0, -0.1 - y*0.1)
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
                                  , pos = (0.20, 0, -0.1 - y*0.1)
                                  , text_align = TextNode.ARight )
          if paramType == 'str' or paramType == 'float' or paramType == 'int' or paramType == 'vec4':
            paramEntry = DirectEntry( text = ""
                                    , scale=.05
                                    , pos = (0.25, 0, -0.1 - y*0.1)
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
                                    , pos = (0.25, 0, -0.1 - y*0.1)
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
      self.buttonsWindow.removeNode()
      self.buttonsWindow.detachNode()
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
          floatVal = float(paramValue)
          execCmd = 'self.object.%s( str("%.3f") )' % (setter, floatVal)
          exec( execCmd )
        elif paramType == 'str':
          execCmd = 'self.object.%s( str("%s") )' % (setter, paramValue)
          exec( execCmd )
        elif paramType == 'int':
          execCmd = 'self.object.%s( %i )' % (setter, paramValue)
          exec( execCmd )
        elif paramType == 'vec4':
          execCmd = 'self.object.%s( Vec4(*%s) )' % (setter, str(paramValue))
          exec( execCmd )
        elif paramType == 'bool':
          execCmd = 'self.object.%s( %i )' % (setter, paramValue)
          exec( execCmd )
        else:
          print "W: BaseWrapper.setEntry: unknown type", paramType
        self.updateAllEntires()
      else:
        print "E: BaseWrapper.setEntry: unknown key", paramName
        print "  -", self.parameterEntries
  
  def updateAllEntires(self):
    if self.buttonsWindow:
      for paramName, [paramType, getter, setter, enabled] in self.mutableParameters.items():
        if paramType == 'float':
          execCmd = 'currentValue = self.object.%s()' % getter
          exec( execCmd )
          currentValue = '%.3f' % currentValue
          self.parameterEntries[paramName].enterText(str(currentValue))
        elif paramType == 'str' or paramType == 'int':
          execCmd = 'currentValue = self.object.%s()' % getter
          exec( execCmd )
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
        
        #if paramName is not None:
        #  if self.parameterEntries[paramName] is not None:
        #    self.parameterEntries[paramName].enterText(str(currentValue))
      
      # when the name changed, update the scenegraph
      if paramName == 'nodeName':
        messenger.send(EVENT_SCENEGRAPHBROWSER_REFRESH)


