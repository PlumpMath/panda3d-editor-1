from pandac.PandaModules import *
from direct.showbase.DirectObject import DirectObject
from direct.gui.DirectButton import DirectButton
from direct.gui.DirectGui import *
from direct.gui.DirectCheckBox import DirectCheckBox
from direct.gui.DirectScrolledList import DirectScrolledList

from dgui.directSidebar import *

from core.pConfigDefs import *
from core.pTexturePainter import texturePainter, PNMBrush_BrushEffect_Enum, \
TexturePainter_PaintMode_Enum, TEXTUREPAINTER_FUNCTION_READ, \
TEXTUREPAINTER_FUNCTION_PAINT_POINT, TEXTUREPAINTER_FUNCTION_PAINT_LINE, \
TEXTUREPAINTER_FUNCTION_PAINT_RECTANGLE

class TexturePainterGui(DirectObject):
  def __init__(self, guiEditorInstance):
    self.guiEditorInstance = guiEditorInstance
    self.accept(EVENT_TEXTUREPAINTER_STARTEDIT, self.showTexturepainterTools)
  
  def showTexturepainterTools(self):
    print "I: dgui.EditorApp.showTexturepainterTools"
    def readBrushSettings(update=True,*args):
      # read
      color, size, smooth, effect = texturePainter.getBrushSettings()
      # show
      #colorStr = str(color).strip('VBase4D(').strip(')')
      colorStr = "%.3G, %.3G, %.3G, %.3G" % (color[0], color[1], color[2], color[3])
      self.texturePainterTools['color'].enterText(colorStr)
      self.texturePainterTools['size'].enterText(str(size))
      self.texturePainterTools['smooth']["indicatorValue"] = smooth
      self.texturePainterTools['smooth'].setIndicatorValue()
      for k, v in PNMBrush_BrushEffect_Enum.items():
        if v == effect:
          currentIndex = self.texturePainterTools['effect'].index(k)
          self.texturePainterTools['effect'].set(currentIndex)
      
      if update is True:
        writeBrushSettings(False)
    
    def writeBrushSettings(update=True,*args):
      # read entries
      try:
        colorStr = self.texturePainterTools['color'].get()
        colorList = colorStr.strip('(').strip(')').split(',')
        color = VBase4D(float(colorList[0]),
                        float(colorList[1]),
                        float(colorList[2]),
                        float(colorList[3]))
      except:
        color = VBase4D(1,1,1,1)
      
      try:
        size = float(self.texturePainterTools['size'].get())
      except:
        size = 10
      
      smooth = self.texturePainterTools['smooth']["indicatorValue"]
      
      effectName = self.texturePainterTools['effect'].get()
      effect = PNMBrush_BrushEffect_Enum[effectName]
      
      # write
      texturePainter.setBrushSettings(color, size, smooth, effect)
      
      if update is True:
        readBrushSettings(False)
    
    editWindowFrame = DirectFrame(
        suppressMouse=1,
      )
    self.texturePainterTools = dict()
    yPos = -0.02
    xPos = 0.47
    
    # --- TITLE ---
    paramLabel = DirectLabel(
        text = 'color',
        parent = editWindowFrame,
        scale=.04,
        pos = (0.1, 0, yPos),
        text_align = TextNode.ALeft
    )
    # color
    paramEntry = DirectEntry(
        scale=.04,
        pos = (xPos, 0, yPos),
        parent = editWindowFrame,
        command=writeBrushSettings,
        extraArgs=['color'],
        initialText="(1,1,1,1)",
        numLines = 1,
        focus=0,
        width=12,
        focusOutCommand=writeBrushSettings,
        focusOutExtraArgs=['color'],
        text_align = TextNode.ALeft,
        frameSize=(-.3,12.3,-.3,0.9),)
    self.texturePainterTools['color'] = paramEntry
    yPos -= 0.06
    
    # --- TITLE ---
    paramLabel = DirectLabel(
        text = 'size',
        parent = editWindowFrame,
        scale=.04,
        pos = (0.1, 0, yPos),
        text_align = TextNode.ALeft
    )
    # size
    paramEntry = DirectEntry(
        scale=.04,
        pos = (xPos, 0, yPos),
        parent = editWindowFrame,
        command=writeBrushSettings,
        extraArgs=['size'],
        initialText="10",
        numLines = 1,
        focus=0,
        width=12,
        focusOutCommand=writeBrushSettings,
        focusOutExtraArgs=['size'],
        text_align = TextNode.ALeft,
        frameSize=(-.3,12.3,-.3,0.9),)
    self.texturePainterTools['size'] = paramEntry
    yPos -= 0.06
    
    # --- TITLE ---
    paramLabel = DirectLabel(
        text = 'smooth',
        parent = editWindowFrame,
        scale=.04,
        pos = (0.1, 0, yPos),
        text_align = TextNode.ALeft
    )
    # smooth
    paramEntry = DirectCheckButton(
        scale=.04,
        pos = (xPos+0.05, 0, yPos),
        parent = editWindowFrame,
        command=writeBrushSettings,
        extraArgs=['smooth'],
        )
    self.texturePainterTools['smooth'] = paramEntry
    yPos -= 0.06
    
    # --- TITLE ---
    paramLabel = DirectLabel(
        text = 'mode',
        parent = editWindowFrame,
        scale=.04,
        pos = (0.1, 0, yPos),
        text_align = TextNode.ALeft
    )
    # effect
    items = PNMBrush_BrushEffect_Enum.keys()
    '''# select the default item 0, this must be done because it
    # may be undefined, and thus updateAll will not set it
    for k, v in PNMBrush_BrushEffect_Enum.items():
      if v == PNMBrush.BEBlend:
        i = k'''
    initialitem = 0 #items.index(i)
    paramEntry = DirectOptionMenu(
        pos = (xPos, 0, yPos),
        scale=.04,
        parent = editWindowFrame,
        command=writeBrushSettings,
        extraArgs=['effect'],
        items=items,
        initialitem=initialitem,
        highlightColor=(0.65,0.65,0.65,1),)
    self.texturePainterTools['effect'] = paramEntry
    yPos -= 0.06
    
    readBrushSettings()
    
    self.accept(EVENT_TEXTUREPAINTER_BRUSHCHANGED, readBrushSettings)
    
    
    # --- PAINT MODE ---
    def readPaintMode(update=False, *args):
      paintMode = texturePainter.getPaintMode()
      print "I: readPaintMode", paintMode
      for k, v in TexturePainter_PaintMode_Enum.items():
        print "  -", k, v
        if v == paintMode:
          setIndex = self.texturePainterTools['paintmode'].index(k)
          print "  -equal", v, setIndex
          self.texturePainterTools['paintmode'].set(setIndex)
      
      if update is True:
        writePaintMode()
    
    def writePaintMode(update=False, *args):
      paintModeName = self.texturePainterTools['paintmode'].get()
      paintMode = TexturePainter_PaintMode_Enum[paintModeName]
      texturePainter.setPaintMode(paintMode)
      
      if update is True:
        readPaintMode()
    
    def setPaintMode(paintMode):
      print "I: EditorApp.showTexturepainterTools.setPaintMode:", paintMode
      texturePainter.setPaintMode(paintMode)
      readPaintMode()
    
    # --- TITLE ---
    paramLabel = DirectLabel(
        text = 'brush',
        parent = editWindowFrame,
        scale=.04,
        pos = (0.1, 0, yPos),
        text_align = TextNode.ALeft
    )
    # effect
    items = TexturePainter_PaintMode_Enum.keys()
    initialitem = 0
    paramEntry = DirectOptionMenu(
        pos = (xPos, 0, yPos),
        scale=.04,
        parent = editWindowFrame,
        command = writePaintMode,
        extraArgs = ['brush'],
        items = items,
        initialitem = initialitem,
        highlightColor = (0.65,0.65,0.65,1),
      )
    self.texturePainterTools['paintmode'] = paramEntry
    yPos -= 0.06
    
    readPaintMode()
    
    self.accept("shift", setPaintMode, [TEXTUREPAINTER_FUNCTION_READ])
    self.accept("shift-up", setPaintMode, [TEXTUREPAINTER_FUNCTION_PAINT_POINT])
    self.accept("control", setPaintMode, [TEXTUREPAINTER_FUNCTION_PAINT_LINE])
    self.accept("control-up", setPaintMode, [TEXTUREPAINTER_FUNCTION_PAINT_POINT])
    self.accept("alt", setPaintMode, [TEXTUREPAINTER_FUNCTION_PAINT_RECTANGLE])
    self.accept("alt-up", setPaintMode, [TEXTUREPAINTER_FUNCTION_PAINT_POINT])
    
    # --- window containing the edit tools ---
    self.texturePainterWindow = DirectSidebar(
        frameSize=(1.1,-yPos+0.04),
        #frameSize=(0.8,0.4), pos=(-.05,0,-0.1), align=ALIGN_RIGHT|ALIGN_TOP, orientation=VERTICAL
        pos=Vec3(0,0,-0.45),
        align=ALIGN_RIGHT|ALIGN_TOP,
        opendir=LEFT_OR_UP,
        orientation=VERTICAL,
        text='painting',
        frameColor=(0,0,0,.8),
      )
    editWindowFrame.reparentTo(self.texturePainterWindow)
    editWindowFrame.setZ(-yPos-0.02)
    
    # accept the destroy event
    self.accept(EVENT_TEXTUREPAINTER_STOPEDIT, self.destroyTexturepainterTools)
  
  def destroyTexturepainterTools(self):
    self.ignore(EVENT_TEXTUREPAINTER_STOPEDIT)
    self.texturePainterWindow.destroy()
