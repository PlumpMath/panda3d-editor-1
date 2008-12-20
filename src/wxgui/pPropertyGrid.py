__all__ = ["PropertyGrid"]

from pandac.PandaModules import NodePath
from direct.showbase.DirectObject import DirectObject
from wx.grid import *
import wx, re

# Local imports
from core.pConfigDefs import *
from core.pModelController import modelController
from core.modules.pLightNodeWrapper import LightNodeWrapper

def makeRenderer(type):
  """Returns a new GridCellRenderer for the given property type."""
  if type == bool: # Bool must be checked before int
    return GridCellBoolRenderer()
  elif type == int or type == long:
    return GridCellNumberRenderer()
  elif type == float:
    return GridCellFloatRenderer()
  else:
    return GridCellStringRenderer()

def makeEditor(type):
  """Returns a new GridCellEditor for the given property type."""
  if type == bool: # Bool must be checked before int
    return GridCellBoolEditor()
  elif type == int or type == long:
    return GridCellNumberEditor()
  elif type == float:
    return GridCellFloatEditor()
  elif isinstance(type, dict):
    return GridCellChoiceEditor(type.keys())
  else:
    return GridCellTextEditor()

class PropertyGrid(Grid, DirectObject):
  """The grid to edit node properties."""
  def __init__(self, *args, **kwargs):
    Grid.__init__(self, *args, **kwargs)
    self.EnableScrolling(False, False)
    self.EnableEditing(True)
    self.CreateGrid(0, 2)
    self.SetRowLabelSize(0)
    self.SetColLabelSize(0)
    self.SetColSize(0, self.ClientSize.GetWidth() / 2)
    self.SetColSize(1, self.ClientSize.GetWidth() / 2)
    self.SetSelectionMode(0)
    self.properties = []
    self.object = None
    
    # Catch events
    self.Bind(EVT_GRID_CELL_CHANGE, self.onCellChange)
    self.Bind(wx.EVT_SIZE, self.onSize)
    self.accept(EVENT_MODELCONTROLLER_SELECT_MODEL_CHANGE, self.viewForNodePath)
    self.accept(EVENT_MODELCONTROLLER_FULL_REFRESH, self.viewForSelection)
  
  def onSize(self, evt = None):
    """Invoked when the size has changed."""
    self.SetColSize(0, self.ClientSize.GetWidth() / 2)
    self.SetColSize(1, self.ClientSize.GetWidth() / 2)
  
  def reset(self):
    """Entirely resets the grid."""
    self.properties = []
    self.ClearGrid()
    if self.GetNumberRows() > 0:
      self.DeleteRows(0, self.GetNumberRows())
  
  def viewForNodePath(self, nodePath):
    """Updates the control based on the specified NodePath."""
    self.reset()
    self.object = nodePath
    if nodePath == None: return
    for propName, prop in nodePath.mutableParameters.items():
      if prop != None:
        self.addProperty(propName, prop[0], nodePath.getParameter(propName))
  
  def viewForSelection(self):
    """Similar to viewForNodePath, but this uses the currently selected model."""
    return self.viewForNodePath(modelController.getSelectedModel())
  
  def addProperty(self, propName, propType, value = None):
    """ Adds a new property to the control. """
    assert self.AppendRows(1)
    row = self.GetNumberRows() - 1
    self.SetCellValue(row, 0, propName)
    self.SetReadOnly(row, 0, True)
    self.SetReadOnly(row, 1, False)
    self.SetCellRenderer(row, 1, makeRenderer(propType))
    self.SetCellEditor(row, 1, makeEditor(propType))
    self.SetCellValue(row, 1, str(value))
  
  def onCellChange(self, evt):
     """Invoked when a cell is modified."""
     if self.object == None: return
     if evt.Col != 1: return
     name = self.GetCellValue(evt.Row, 0)
     value = self.GetCellValue(evt.Row, 1)
     try:
       self.object.setParameter(name, eval(value))
       #FIXME: If it changed the nodepath name, it should reload the scene graph tree.
       #if prop.setter == NodePath.setName:
       #  messenger.send(EVENT_SCENEGRAPHBROWSER_REFRESH)
     except Exception, ex: # Stop the change if the value is invalid.
       print ex
       evt.Veto()
     self.SetCellValue(evt.Row, 1, str(self.object.getParameter(name)))
