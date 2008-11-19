__all__ = ["SceneGraphTree"]

from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import NodePath
import wx

# Local imports
from core.pModelController import modelController
from core.pModelIdManager import modelIdManager

class SceneGraphTree(wx.TreeCtrl, DirectObject):
  """A treeview object to show the Scene Graph."""
  def __init__(self, parent):
    wx.TreeCtrl.__init__(self, parent, style = wx.TR_HAS_BUTTONS | wx.TR_DEFAULT_STYLE | wx.SUNKEN_BORDER)
    
    # Create an imagelist and add some images
    self.imgList = wx.ImageList(16, 16)
    #self.imgList.Add(wx.Bitmap(Filename(APP_PATH+"content/gui/properties.png").toOsSpecific()))
    #self.imgList.Add(wx.Bitmap(Filename(APP_PATH+"content/gui/script.png").toOsSpecific()))
    #self.imgList.Add(wx.Bitmap(Filename(APP_PATH+"content/gui/sun.png").toOsSpecific()))
    #self.imgList.Add(wx.Bitmap(Filename(APP_PATH+"content/gui/sphere.png").toOsSpecific()))
    #self.imgList.Add(wx.Bitmap(Filename(APP_PATH+"content/gui/mountain.png").toOsSpecific()))
    #self.imgList.Add(wx.Bitmap(Filename(APP_PATH+"content/gui/water.png").toOsSpecific()))
    #self.imgList.Add(wx.Bitmap(Filename(APP_PATH+"content/gui/character.png").toOsSpecific()))
    #self.imgList.Add(wx.Bitmap(Filename(APP_PATH+"content/gui/pyramid.png").toOsSpecific()))
    #self.imgList.Add(wx.Bitmap(Filename(APP_PATH+"content/gui/light.png").toOsSpecific()))
    self.AssignImageList(self.imgList)
    self.Bind(wx.EVT_TREE_SEL_CHANGED, self.onSelChange)
    self.reload()
    
    self.accept(EVENT_MODELCONTROLLER_SELECT_MODEL, self.selectNodePath)
  
  def onSelChange(self, item):
    """This event gets invoked when the selection gets changed on the tree view."""
    if not isinstance(item, wx.TreeItemId):
      item = item.GetItem()
    modelController.selectModel(modelIdManager.getObject(modelIdManager.getObjectId(self.GetItemPyData(item))))
    #base.messenger.send(EVENT_MODELCONTROLLER_SELECT_MODEL, [self.GetItemPyData(item)])
  
  def selectNodePath(self, nodePath):
    """Selects the given NodePath in the tree."""
    pass #TODO
  
  def reload(self):
    """Clears the tree view and reloads it based on the scene graph."""
    self.DeleteAllItems()
    
    # Create the root render node
    renderId = self.AddRoot("render")
    self.SetItemPyData(renderId, base.render)
    self.__appendChildren(renderId, base.render)
    self.Expand(renderId)
    # Force a select event.
    self.onSelChange(renderId)
  
  def __appendChildren(self, parent, nodePath):
    """Used internally to recursively add the children of a nodepath to the scene graph browser."""
    for c in xrange(nodePath.getNumChildren()):
      child = nodePath.getChild(c)
      tree = self.AppendItem(parent, child.getName())
      self.SetItemPyData(tree, child)
      self.__appendChildren(tree, child)

