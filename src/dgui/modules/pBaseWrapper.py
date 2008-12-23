import traceback

from pandac.PandaModules import *
from direct.gui.DirectGui import *
from direct.gui.DirectCheckBox import DirectCheckBox
from direct.showbase.DirectObject import DirectObject

from dgui.directWindow.src.directWindow import DirectWindow
from dgui.directSidebar import *
from core.pModelIdManager import modelIdManager
from core.pConfigDefs import *
from core.modules.pBaseWrapper import Enum, TransparencyEnum, AntialiasEnum

def strListToFloat(l):
  o = list()
  for i in l:
    o.append(float(i))
  return o

def str2type(string, valueType):
  value = None
  try:
    if valueType in [str, int, float]:
      value = valueType(string)
    elif valueType in [Vec4, Point4, Vec3, Point3, Vec2, Point2, tuple, list]:
      strippedString = string.lstrip('(').rstrip(')')
      splitStrValues = strippedString.split(',')
      splitValues = strListToFloat(splitStrValues)
      if valueType in [tuple, list]:
        value = valueType(splitValues)
      else:
        value = valueType(*splitValues)
    else:
      print "E: str2type: unknown type", valueType, string
  except:
    print "E: str2type: conversion error", valueType, string
    traceback.print_exc()
  return value



