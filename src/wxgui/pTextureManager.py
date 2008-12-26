__all__ = ["TextureManager"]
"""For managing of the textures assigned to a model."""

from pandac.PandaModules import Texture, TextureStage
from direct.showbase.DirectObject import DirectObject
import wx

# Local imports
from core.pConfigDefs import *
from core.pModelController import modelController

THUMBNAIL_SIZE =  64
THUMBNAIL_MAX_WIDTH = 64

TEXTURESTAGE_MODES = {
  "Modulate" : TextureStage.MModulate,
  "Add" : TextureStage.MAdd,
  "Height" : TextureStage.MHeight,
  "Normal" : TextureStage.MNormal,
}

def modeAsString(mode):
  for k, v in TEXTURESTAGE_MODES.items():
    if v == mode: return k

class TextureLayer(wx.Panel):
  def __init__(self, parent, stage, tex):
    wx.Panel.__init__(self, parent, style = wx.NO_BORDER)
    self.stage, self.tex = stage, tex
    self.selected = False
    self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW))
    self.sizer = wx.BoxSizer(wx.HORIZONTAL)
    self.icon = wx.StaticBitmap(self, size = (16, 16))
    self.icon.SetBitmap(wx.Bitmap("data/ui/" + modeAsString(stage.getMode()).lower() + ".png"))
    self.sizer.Add(self.icon, 0, wx.ALIGN_CENTER | wx.ALL, 4)
    self.panel = wx.Panel(self, style = wx.DOUBLE_BORDER)
    self.panel.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW))
    self.bitmap = self.makeStaticBitmap(tex)
    self.sizer.Add(self.panel, 0, wx.ADJUST_MINSIZE | wx.ALIGN_CENTER | wx.ALL, 4)
    self.sizer.AddSpacer((3, 0))
    self.label = wx.StaticText(self, label = tex.getName() + "\non " + stage.getName())
    self.sizer.Add(self.label, 0, wx.ADJUST_MINSIZE | wx.ALIGN_CENTER, 0)
    self.SetSizer(self.sizer)
    self.Layout()
  
  def Bind(self, event, handler):
    if event == wx.EVT_LEFT_DOWN:
      self.panel.Bind(event, handler)
      self.bitmap.Bind(event, handler)
      self.icon.Bind(event, handler)
      self.label.Bind(event, handler)
    wx.Panel.Bind(self, event, handler)
  
  def setStageMode(self, mode):
    if isinstance(mode, str) or isinstance(mode, unicode):
      mode = TEXTURESTAGE_MODES[mode]
    if mode != self.stage.getMode():
      self.icon.SetBitmap(wx.Bitmap("data/ui/" + modeAsString(mode).lower() + ".png"))
      self.stage.setMode(mode)
  
  def select(self):
    self.selected = True
    self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHT))
    self.panel.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHT))
    self.label.SetForegroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHTTEXT))
  
  def unfocus(self):
    if not self.selected: return
    self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_INACTIVECAPTION))
    self.panel.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_INACTIVECAPTION))
    self.label.SetForegroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_INACTIVECAPTIONTEXT))
  
  def deselect(self):
    self.selected = False
    self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW))
    self.panel.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW))
    self.label.SetForegroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOWTEXT))
  
  def makeStaticBitmap(self, tex):
    """Changes the image. 'tex' should be a Panda Texture object."""
    assert isinstance(tex, Texture)
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
    if xsize == ysize:
      xsize, ysize = THUMBNAIL_SIZE, THUMBNAIL_SIZE
    else:
      factor = ysize / float(THUMBNAIL_SIZE)
      xsize, ysize = int(xsize / factor), int(ysize / factor)
    if xsize > THUMBNAIL_MAX_WIDTH:
      factor = xsize / float(THUMBNAIL_MAX_WIDTH)
      xsize, ysize = int(xsize / factor), int(ysize / factor)
    self.SetSize((self.Size.GetWidth(), ysize + 4))
    img.Rescale(xsize, ysize, wx.IMAGE_QUALITY_HIGH)
    
    # Swap red and blue channels, if we aren't using 1.6.0 or higher.
    if not hasattr(Texture, "getRamImageAs"):
      for x in xrange(xsize):
        for y in xrange(ysize):
          img.SetRGB(x, y, img.GetBlue(x, y), img.GetGreen(x, y), img.GetRed(x, y))
    img = img.Mirror(False) # Downside up.
    
    bitmap = wx.StaticBitmap(self.panel, size = (xsize, ysize))
    bitmap.SetBitmap(wx.BitmapFromImage(img))
    return bitmap

