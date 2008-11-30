from pandac.PandaModules import *
from direct.gui.DirectGui import *

from core.pModelIdManager import modelIdManager
from core.pConfigDefs import *
from dgui.directWindow.src.directWindow import DirectWindow

class BaseWrapper( NodePath ):
  def __init__( self, object ):
    print "I: BaseWrapper.__init__:", object
    self.object = object
    self.mutableParameters = {
        'pX': ['float', 'getX', 'setX']
      , 'pY': ['float', 'getY', 'setY']
      , 'pZ': ['float', 'getZ', 'setZ']
      , 'H': ['float', 'getH', 'setH']
      , 'P': ['float', 'getP', 'setP']
      , 'R': ['float', 'getR', 'setR']
      , 'sX': ['float', 'getSx', 'setSx']
      , 'sY': ['float', 'getSy', 'setSy']
      , 'sZ': ['float', 'getSz', 'setSz']
      , 'transparency': ['bool', 'getTransparency', 'setTransparency' ]
      , 'nodeName': ['str', 'getName', 'setName' ]
    }
    self.mutableParametersSorting = [
      [ 'pX', 'pY', 'pZ' ]
    , [ 'H', 'P', 'R' ]
    , [ 'sX', 'sY', 'sZ' ]
    , 'transparency'
    , 'nodeName'
    ]
    self.buttonsWindow = None
  
  def startEdit( self ):
    # the object is selected to be edited
    # creates a directFrame to edit this object
    #self.createEditWindow()
    self.createEditWindow()
  def stopEdit( self ):
    # the object is deselected from being edited
    #self.destroyEditWindow()
    self.destroyEditWindow()
  
  def createEditWindow( self ):
    print "I: baseWrapper.createEditWindow"
    if self.buttonsWindow is None:
      ySize = len(self.mutableParametersSorting)
      print "ySize", ySize
      self.buttonsWindow = DirectWindow( title='editWindow' % self.getName()
                                        , pos = ( .23, -1+(ySize+1)*.11 )
                                        , virtualSize = (1.0,ySize*.11)
                                       )
      self.parameterEntries = dict()
      
      for y in xrange(ySize):
        yParamName = self.mutableParametersSorting[y]
        #paramType, getter, setter = self.mutableParameters[yParamName]
        if type(self.mutableParametersSorting[y]) == list:
          # it's a horizontal list of parameters
          xSize = len(self.mutableParametersSorting[y])
          
          for x in xrange(xSize):
            xParamName = self.mutableParametersSorting[y][x]
            paramType, getter, setter = self.mutableParameters[xParamName]
            if paramType == 'str' or paramType == 'float' or paramType == 'int':
              paramLabel = DirectLabel( text = xParamName
                                      , parent = self.buttonsWindow
                                      , scale=.05
                                      , pos = (.05+0.35*(x), 0, -0.1 - y*0.1)
                                      , text_align = TextNode.ARight )
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
            else:
              paramEntry = None
            self.parameterEntries[xParamName] = paramEntry
        else:
          paramType, getter, setter = self.mutableParameters[yParamName]
          if paramType == 'str' or paramType == 'float' or paramType == 'int':
            paramLabel = DirectLabel( text = yParamName
                                    , parent = self.buttonsWindow
                                    , scale=.05
                                    , pos = (0.20, 0, -0.1 - y*0.1)
                                    , text_align = TextNode.ARight )
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
          else:
            paramEntry = None
          self.parameterEntries[yParamName] = paramEntry
      self.updateAllEntires()
  
  def destroyEditWindow( self ):
    print "I: baseWrapper.destroyEditWindow"
    if self.buttonsWindow:
      for paramName, paramEntry in self.parameterEntries.items():
        paramType, getter, setter = self.mutableParameters[paramName]
        if paramType == 'str' or paramType == 'float' or paramType == 'int':
          paramEntry.removeNode()
          paramEntry.detachNode()
      self.buttonsWindow.removeNode()
      self.buttonsWindow.detachNode()
    self.buttonsWindow = None
  
  def setEntry( self, *parameters ):
    if self.buttonsWindow:
      if len(parameters) == 2:
        paramValue, paramName=parameters
      elif len(parameters) == 1:
        paramName = parameters[0]
        paramValue = self.parameterEntries[paramName].get()
      else:
        return
      paramEntry = self.parameterEntries[paramName]
      paramType, getter, setter = self.mutableParameters[paramName]
      if paramType == 'float':
        floatVal = float(paramValue)
        execCmd = 'self.object.%s( str("%.3f") )' % (setter, floatVal)
        exec( execCmd )
        #execCmd = 'setValue = "%s" % (%s(%s))' % (paramType, paramValue)
      elif paramType == 'str':
        execCmd = 'self.object.%s( str("%s") )' % (setter, paramValue)
        exec( execCmd )
      elif paramType == 'int':
        execCmd = 'self.object.%s( %i )' % (setter, paramValue)
        exec( execCmd )
      self.updateAllEntires()
  
  def updateAllEntires( self ):
    if self.buttonsWindow:
      for paramName, [paramType, getter, setter] in self.mutableParameters.items():
        if paramType == 'float':
          execCmd = 'currentValue = self.object.%s()' % getter
          exec( execCmd )
          currentValue = '%.3f' % currentValue
        elif paramType == 'str' or paramType == 'int':
          execCmd = 'currentValue = self.object.%s()' % getter
          exec( execCmd )
        else:
          currentValue = ''
        
        if paramName is not None:
          if self.parameterEntries[paramName] is not None:
            self.parameterEntries[paramName].enterText(str(currentValue))
      
      # maybe the name changed, we need to update the scenegraph in this case
      messenger.send(EVENT_SCENEGRAPHBROWSER_REFRESH)