class BaseWrapper(DirectObject):
  def __init__(self, object, editorInstance):
    self.object = object
    self.mutableParameters = self.object.mutableParameters
    self.mutableParametersSorting = [
      'name',
      'position',
      'rotation',
      'scale',
      'color',
      'colorScale',
      'transparency',
      'antialias',
    ]
    
    self.buttonsWindow = None
    self.editorInstance = editorInstance
  
  def startEdit(self):
    # the object is selected to be edited
    # creates a directFrame to edit this object
    self.createEditWindow()
    # it's getting slow with this
    #self.accept(EVENT_MODELCONTROLLER_FAST_REFRESH, self.updateAllEntires)
    self.accept(EVENT_MODELCONTROLLER_FULL_REFRESH, self.updateAllEntires)
  
  def stopEdit(self):
    # the object is deselected from being edited
    self.destroyEditWindow()
    self.ignore(EVENT_MODELCONTROLLER_FULL_REFRESH)
    self.ignore(EVENT_MODELCONTROLLER_FAST_REFRESH)
    self.ignoreAll()
  
  def createEditWindow(self):
    if self.buttonsWindow is None:
      ySize = len(self.mutableParameters)
      title='editWindow-%s' % str(self.object.getName())
      self.buttonsWindow = DirectSidebar(
        frameSize=(1.1,ySize*.11)
      , align=ALIGN_RIGHT|ALIGN_BOTTOM, opendir=LEFT_OR_UP, orientation=VERTICAL
      , text=title
      , toggleFunc=self.editorInstance.setObjectEditwindowToggled)
      self.parameterEntries = dict()
      
      self.buttonsWindow.toggleCollapsed(self.editorInstance.getObjectEditwindowToggled())
      
      dy = ySize*.11
      for paramName in self.mutableParameters.keys():
        if paramName in self.mutableParametersSorting:
          y = self.mutableParametersSorting.index(paramName)
          #print "creating entry", paramName
          paramLabel = DirectLabel( text = paramName
                                  , parent = self.buttonsWindow
                                  , scale=.05
                                  , pos = (0.42, 0, dy-0.1 - y*0.1)
                                  , text_align = TextNode.ARight )
          # only if the parameter is in mutableparameters allow to change it
          # for example ambientlight does not have specularColor (but it is defined in the sorting)
          
          paramType, getFunc, setFunc, hasFunc, clearFunc = self.mutableParameters[paramName]
          if paramType  in [str, float, int, Vec4, Vec3, Vec2, Point4, Point3, Point2]:
            paramEntry = DirectEntry(
                #text = "",
                scale=.05,
                pos = (0.47, 0, dy-0.1 - y*0.1),
                parent = self.buttonsWindow,
                command=self.setEntryCommand,
                extraArgs=[paramName],
                initialText="",
                numLines = 1,
                focus=0,
                width=12,
                focusOutCommand=self.setEntryFocusOut,
                focusOutExtraArgs=[paramName],
                text_align = TextNode.ALeft,)
          elif paramType == bool:
            paramEntry = DirectCheckButton(
                scale=.05,
                pos = (0.52, 0, dy-0.08 - y*0.1),
                parent = self.buttonsWindow,
                command=self.setEntryCommand,
                extraArgs=[paramName],)
          elif paramType.__name__ == "Enum":
            items = paramType.keys()
            # select the default item 0
            for k, v in paramType.items():
              if v == 0:
                i = k
            initialitem = items.index(i)
            paramEntry = DirectOptionMenu(
                pos = (0.52, 0, dy-0.08 - y*0.1),
                scale=.05,
                parent = self.buttonsWindow,
                command=self.setEntryCommand,
                extraArgs=[paramName],
                items=items,
                initialitem=initialitem,
                highlightColor=(0.65,0.65,0.65,1),)
          else:
            print "W: dgui.BaseWrapper.createEditWindow: unknown entry type"
            print "  -", self.object.__class__.__name__
            print "  -", paramType.__name__
            print "  -", paramType, paramName
            #print "  -", getFunc, setFunc, hasFunc, clearFunc
            print Enum
            paramEntry = None
        else:
          print "W: dgui.BaseWrapper.createEditWindow: no mutableparameter for entry"
          print "  -", self.object.__class__.__name__
          print "  -", paramType, paramName
          print "  - in", self.mutableParametersSorting
        self.parameterEntries[paramName] = paramEntry
      self.updateAllEntires()
  
  def destroyEditWindow(self):
    if self.buttonsWindow:
      for paramName, paramEntry in self.parameterEntries.items():
        if paramName in self.mutableParameters:
          paramType, getFunc, setFunc, hasFunc, clearFunc = self.mutableParameters[paramName]
          if paramType == 'str' or paramType == 'float' or paramType == 'int':
            if paramEntry:
              paramEntry.removeNode()
              paramEntry.detachNode()
      self.buttonsWindow.detachNode()
      self.buttonsWindow.removeNode()
      self.buttonsWindow.destroy()
      del self.buttonsWindow
    
    self.buttonsWindow = None
  
  def setEntry(self, paramName, paramValue):
    if self.buttonsWindow:
      if self.parameterEntries.has_key(paramName):
        paramType, getFunc, setFunc, hasFunc, clearFunc = self.mutableParameters[paramName]
        #self.object.setParameters( {paramName: paramValue} )
        try:
          if paramType in [str, float, int]:
            paramValue = paramType(paramValue)
          elif paramType.__name__ == "Enum":
            pass # doesnt need conversion
          elif paramType in [Vec4, Vec3, Vec2, Point4, Point3, Point2]:
            paramValue = str2type(paramValue, tuple)
          elif paramType == bool:
            pass
        except ValueError:
          print "E: dgui.BaseWrapper.setEntry: error"
          traceback.print_exc()
        self.object.setParameters( {paramName: paramValue} )
      else:
        print "E: dgui.BaseWrapper.setEntry: unknown key", paramName
        print "  -", self.parameterEntries
      self.updateAllEntires()
  
  def setEntryFocusOut(self, paramName):
    paramValue = self.parameterEntries[paramName].get()
    self.setEntry(paramName, paramValue)
  
  def setEntryCommand(self, paramValue, paramName):
    self.setEntry(paramName, paramValue)
  
  def updateAllEntires(self):
    if self.buttonsWindow:
      for paramName, [paramType, getFunc, setFunc, hasFunc, clearFunc] in self.mutableParameters.items():
        objectParameters = self.object.getParameters()
        if paramName in objectParameters:
          if self.parameterEntries[paramName]:
            currentValue = objectParameters[paramName]
            if paramType == bool:
              self.parameterEntries[paramName]["indicatorValue"] = currentValue
              self.parameterEntries[paramName].setIndicatorValue()
            elif paramType.__name__ == "Enum":
              if self.parameterEntries[paramName].get() != currentValue:
                for n, v in paramType.items():
                  if n == currentValue:
                    # get the index of the currently saved value
                    i = self.parameterEntries[paramName].index(n)
                    self.parameterEntries[paramName].set(i)
              else:
                #print "updateAllEntries: enum: value already selected"
                pass
            else:
              if paramType in [str]:
                valueString = currentValue
                self.parameterEntries[paramName].enterText(valueString)
              elif paramType in [Vec4, Point4, VBase4, Vec3, Point3, VBase3, Vec2, Point2, VBase2, tuple, list]:
                valueString = ""
                for val in currentValue:
                  valueString += "%.3G, " % val
                valueString = valueString[:-2]
                self.parameterEntries[paramName].enterText(valueString)
              elif paramType in [float, int]:
                valueString = "%.3G" % currentValue
                self.parameterEntries[paramName].enterText(valueString)
              else:
                #print "I: dgui.BaseWrapper.updateAllEntires: undefined value for", paramName, currentValue, paramType
                pass
          else:
            print "W: dgui.BaseWrapper.updateAllEntires: no parameterEntry for", paramName, self.object.__class__.__name__
        else:
          print "W: dgui.BaseWrapper.updateAllEntires: undefined value for", paramName
      # when the name changed, update the scenegraph
      if paramName == 'name':
        messenger.send(EVENT_SCENEGRAPHBROWSER_REFRESH)