class TextureManager(wx.ScrolledWindow, DirectObject):
  """This class is responsible for managing the texture stages.""" 
  def __init__(self, *args, **kwargs):
    wx.ScrolledWindow.__init__(self, *args, **kwargs)
    self.sizer = wx.BoxSizer(wx.VERTICAL)
    self.button = wx.Button(self, label = "Add Texture &Stage")
    self.sizer.Add(self.button, 0, wx.ADJUST_MINSIZE, 0)
    self.combo = wx.ComboBox(self, value = "Mode", choices = TEXTURESTAGE_MODES.keys())
    self.sizer.Add(self.combo, 0, wx.ADJUST_MINSIZE, 0)
    self.check = wx.CheckBox(self, label = "Saved &Result")
    self.sizer.Add(self.check, 0, wx.ADJUST_MINSIZE, 0)
    self.panel = wx.Panel(self, style = wx.SUNKEN_BORDER)
    self.panel.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW))
    self.sizer.Add(self.panel, 1, wx.EXPAND, 0)
    self.psizer = wx.BoxSizer(wx.VERTICAL)
    self.panel.SetSizer(self.psizer)
    # Disable for now
    self.button.Disable()
    self.combo.Disable()
    self.check.Disable()
    self.layers = []
    self.object = None
    self.selection = None
    self.SetSizer(self.sizer)
    self.accept(EVENT_MODELCONTROLLER_SELECT_MODEL_CHANGE, self.viewForNodePath)
    self.accept(EVENT_MODELCONTROLLER_FULL_REFRESH, self.viewForSelection)
    self.panel.Bind(wx.EVT_SET_FOCUS, self.onSetFocus)
    self.panel.Bind(wx.EVT_KILL_FOCUS, self.onKillFocus)
    self.panel.Bind(wx.EVT_LEFT_DOWN, self.onSelect)
    self.combo.Bind(wx.EVT_COMBOBOX, self.onChangeMode)
    self.check.Bind(wx.EVT_CHECKBOX, self.onChangeSavedResult)
  
  def reset(self):
    """Clears the TextureManager by deleting all layers."""
    self.selection = None
    for l in self.layers:
      l.Destroy()
    self.layers = []
    self.object = None
    self.button.Disable()
    self.combo.Disable()
    self.check.Disable()
  
  def __addLayer(self, stage = None, tex = None):
    layer = TextureLayer(self.panel, stage, tex)
    layer.Bind(wx.EVT_LEFT_DOWN, self.onSelect)
    self.psizer.Add(layer, 0, wx.EXPAND, 0)
    self.layers.append(layer)
    self.Layout()
    return layer
  
  def onChangeMode(self, evt):
    self.selection.setStageMode(self.combo.Value)
  
  def onChangeSavedResult(self, evt):
    self.selection.stage.setSavedResult(self.check.Value)
  
  def onSetFocus(self, evt):
    if self.selection != None:
      self.selection.select()
  
  def onKillFocus(self, evt):
    print "AAAAAAAAAAAAAHGR"
    if self.selection != None:
      self.selection.defocus()
  
  def onSelect(self, evt):
    for l in self.layers:
      if l.HitTest(evt.Position) == wx.HT_WINDOW_INSIDE:
        self.select(l)
        return
    self.select(None)
  
  def select(self, layer):
    if layer == self.selection: return
    if self.selection != None:
      self.selection.deselect()
      self.selection = None
    if layer == None:
      self.combo.Disable()
      self.check.Disable()
    else:
      self.combo.Enable()
      self.check.Enable()
      self.combo.Value = modeAsString(layer.stage.getMode())
      self.check.Value = layer.stage.getSavedResult()
      self.selection = layer
      layer.select()
  
  def viewForNodePath(self, nodePath):
    """Updates the control based on the specified NodePath."""
    self.reset()
    self.object = nodePath
    if nodePath == None: return
    self.button.Enable()
    for stage in reversed(nodePath.findAllTextureStages()):
      self.__addLayer(stage, nodePath.findTexture(stage))
  
  def viewForSelection(self):
    """Similar to viewForNodePath, but this uses the currently selected model."""
    return self.viewForNodePath(modelController.getSelectedModel())

