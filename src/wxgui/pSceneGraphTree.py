__all__ = ["SceneGraphTree"]

import wx

class SceneGraphTree(wx.TreeCtrl):
  """A treeview object to show the Scene Graph."""
  def __init__(self, parent):
    wx.TreeCtrl.__init__(self, parent, style = wx.TR_HAS_BUTTONS | wx.TR_DEFAULT_STYLE | wx.SUNKEN_BORDER)

