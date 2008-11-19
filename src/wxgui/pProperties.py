__all__ = ["Enums", "Properties"]

from pandac.PandaModules import NodePath, Vec2, Point3, Vec3, Vec4
from pandac.PandaModules import TransparencyAttrib, TransparencyAttrib
from wx.grid import *

class Property:
  def __init__(self, getter, setter, hasser = None):
    self.getter = getter
    self.setter = setter
    self.hasser = hasser
  
  IsReadOnly = True
  def MakeRenderer(self): return GridCellStringRenderer()
  def MakeEditor(self):   return GridCellTextEditor()
  def ValueAsString(self, value): return str(value)
  def StringToValue(self, value): return value
  def SetValue(self, obj, value): return self.setter(obj, value)
  def GetValue(self, obj):
    if self.hasser != None and not self.hasser(obj):
      return None
    else:
      return self.getter(obj)

class NumberProperty(Property):
  IsReadOnly = False
  def MakeRenderer(self): return GridCellNumberRenderer()
  def MakeEditor(self):   return GridCellNumberEditor()
  def StringToValue(self, value): return int(value)

class FloatProperty(Property):
  IsReadOnly = False
  def MakeRenderer(self): return GridCellFloatRenderer()
  def MakeEditor(self):   return GridCellFloatEditor()
  def StringToValue(self, value): return float(value)

class BoolProperty(Property):
  IsReadOnly = False
  def MakeRenderer(self): return GridCellBoolRenderer()
  def MakeEditor(self):   return GridCellBoolEditor()
  def StringToValue(self, value): return bool(value)

class TupleProperty(Property):
  def __init__(self, count, *args, **kwargs):
    Property.__init__(self, *args, **kwargs)
    self.count = count

  IsReadOnly = False
  def ValueAsString(self, value):
    if value == None:
      return "None"
    else:
      return "(%s)" % ", ".join([ str(value[i]) for i in range(self.count) ])
  
  def StringToValue(self, value):
    if value == "None": return value
    return tuple([float(i) for i in value.replace("(", "").replace(")", "").replace(" ", "").split(",")])
  
  def SetValue(self, obj, value):
    if self.count == 4 and len(value) == 3:
      value = value + (1, )
    if self.count == 4:
      self.setter(obj, Vec4(*value))
    elif self.count == 3:
      self.setter(obj, Vec3(*value))
    elif self.count == 2:
      self.setter(obj, Vec2(*value))
    else:
      self.setter(obj, value)

class EnumProperty(Property):
  def __init__(self, *args, **kwargs):
    Property.__init__(self, *args, **kwargs)
    assert self.hasser == None # Not yet supported
    self.choiceString = ",".join(self.choices.keys())  
  
  IsReadOnly = False
  def MakeRenderer(self): return GridCellEnumRenderer(self.choiceString)
  def MakeEditor(self):   return GridCellEnumEditor(self.choiceString)
  def StringToValue(self, value): return choices[value]

class Enums:
  class TransparencyAttrib:
    class Mode(EnumProperty):
      choices = {
        "MAlpha"           : TransparencyAttrib.MAlpha,
        "MNone"            : TransparencyAttrib.MNone,
        "MNotused"         : TransparencyAttrib.MNotused,
        "MMultisample"     : TransparencyAttrib.MMultisample,
        "MMultisampleMask" : TransparencyAttrib.MMultisampleMask,
        "MBinary"          : TransparencyAttrib.MBinary,
        "MDual"            : TransparencyAttrib.MDual,
      }

class Properties:
  NodePath = {
    "Pos"          : TupleProperty(3, NodePath.getPos, NodePath.setPos),
    "Hpr"          : TupleProperty(3, NodePath.getHpr, NodePath.setHpr),
    "Transparency" : BoolProperty(NodePath.getTransparency, NodePath.setTransparency),
    "Color"        : TupleProperty(4, NodePath.getColor, NodePath.setColor, NodePath.hasColor),
    "ColorScale"   : TupleProperty(4, NodePath.getColorScale, NodePath.setColorScale, NodePath.hasColorScale),
  }

