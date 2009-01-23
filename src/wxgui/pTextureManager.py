__all__ = ["TextureManager"]
"""For managing of the textures assigned to a model."""

from pandac.PandaModules import Texture, TextureStage, CardMaker
from direct.showbase.DirectObject import DirectObject
import wx

# Local imports
from core.pConfigDefs import *
from core.pModelController import modelController
from core.pTexturePainter import texturePainter
from core.pWindow import WindowManager

THUMBNAIL_SIZE =  64
THUMBNAIL_MAX_WIDTH = 64

PREVIEW_SIZE = (128, 128)
PREVIEW_ENABLED_DEFAULT = False 

TEXTURESTAGE_MODES = {
  "Modulate" : TextureStage.MModulate,
  "Add" : TextureStage.MAdd,
  "Height" : TextureStage.MHeight,
  "Normal" : TextureStage.MNormal,
}

def modeAsString(mode):
  for k, v in TEXTURESTAGE_MODES.items():
    if v == mode: return k

def makeBitmap(tex, alpha = True, thumb = False):
  """Returns a wx.Bitmap. 'tex' should be a Panda Texture object."""
  assert isinstance(tex, Texture)
  xsize, ysize = tex.getXSize(), tex.getYSize()
  data, adata = None, None
  
  # Only available in 1.6.0 and higher
  if hasattr(Texture, "getRamImageAs"):
    data = tex.getRamImageAs("RGB")
    if alpha and tex.getNumComponents() in [2, 4]:
      adata = tex.getRamImageAs("A")
  else:
    # Grab the RGB data
    ttex = tex.makeCopy()
    ttex.setFormat(Texture.FRgb)
    if hasattr(ttex, "getUncompressedRamImage"):
      data = ttex.getUncompressedRamImage()
    else:
      data = ttex.getRamImage()
    # If we have an alpha channel, grab it as well.
    if alpha and tex.getNumComponents() in [2, 4]:
      ttex = tex.makeCopy()
      ttex.setFormat(Texture.FAlpha)
      if hasattr(ttex, "getUncompressedRamImage"):
        adata = ttex.getUncompressedRamImage()
      else:
        adata = ttex.getRamImage()
  
  # Now for the conversion to wx.
  assert not data.isNull()
  if adata == None:
    img = wx.ImageFromData(xsize, ysize, data.getData())
  else:
    assert not adata.isNull()
    img = wx.ImageFromDataWithAlpha(xsize, ysize, data.getData(), adata.getData())
  
  if thumb:
   # Resize it not to be bigger than the THUMBNAIL_SIZE.
    if xsize == ysize:
      xsize, ysize = THUMBNAIL_SIZE, THUMBNAIL_SIZE
    else:
      factor = ysize / float(THUMBNAIL_SIZE)
      xsize, ysize = int(xsize / factor), int(ysize / factor)
    if xsize > THUMBNAIL_MAX_WIDTH:
      factor = xsize / float(THUMBNAIL_MAX_WIDTH)
      xsize, ysize = int(xsize / factor), int(ysize / factor)
    img.Rescale(xsize, ysize, wx.IMAGE_QUALITY_HIGH)
  
  # Swap red and blue channels, if we aren't using 1.6.0 or higher.
  if not hasattr(Texture, "getRamImageAs"):
    for x in xrange(xsize):
      for y in xrange(ysize):
        img.SetRGB(x, y, img.GetBlue(x, y), img.GetGreen(x, y), img.GetRed(x, y))
  img = img.Mirror(False) # Downside up.
  
  return wx.BitmapFromImage(img)

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
    bitmap = makeBitmap(tex, thumb = True)
    self.bitmap = wx.StaticBitmap(self.panel, size = bitmap.GetSize())
    self.bitmap.SetBitmap(bitmap)
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

