__all__ = ["TextureManager"]
"""For managing of the textures assigned to a model."""

from pandac.PandaModules import Texture, TextureStage
from direct.showbase.DirectObject import DirectObject
import wx

# Local imports
from core.pConfigDefs import *
from core.pModelController import modelController

THUMBNAIL_SIZE = 64

class TextureLayer(wx.Panel):
  def __init__(self, parent, stage = None, tex = None, style = wx.RAISED_BORDER):
    wx.Panel.__init__(self, parent, style = style)
    self.sizer = wx.BoxSizer(wx.HORIZONTAL)
    self.bitmap = wx.StaticBitmap(self, size = (THUMBNAIL_SIZE, THUMBNAIL_SIZE))
    self.sizer.Add(self.bitmap, 0, wx.ADJUST_MINSIZE, 4)
    self.sizer.AddSpacer((3, 0))
    self.label = wx.StaticText(self)
    self.sizer.Add(self.label, 0, wx.SHAPED, 0)
    if tex != None:
      self.setTexture(tex)
    self.SetSizer(self.sizer)
  
  def setTexture(self, tex):
    """Changes the image. 'tex' should be a Panda texture object."""
    assert isinstance(tex, Texture)
    self.label.SetLabel(tex.getName())
    xsize, ysize = tex.getXSize(), tex.getYSize()
    data, adata = None, None
    
    # Only available in 1.6.0 and higher
    if hasattr(Texture, "getRamImageAs"):
      data = tex.getRamImageAs("RGB")
      if tex.getNumComponents() in [2, 4]:
        adata = tex.getRamImageAs("A")
    else:
      # Grab the RGB data
      ttex = tex.makeCopy()
      ttex.setFormat(Texture.FRgb)
      data = ttex.getUncompressedRamImage()
      # If we have an alpha channel, grab it as well.
      if tex.getNumComponents() in [2, 4]:
        ttex = tex.makeCopy()
        ttex.setFormat(Texture.FAlpha)
        adata = ttex.getUncompressedRamImage()
    
    # Now for the conversion to wx.
    assert not data.isNull()
    if adata == None:
      img = wx.ImageFromData(xsize, ysize, data.getData())
    else:
      assert not adata.isNull()
      img = wx.ImageFromDataWithAlpha(xsize, ysize, data, adata.getData())
    
    # Resize it not to be bigger than the THUMBNAIL_SIZE.
    if xsize > ysize:
      factor = ysize / float(THUMBNAIL_SIZE)
      xsize, ysize = int(xsize / factor), int(ysize / factor)
    elif ysize > xsize:
      factor = xsize / float(THUMBNAIL_SIZE)
      xsize, ysize = int(xsize / factor), int(ysize / factor)
    else:
      xsize, ysize = THUMBNAIL_SIZE, THUMBNAIL_SIZE
    self.bitmap.SetSize((xsize, ysize))
    img.Rescale(xsize, ysize, wx.IMAGE_QUALITY_HIGH)
    
    # Swap red and blue channels, if we aren't using 1.6.0 or higher.
    if not hasattr(Texture, "getRamImageAs"):
      for x in xrange(xsize):
        for y in xrange(ysize):
          img.SetRGB(x, y, img.GetBlue(x, y), img.GetGreen(x, y), img.GetRed(x, y))
    img = img.Mirror(False) # Downside up.
    self.bitmap.SetBitmap(wx.BitmapFromImage(img))

class TextureManager(wx.ScrolledWindow, DirectObject):
  """This class is responsible for managing the texture stages.""" 
  def __init__(self, *args, **kwargs):
    wx.ScrolledWindow.__init__(self, *args, **kwargs)
    self.sizer = wx.BoxSizer(wx.VERTICAL)
    self.layers = []
    self.object = None
    self.SetSizer(self.sizer)
    self.accept(EVENT_MODELCONTROLLER_SELECT_MODEL_CHANGE, self.viewForNodePath)
    self.accept(EVENT_MODELCONTROLLER_FULL_REFRESH, self.viewForSelection)
  
  def reset(self):
    """Clears the TextureManager by deleting all layers."""
    for l in self.layers:
      l.Destroy()
    self.layers = []
    self.object = None
  
  def __addLayer(self, stage = None, tex = None):
    layer = TextureLayer(self, stage, tex)
    self.sizer.Add(layer, 1, wx.EXPAND, 0)
    self.layers.append(layer)
    self.Layout()
    return layer
  
  def viewForNodePath(self, nodePath):
    """Updates the control based on the specified NodePath."""
    self.reset()
    self.object = nodePath
    if nodePath == None: return
    for stage in reversed(nodePath.findAllTextureStages()):
      self.__addLayer(stage, nodePath.findTexture(stage))
  
  def viewForSelection(self):
    """Similar to viewForNodePath, but this uses the currently selected model."""
    return self.viewForNodePath(modelController.getSelectedModel())

