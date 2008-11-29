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
        'posXa': ['float', 'getX', 'setX']
      , 'posYa': ['float', 'getY', 'setY']
      , 'posZa': ['float', 'getZ', 'setZ']
      , 'pos' : { 'posX': ['float', 'getX', 'setX']
                , 'posY': ['float', 'getY', 'setY']
                , 'posZ': ['float', 'getZ', 'setZ'] }
      , 'H': ['float', 'getH', 'setH']
      , 'P': ['float', 'getP', 'setP']
      , 'R': ['float', 'getR', 'setR']
      , 'scaleX': ['float', 'getSx', 'setSx']
      , 'scaleY': ['float', 'getSy', 'setSy']
      , 'scaleZ': ['float', 'getSz', 'setSz']
      , 'transparency': ['bool', 'getTransparency', 'setTransparency' ]
      , 'nodeName': ['str', 'getName', 'setName' ]
    }
    self.mutableParametersSorting = [
      'posX', 'posY', 'posZ'
    , 'H', 'P', 'R'
    , 'scaleX', 'scaleY', 'scaleZ'
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
      self.buttonsWindow = DirectWindow( title='%s-editWindow' % self.getName()
                                        , pos = ( .63, 0 )
                                        , virtualSize = (0.8,ySize*.11)
#                                        , maxSize = ( .8, 1 )
#                                        , minSize = ( .8, 1 )
                                       )
      self.parameterEntries = dict()
      for i in xrange(ySize):
        yParamName = self.mutableParametersSorting[i]
        if type(self.mutableParameters[paramName]) == dict:
          # it's a horizontal list of parameters
          xSize = len(self.mutableParameters[paramName])
          xParamName = self.mutableParametersSorting[i]
          
          for j in xrange(xSize):
            paramType, getter, setter = self.mutableParameters[paramName]
            if paramType == 'str' or paramType == 'float' or paramType == 'int':
              paramLabel = DirectLabel( text = paramName
                                      , parent = self.buttonsWindow
                                      , scale=.05
                                      , pos = (0.20, 0, -0.1 - i*0.1)
                                      , text_align = TextNode.ARight )
              paramEntry = DirectEntry( text = ""
                                      , scale=.05
                                      , pos = (0.25, 0, -0.1 - i*0.1)
                                      , parent = self.buttonsWindow
                                      , initialText=""
                                      , numLines = 1
                                      , focus=0
                                      , focusOutCommand=self.setEntry
                                      , focusOutExtraArgs=[paramName]
                                      , command=self.setEntry
                                      , extraArgs=[paramName]
                                      , text_align = TextNode.ALeft)
            else:
              paramEntry = None
            self.parameterEntries[paramName] = paramEntry
        else:
          paramType, getter, setter = self.mutableParameters[yParamName]
          if paramType == 'str' or paramType == 'float' or paramType == 'int':
            paramLabel = DirectLabel( text = paramName
                                    , parent = self.buttonsWindow
                                    , scale=.05
                                    , pos = (0.20, 0, -0.1 - i*0.1)
                                    , text_align = TextNode.ARight )
            paramEntry = DirectEntry( text = ""
                                    , scale=.05
                                    , pos = (0.25, 0, -0.1 - i*0.1)
                                    , parent = self.buttonsWindow
                                    , initialText=""
                                    , numLines = 1
                                    , focus=0
                                    , focusOutCommand=self.setEntry
                                    , focusOutExtraArgs=[paramName]
                                    , command=self.setEntry
                                    , extraArgs=[paramName]
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
        execCmd = 'setValue = str("%.3f")' % floatVal
        #execCmd = 'setValue = "%s" % (%s(%s))' % (paramType, paramValue)
      elif paramType == 'str':
        execCmd = 'setValue = %s' % paramValue
      elif paramType == 'int':
        execCmd = 'setValue = str(%s(%s))' % (paramType, paramValue)
      exec( execCmd )
      execCmd = 'self.object.%s( %s )' % (setter, setValue)
      exec( execCmd )
      
      #print "done"
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