class TextureManager(wx.ScrolledWindow, DirectObject):
  """This class is responsible for managing the texture stages.""" 
  def __init__(self, *args, **kwargs):
    wx.ScrolledWindow.__init__(self, *args, **kwargs)
    self.sizer = wx.BoxSizer(wx.VERTICAL)
    self.hsizer = wx.BoxSizer(wx.HORIZONTAL)
    self.button = wx.Button(self, label = "Add &Stage")
    self.hsizer.Add(self.button, 1, wx.EXPAND, 0)
    self.paint = wx.ToggleButton(self, label = "&Paint")
    self.hsizer.Add(self.paint, 1, wx.EXPAND, 0)
    self.sizer.Add(self.hsizer, 0, wx.EXPAND, 0)
    self.combo = wx.ComboBox(self, value = "Mode", choices = TEXTURESTAGE_MODES.keys())
    self.sizer.Add(self.combo, 0, wx.EXPAND, 0)
    self.check = wx.CheckBox(self, label = "Saved &Result")
    self.sizer.Add(self.check, 0, wx.EXPAND, 0)
    self.panel = wx.Panel(self, style = wx.SUNKEN_BORDER)
    self.panel.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW))
    self.sizer.Add(self.panel, 1, wx.EXPAND, 0)
    self.psizer = wx.BoxSizer(wx.VERTICAL)
    self.panel.SetSizer(self.psizer)
    # For preview.
    self.previewCheck = wx.CheckBox(self, label = "Pre&view")
    self.previewCheck.Value = PREVIEW_ENABLED_DEFAULT
    self.sizer.Add(self.previewCheck, 0, wx.EXPAND, 0)
    self.preview = None
    self.previewBuffer = None
    self.previewCamera = None
    # Disable for now
    self.button.Disable()
    self.paint.Disable()
    self.combo.Disable()
    self.check.Disable()
    self.layers = []
    self.object = None
    self.selection = None
    self.SetSizer(self.sizer)
    self.accept(EVENT_MODELCONTROLLER_SELECT_MODEL_CHANGE, self.viewForNodePath)
    self.accept(EVENT_MODELCONTROLLER_FULL_REFRESH, self.viewForSelection)
    self.previewCheck.Bind(wx.EVT_CHECKBOX, self.onChangePreview)
    self.button.Bind(wx.EVT_BUTTON, self.onAddNewTextureStage)
    self.paint.Bind(wx.EVT_TOGGLEBUTTON, self.onPaint)
    self.panel.Bind(wx.EVT_LEFT_DOWN, self.onSelect)
    self.combo.Bind(wx.EVT_COMBOBOX, self.onChangeMode)
    self.check.Bind(wx.EVT_CHECKBOX, self.onChangeSavedResult)
  
  def __setupPreview(self):
    """Creates the preview."""
    if not self.previewCheck.Value: return
    if self.preview != None:
      self.__destroyPreview()
    self.preview = wx.StaticBitmap(self, style = wx.SUNKEN_BORDER, size = PREVIEW_SIZE)
    self.sizer.Add(self.preview, 0, wx.ADJUST_MINSIZE | wx.ALIGN_CENTER, 0)
    cm = CardMaker("preview")
    cm.setFrame(-1, 1, -1, 1)
    cm.setUvRange(Point2(0, 0), Point2(1, 1))
    self.previewTexture = Texture()
    self.previewBuffer = WindowManager.windows[0].win.makeTextureBuffer("preview", *PREVIEW_SIZE)
    self.previewBuffer.setClearColor(Vec4(1, 1, 1, 1))
    self.previewCamera = base.makeCamera2d(self.previewBuffer)
    self.previewPlane = NodePath(cm.generate())
    self.previewPlane.setFogOff(1000)
    self.previewPlane.setLightOff(1000)
    self.previewCamera.node().setScene(self.previewPlane)
    self.previewBuffer.addRenderTexture(self.previewTexture, GraphicsOutput.RTMCopyRam)
    self.previewCamera.node().setActive(texturePainter.enabled)
    self.Layout()
  
  def __destroyPreview(self):
    """Destroys the preview."""
    if self.previewBuffer != None:
      base.graphicsEngine.removeWindow(self.previewBuffer)
    if self.previewCamera != None:
      self.previewCamera.node().setActive(False)
    self.preview.Destroy()
    self.preview = None
    self.previewBuffer = None
    self.previewCamera = None
    self.previewPlane.removeNode()
    self.previewPlane = None
    self.previewTexture = Texture()
    self.Layout()
  
  def __updatePreview(self, task):
    """Only used internally."""
    if not self.previewCheck.Value: return
    if self.preview == None or self.previewCamera == None or self.previewTexture == None or not self.previewCamera.node().isActive():
      return task.done
    else:
      self.preview.SetBitmap(makeBitmap(self.previewTexture, alpha = False))
      return task.again
  
  def updatePreview(self):
    """Renders the preview."""
    if not self.previewCheck.Value: return
    if self.preview == None or self.previewCamera == None:
      self.__setupPreview()
    self.previewPlane.clearTexture()
    self.previewPlane.clearColor()
    self.previewPlane.clearColorScale()
    if self.object != None:
      if self.object.hasColor(): self.previewPlane.setColor(self.object.getColor())
      if self.object.hasColorScale(): self.previewPlane.setColorScale(self.object.getColorScale())
      stages = self.object.findAllTextureStages()
      if not hasattr(Texture, "__iter__"):
        stages = [stages.getTextureStage(i) for i in range(stages.getNumTextureStages())]
      for stage in stages:
        self.previewPlane.setTexture(stage, self.object.findTexture(stage))
    wasActive = self.previewCamera.node().isActive()
    self.previewCamera.node().setActive(True)
    base.graphicsEngine.renderFrame()
    base.graphicsEngine.renderFrame()
    self.previewCamera.node().setActive(wasActive)
    self.preview.SetBitmap(makeBitmap(self.previewTexture, alpha = False))
  
  def reset(self):
    """Clears the TextureManager by deleting all layers."""
    if texturePainter.enabled:
      self.disablePaint()
    self.selection = None
    for l in self.layers:
      l.Destroy()
    self.layers = []
    self.object = None
    self.button.Disable()
    self.paint.Disable()
    self.combo.Disable()
    self.check.Disable()
  
  def __addLayer(self, stage = None, tex = None):
    layer = TextureLayer(self.panel, stage, tex)
    layer.Bind(wx.EVT_LEFT_DOWN, self.onSelect)
    self.psizer.Add(layer, 0, wx.EXPAND, 0)
    self.layers.append(layer)
    self.Layout()
    return layer
  
  def onChangePreview(self, evt):
    if self.previewCheck.Value:
      if self.preview == None:
        self.updatePreview()
    elif self.preview != None:
      self.__destroyPreview()
  
  def onAddNewTextureStage(self, evt):
    if self.object == None: # Huh? Something must be wrong.
      self.button.Disable()
      return
    filter = "Portable Network Graphics (*.png)|*.[pP][nN][gG];*.png"
    filter += "|All files|*.*"
    dlg = wx.FileDialog(self, "Select texture", "", "", filter, wx.OPEN)
    try:
      if dlg.ShowModal() == wx.ID_OK:
        tex = loader.loadTexture(Filename.fromOsSpecific(dlg.GetPath()).getFullpath())
        if tex == None:
          wx.MessageDialog(None, "Failed to load texture!", "Error", wx.OK | wx.ICON_ERROR).ShowModal()
          return
        stage = TextureStage(tex.getName())
        self.object.setTexture(stage, tex)
        self.viewForNodePath(self.object)
        # Select the newly created layer.
        for l in self.layers:
          if l.stage == stage and l.tex == tex:
            self.select(l)
    finally:
      dlg.Destroy()
    self.updatePreview()
  
  def onPaint(self, evt = None):
    if self.object == None or self.selection == None: # Huh? Something must be wrong.
      self.paint.Disable()
      return
    if self.paint.Value and not texturePainter.enabled:
      self.enablePaint()
    elif texturePainter.enabled and not self.paint.Value:
      self.disablePaint()
  
  def enablePaint(self):
    self.paint.Value = True
    modelController.disableEditmode(deselect = False)
    texturePainter.enableEditor(self.object, self.selection.tex)
    #texturePainter.selectPaintModel()
    texturePainter.startEdit()
    self.updatePreview()
    if self.previewCamera != None:
      self.previewCamera.node().setActive(True)
    taskMgr.doMethodLater(.1, self.__updatePreview, "_TextureManager__updatePreview")
  
  def disablePaint(self):
    if self.previewCamera != None:
      self.previewCamera.node().setActive(False)
    self.paint.Value = False
    texturePainter.disableEditor()
    modelController.enableEditmode()
    taskMgr.remove("_TextureManager__updatePreview")
  
  def onChangeMode(self, evt):
    self.selection.setStageMode(self.combo.Value)
    self.updatePreview()
  
  def onChangeSavedResult(self, evt):
    self.selection.stage.setSavedResult(self.check.Value)
    self.updatePreview()
  
  def onSelect(self, evt):
    for l in reversed(self.layers):
      if l.HitTest(evt.Position) == wx.HT_WINDOW_INSIDE:
        self.select(l)
        return
    self.select(None)
  
  def select(self, layer):
    if layer == self.selection: return
    # Deselect the current.
    if self.selection != None:
      self.selection.deselect()
      self.selection = None
    self.selection = layer
    # If we have a painter, update it for the new selection.
    if texturePainter.enabled or self.paint.Value:
      if layer == None:
        self.disablePaint()
      else:
        texturePainter.stopEdit()
        self.onPaint()
    # Update the controls.
    if layer == None:
      self.paint.Disable()
      self.combo.Disable()
      self.check.Disable()
    else:
      self.paint.Enable()
      self.combo.Enable()
      self.check.Enable()
      self.combo.Value = modeAsString(layer.stage.getMode())
      self.check.Value = layer.stage.getSavedResult()
      layer.select()
  
  def viewForNodePath(self, nodePath):
    """Updates the control based on the specified NodePath."""
    self.reset()
    self.object = nodePath
    if nodePath == None: return
    self.button.Enable()
    stages = nodePath.findAllTextureStages()
    if not hasattr(Texture, "__iter__"):
      stages = [stages.getTextureStage(i) for i in range(stages.getNumTextureStages())]
    for stage in stages:
      self.__addLayer(stage, nodePath.findTexture(stage))
    self.updatePreview()
  
  def viewForSelection(self):
    """Similar to viewForNodePath, but this uses the currently selected model."""
    return self.viewForNodePath(modelController.getSelectedObject())

