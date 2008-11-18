__all__ = ["PropertyGrid"]

import wx.grid

"""
class PropertyGridTable(wx.grid.PyGridTableBase);
  def GetNumberRows(self): return 20
  def GetNumberCols(self): return 20
  def IsEmptyCell(self, row, col): return False
  def GetTypeName(self, row, col): return None
  def GetValue(self, row, col): return "cell"
  def SetValue(self, row, col, value): pass
"""

class PropertyGrid(wx.grid.Grid):
  """The grid to edit node properties."""
  def __init__(self, parent):
    wx.grid.Grid.__init__(self, parent)
    self.CreateGrid(5, 2)
    self.SetRowLabelSize(0)
    self.SetColLabelSize(0)

