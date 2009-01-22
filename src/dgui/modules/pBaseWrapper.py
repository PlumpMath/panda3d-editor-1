import traceback, posixpath

from core.pCommonPath import relpath

from pandac.PandaModules import *
from direct.gui.DirectGui import *
from direct.gui.DirectCheckBox import DirectCheckBox
from direct.showbase.DirectObject import DirectObject

from dgui.filebrowser import FG

from dgui.directWindow.src.directWindow import DirectWindow
from dgui.directSidebar import *
from core.pModelIdManager import modelIdManager
from core.pConfigDefs import *
from core.modules.pBaseWrapper import TransparencyEnum, AntialiasEnum
from core.modules.pNodePathWrapper.pEggGroup import EggGroup_CollideFlags_Bitmask, \
EggGroup_CollisionSolidType_Enum, EggGroup_DCSType_Enum, \
EggGroup_BillboardType_Enum


DEBUG = False


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
    self.mutableParameters = None
    self.object = None
  
  def createEditWindow(self):
    if self.buttonsWindow is None:
      # add mutableParameters not in parameterSorting to the paraemters we show here
      mutableParameterSorting = self.mutableParametersSorting[:]
      for paramName in self.mutableParameters.keys():
        if paramName not in mutableParameterSorting:
          mutableParameterSorting.append(paramName)
      
      editWindowFrame = DirectFrame()
      self.parameterEntries = dict()
      yPos = -0.02
      xPos = 0.47
      for paramName in mutableParameterSorting:
        if paramName in self.mutableParameters.keys():
          # --- TITLE ---
          paramLabel = DirectLabel(
              text = paramName,
              parent = editWindowFrame,
              scale=.04,
              pos = (0.1, 0, yPos),
              text_align = TextNode.ALeft
          )
          #yPos -= 0.05
          
          # --- ELEMENTS ---
          paramType, getFunc, setFunc, hasFunc, clearFunc = self.mutableParameters[paramName]
          if paramType  in [str, float, int, Vec4, Vec3, Vec2, Point4, Point3, Point2]:
            paramEntry = DirectEntry(
                #text = "",
                scale=.04,
                pos = (xPos, 0, yPos),
                parent = editWindowFrame,
                command=self.setEntryCommand,
                extraArgs=[paramName],
                initialText="",
                numLines = 1,
                focus=0,
                width=12,
                focusOutCommand=self.setEntryFocusOut,
                focusOutExtraArgs=[paramName],
                text_align = TextNode.ALeft,
                frameSize=(-.3,12.3,-.3,0.9),
                #text_bg=(0,0,0,1),
                #text_fg=(.8,.8,.8,1),
                #fg=(0,0,0,0),
                #frameColor=(0,0,0,0) # this is the background
                )
            yPos -= 0.06
          elif paramType == bool:
            paramEntry = DirectCheckButton(
                scale=.04,
                pos = (xPos+0.05, 0, yPos),
                parent = editWindowFrame,
                command=self.setEntryCommand,
                extraArgs=[paramName],
                )
            yPos -= 0.06
          elif paramType.__name__ == "Enum":
            items = paramType.keys()
            # select the default item 0, this must be done because it
            # may be undefined, and thus updateAll will not set it
            for k, v in paramType.items():
              if v == 0:
                i = k
            initialitem = items.index(i)
            paramEntry = DirectOptionMenu(
                pos = (xPos, 0, yPos),
                scale=.04,
                parent = editWindowFrame,
                command=self.setEntryCommand,
                extraArgs=[paramName],
                items=items,
                initialitem=initialitem,
                highlightColor=(0.65,0.65,0.65,1),)
            yPos -= 0.06
          elif paramType.__name__ == "Bitmask":
            paramEntry = dict()
            i = 0
            for k, v in paramType.items():
              i += 1
              entry = DirectCheckButton(
                  #pos = (0.47, 0, yPos),
                  scale=.04,
                  parent = editWindowFrame,
                  text = k,
                  command=self.setEntryCommand,
                  extraArgs=[paramName, k],
                  )
              paramEntry[k] = entry
              entry.setPos((xPos+0.02 - entry.getBounds()[0] * .04, 0, yPos))
              yPos -= 0.06
            items = paramType.keys()
          elif paramType.__name__ == "Trigger":
            button = DirectButton(
                scale=.04,
                pos = (xPos+0.55, 0, yPos),
                parent = editWindowFrame,
                command=self.setEntry,
                extraArgs=[paramName],
                text=paramName,)
            yPos -= 0.06
          elif paramType.__name__ == "Filepath":
            paramEntry = DirectEntry(
                scale=.04,
                pos = (xPos, 0, yPos),
                parent = editWindowFrame,
                command=self.setEntryCommand,
                extraArgs=[paramName],
                initialText="",
                numLines = 1,
                focus=0,
                width=12,
                focusOutCommand=self.setEntryFocusOut,
                focusOutExtraArgs=[paramName],
                text_align = TextNode.ALeft,
                frameSize=(-.3,12.3,-.3,0.9),)
            
            def setPathCallback(entry, filepath):
              entry.set(filepath)
              # call the commandfunc, to store the value
              entry.commandFunc(None)
              # the path is modified internally, reloading the values fixes the entry
              self.updateAllEntires()
            def setPath(entry):
              FG.openFileBrowser()
              FG.accept('selectionMade', setPathCallback, [entry])
            button = DirectButton(
                scale=.04,
                pos = (xPos+0.55, 0, yPos),
                parent = editWindowFrame,
                command=setPath,
                extraArgs=[paramEntry],
                text="load",)
