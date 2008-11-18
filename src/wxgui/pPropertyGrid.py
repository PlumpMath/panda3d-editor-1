__all__ = ["PropertyGrid"]

from pandac.PandaModules import Vec2
from wx.grid import *
import re

"""
class PropertyGridTable(PyGridTableBase);
  def GetNumberRows(self): return 20
  def GetNumberCols(self): return 20
  def IsEmptyCell(self, row, col): return False
  def GetTypeName(self, row, col): return None
  def GetValue(self, row, col): return "cell"
  def SetValue(self, row, col, value): pass
"""

class PropertyGrid(Grid):
  """The grid to edit node properties."""
  def __init__(self, *args, **kwargs):
    Grid.__init__(self, *args, **kwargs)
    self.CreateGrid(0, 2)
    self.SetRowLabelSize(0)
    self.SetColLabelSize(0)
    self.SetSelectionMode(0)
    self.properties = {}
    self.addProperty("Position", None, Vec2(1,2))
    self.addProperty("Orientation", 3.5)
    
    # Catch events
    self.Bind(EVT_GRID_CELL_CHANGE, self.onCellChange)
  
  def addProperty(self, propName, propType = None, value = None):
    """ Adds a new property to the control. """
    assert self.AppendRows(1)
    row = self.GetNumberRows() - 1
    self.SetCellValue(row, 0, propName)
    self.SetReadOnly(row, 0, True)
    self.SetReadOnly(row, 1, False)
    # If it's not a type, find it out somehow.
    if propType == None:
      propType = type(value)
    elif not isinstance(propType, type):
      propType = type(propType)
    # See what type it is.
    if propType == int or propType == long:
      self.SetCellRenderer(row, 1, GridCellNumberRenderer())
      self.SetCellEditor(row, 1, GridCellNumberEditor())
      #if value == None: self.SetCellValue(row, 1, 0)
      #else: self.SetCellValue(row, 1, value)
    elif propType == bool:
      self.SetCellRenderer(row, 1, GridCellBoolRenderer())
      self.SetCellEditor(row, 1, GridCellBoolEditor())
      #if value == None: self.SetCellValue(row, 1, False)
      #else: self.SetCellValue(row, 1, value)
    elif propType == float:
      self.SetCellRenderer(row, 1, GridCellFloatRenderer())
      self.SetCellEditor(row, 1, GridCellFloatEditor())
      #if value == None: self.SetCellValue(row, 1, 0.0)
      #else: self.SetCellValue(row, 1, value)
    elif propType == Vec2:
      self.SetCellValue(row, 1, "(%s, %s)" % (value[0], value[1]))
    
    self.properties[propName] = (row, propType)
  
  def setProperty(self, propName, value):
    assert self.properties.has_key(propName)
    self.SetCellValue(self.properties[propName][0], 1, value)
  
  def onCellChange(self, evt):
     if evt.Col != 1: return
     value = self.GetCellValue(evt.Row, 1)
     # Veto the event if the value is invalid.
     if re.match(re.compile(r"([(]?)([0-9]*)([.]?)([0-9]*)([ ]*),([ ]*)([0-9]*)([.]?)([0-9]*)([)]?)"), value) != None:
       self.SetCellValue(evt.Row, 1, "(" + value.replace("(", "").replace(")", "").replace(" ", "").replace(",", ", ") + ")")
     else:
       evt.Veto()

