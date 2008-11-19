__all__ = ["PropertyGrid"]
from wx.grid import *
import wx, re

# Local imports
from pProperties import EnumProperty, Enums, Properties

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
    self.EnableScrolling(False, False)
    self.CreateGrid(0, 2)
    self.SetRowLabelSize(0)
    self.SetColLabelSize(0)
    self.SetColSize(0, self.ClientSize.GetWidth() / 2)
    self.SetColSize(1, self.ClientSize.GetWidth() / 2)
    self.SetSelectionMode(0)
    self.properties = []
    self.object = None
    
    # Catch events
    #self.Bind(EVT_GRID_CELL_CHANGE, self.onCellChange)
    self.Bind(wx.EVT_SIZE, self.onSize)
    base.accept("sgtree-selection-changed", self.viewForNodePath)
  
  def onSize(self, evt = None):
    """Invoked when the size has changed."""
    self.SetColSize(0, self.ClientSize.GetWidth() / 2)
    self.SetColSize(1, self.ClientSize.GetWidth() / 2)
  
  def reset(self):
    """Entirely resets the grid."""
    self.properties = []
    self.ClearGrid()
    self.DeleteRows(0, self.GetNumberRows())
  
  def viewForNodePath(self, nodePath):
    """Updates the control based on the specified NodePath."""
    self.reset()
    self.object = nodePath
    for propName, prop in Properties.NodePath.items():
      self.addProperty(propName, prop, prop.getter(nodePath))
  
  def addProperty(self, propName, prop, value = None):
    """ Adds a new property to the control. """
    assert self.AppendRows(1)
    row = self.GetNumberRows() - 1
    self.SetCellValue(row, 0, propName)
    self.SetReadOnly(row, 0, True)
    self.SetReadOnly(row, 1, prop.IsReadOnly)
    self.SetCellRenderer(row, 1, prop.MakeRenderer())
    self.SetCellEditor(row, 1, prop.MakeEditor())
    if value != None: self.SetCellValue(row, 1, prop.ValueAsString(value))
    
    self.properties.append(prop)
  
  #def setProperty(self, propName, value):
  #  assert self.properties.has_key(propName)
  #  self.SetCellValue(self.properties[propName][0], 1, value)
  #
  #def onCellChange(self, evt):
  #   if evt.Col != 1: return
  #   value = self.GetCellValue(evt.Row, 1)
  #   # Veto the event if the value is invalid.
  #   if re.match(re.compile(r"([(]?)([0-9]*)([.]?)([0-9]*)([ ]*),([ ]*)([0-9]*)([.]?)([0-9]*)([)]?)"), value) != None:
  #     self.SetCellValue(evt.Row, 1, "(" + value.replace("(", "").replace(")", "").replace(" ", "").replace(",", ", ") + ")")
  #   else:
  #     evt.Veto()