#            paramEntry = [entry, button]
            yPos -= 0.06
          else:
            if DEBUG:
              print "W: dgui.BaseWrapper.createEditWindow: unknown entry type"
              print "  -", self.object.__class__.__name__
              print "  -", paramType.__name__
              print "  -", paramType, paramName
              #print "  -", getFunc, setFunc, hasFunc, clearFunc
              print Enum
            paramEntry = None
        else:
          if DEBUG:
            print "W: dgui.BaseWrapper.createEditWindow: no mutableparameter for entry"
            print "  -", self.object.__class__.__name__
            print "  -", paramName
            print "  - in", self.mutableParametersSorting
          paramEntry = None
        self.parameterEntries[paramName] = paramEntry
      
      #ySize = -yPos #len(self.mutableParameters)*.11
      title='editWindow-%s' % str(self.object.getName())
      self.buttonsWindow = DirectSidebar(
        frameSize=(1.1,-yPos+0.04),
        align=ALIGN_RIGHT|ALIGN_BOTTOM, opendir=LEFT_OR_UP, orientation=VERTICAL,
        text=title,
        toggleFunc=self.editorInstance.setObjectEditwindowToggled,)
      self.buttonsWindow.toggleCollapsed(self.editorInstance.getObjectEditwindowToggled())
      
      editWindowFrame.reparentTo(self.buttonsWindow)
      editWindowFrame.setZ(-yPos-0.02)
      
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
  
  def setEntry(self, paramName, *args):
    if self.buttonsWindow:
      if self.parameterEntries.has_key(paramName):
        if len(args) > 0:
          paramValue = args[0]
        paramType, getFunc, setFunc, hasFunc, clearFunc = self.mutableParameters[paramName]
        #self.object.setParameters( {paramName: paramValue} )
        try:
          if paramType in [str, float, int]:
            paramValue = paramType(paramValue)
          elif paramType.__name__ == "Enum":
            pass # doesnt need conversion
          elif paramType.__name__ == "Filename":
            pass # dont know, but looks like it would work fine this way
          elif paramType.__name__ == "Trigger":
            pass # there is nothing to convert
            paramValue = 0 # we need a paramvalue for the following set function
          elif paramType.__name__ == "Bitmask":
            paramIndex=args[1]
            currentValue = getFunc()
            # add the value (or)
            if paramValue: paramValue = currentValue | paramType[paramIndex]
            # remove the value (xor)
            else:          paramValue = currentValue ^ paramType[paramIndex]
          elif paramType in [Vec4, Vec3, Vec2, Point4, Point3, Point2]:
            paramValue = str2type(paramValue, tuple)
          elif paramType == bool:
            pass
          else:
            print "W: dgui.BaseWrapper.setEntry: unknown conversion", paramName
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
  
  def setEntryCommand(self, paramValue, paramName, *args):
    self.setEntry(paramName, paramValue, *args)
  
  def updateAllEntires(self):
    if self.buttonsWindow:
      for paramName in self.parameterEntries:
        if paramName in self.mutableParameters:
          [paramType, getFunc, setFunc, hasFunc, clearFunc] = self.mutableParameters[paramName]
          objectParameters = self.object.getParameters()
          if paramName in objectParameters:
            if self.parameterEntries[paramName]:
              currentValue = objectParameters[paramName]
              paramEntry = self.parameterEntries[paramName]
              if paramType == bool:
                paramEntry["indicatorValue"] = currentValue
                paramEntry.setIndicatorValue()
              elif paramType.__name__ == "Enum":
                entryValue = paramEntry.get()
                if entryValue != currentValue:
                  for k, v in paramType.items():
                    if k == currentValue:
                      currentIndex = paramEntry.index(k)
                      paramEntry.set(currentIndex)
              elif paramType.__name__ == "Bitmask":
                for valueName, valueEntry in paramEntry.items():
                  valueActive = bool(paramType[valueName] & currentValue)
                  valueEntry["indicatorValue"] = valueActive
                  valueEntry.setIndicatorValue()
              elif paramType.__name__ == "Filepath":
                #entry = paramEntry
                paramEntry.enterText(currentValue)
              elif paramType.__name__ == "Trigger":
                pass # nothing needs to happen
              else:
                if paramType in [str]:
                  valueString = currentValue
                  paramEntry.enterText(valueString)
                elif paramType in [Vec4, Point4, VBase4, Vec3, Point3, VBase3, Vec2, Point2, VBase2, tuple, list]:
                  valueString = ""
                  for val in currentValue:
                    valueString += "%.3G, " % val
                  valueString = valueString[:-2]
                  paramEntry.enterText(valueString)
                elif paramType in [float, int]:
                  valueString = "%.3G" % currentValue
                  paramEntry.enterText(valueString)
                else:
                  #print "I: dgui.BaseWrapper.updateAllEntires: undefined value for", paramName, currentValue, paramType
                  pass
            else:
              print "W: dgui.BaseWrapper.updateAllEntires: no parameterEntry for", paramName, self.object.__class__.__name__
          # when the name changed, update the scenegraph
          if paramName == 'name':
            messenger.send(EVENT_SCENEGRAPH_REFRESH)



