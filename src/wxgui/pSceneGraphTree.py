__all__ = ["SceneGraphTree"]

from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import NodePath
import wx

# Local imports
from core.pModelController import modelController
from core.pModelIdManager import modelIdManager
from core.pConfigDefs import *

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
    
    self.modelDict = {}
    self.reload()
    
    self.accept(EVENT_SCENEGRAPHBROWSER_REFRESH, self.reload)
    self.accept(EVENT_MODELCONTROLLER_SELECT_MODEL, self.selectNodePath)
  
  def onSelChange(self, item):
    """This event gets invoked when the selection gets changed on the tree view."""
    if not isinstance(item, wx.TreeItemId):
      item = item.GetItem()
    modelController.selectModel(self.GetItemPyData(item))
    #base.messenger.send(EVENT_MODELCONTROLLER_SELECT_MODEL, [self.GetItemPyData(item)])
  
  def selectNodePath(self, model):
    """Selects the given NodePath in the tree."""
    if model in self.modelDict:
      treeItem = self.modelDict[model]
      self.SelectItem(treeItem)
  
  def reload(self):
    """Clears the tree view and reloads it based on the scene graph."""
    self.DeleteAllItems()
    self.modelDict.clear()
    
    # Create the root render node
    renderId = self.AddRoot("render")
    # render should send a pydata None (deselects all models)
    self.SetItemPyData(renderId, None)
    self.__appendChildren(renderId, base.render)
    self.modelDict[None] = renderId
    self.Expand(renderId)
    # Force a select event.
    self.onSelChange(renderId)
  
  def __appendChildren(self, treeParent, nodePath):
    """Used internally to recursively add the children of a nodepath to the scene graph browser."""
    for c in xrange(nodePath.getNumChildren()):
      childNodePath = nodePath.getChild(c)
      childModel = modelIdManager.getObject(modelIdManager.getObjectId(childNodePath))
      if childNodePath.hasTag(ENABLE_SCENEGRAPHBROWSER_MODEL_TAG):
        treeItem = self.AppendItem(treeParent, childNodePath.getName())
        self.SetItemPyData(treeItem, childModel)
        self.modelDict[childNodePath] = treeItem
        # Iterate through the children
        self.__appendChildren(treeItem, childNodePath)

