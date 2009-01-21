__all__ = ["VShader", "VShaderProgram"]
"""
Useful for automating shader generation.
"""

import re
from pandac.PandaModules import Shader, Texture, TextureStage

class VShaderProgram:
  """Represents a single shader program, eg. Vertex or Fragment."""
  def __init__(self, name):
    """Parameter name is the name of the function, e.g. vshader or fshader."""
    self.Name = name
    # Items should be like (Name, Type, Semantic)
    self.In = []
    self.Out = []
    self.Body = ""
    self.__curTex = 0
  
  def Write(self):
    """Returns the shader program as string."""
    prog = "void %s(" % self.Name
    first = True
    for name, type, semantic in self.In:
      if first: first = False
      else: prog += ",\n      " + (" " * len(self.Name))
      if semantic == None or semantic == "":
        prog += "in %s %s" % (type, name)
      else:
        prog += "in %s %s : %s" % (type, name, semantic)
    for name, type, semantic in self.Out:
      if first: first = False
      else: prog += ",\n      " + (" " * len(self.Name))
      if semantic == None or semantic == "":
        prog += "out %s %s" % (type, name)
      else:
        prog += "out %s %s : %s" % (type, name, semantic)
    body = self.Body.strip().split("\n")
    body = [ "  " + line.strip() for line in body ]
    body = "\n".join(body)
    prog += ") {\n" + body + "\n}"
    return prog
  
  def AddParam(self, dir, name, type = None, sstr = None):
    """Adds a parameter. Use AddInput or AddOutput instead."""
    assert dir in ["in", "out"]
    # If no type or semantic is given figure it out ourselves.
    if name == "o_color":
      if type == None: type = "float4"
      if sstr == None: sstr = "COLOR"
    elif name == "vtx_position":
      if type == None: type = "float4"
      if sstr == None: sstr = "POSITION"
    elif name == "vtx_normal":
      if type == None: type = "float3"
      if sstr == None: sstr = "NORMAL"
    elif name == "vtx_color":
      if type == None: type = "float4"
      if sstr == None: sstr = "COLOR"
    elif name.startswith("vtx_texcoord"):
      if type == None: type = "float2"
      if sstr == None: sstr = name.upper()[4:]
    elif name.startswith("vtx_tangent"):
      if type == None: type = "float3"
    elif name.startswith("vtx_binormal"):
      if type == None: type = "float3"
    elif name.startswith("l_position"):
      if type == None: type = "float4"
      if sstr == None: sstr = name.upper()[2:]
    elif name.startswith("l_color"):
      if type == None: type = "float4"
      if sstr == None: sstr = name.upper()[2:]
    elif name.startswith("l_texcoord"):
      if type == None: type = "float2"
      if sstr == None: sstr = name.upper()[2:]
    elif name == "attr_material":
      if type == None: type = "uniform float4x4"
    elif name == "attr_color":
      if type == None: type = "uniform float4"
    elif name.startswith("alight_"):
      if type == None: type = "uniform float4"
    elif name.startswith("dlight_"):
      if type == None: type = "uniform float4x4"
    elif name.startswith("texpad_") or name.startswith("texpix_"):
      if type == None: type = "uniform float2"
    elif name.startswith("row") or name.startswith("col"):
      if type == None: type = "uniform float4"
    elif (name.startswith("mspos") or name.startswith("cspos")
       or name.startswith("wspos") or name.startswith("vspos")):
      if type == None: type = "uniform float4"
    elif (name.startswith("mstrans_") or name.startswith("cstrans_")
       or name.startswith("wstrans_") or name.startswith("vstrans_")
       or name.startswith("trans_") or name.startswith("tpose_")
       or name.startswith("mat_") or name.startswith("inv_")
       or name.startswith("tps_") or name.startswith("itp_")):
      if type == None: type = "uniform float4x4"
    if dir == "out":
      self.Out.append((name, type, sstr))
    else:
      self.In.append((name, type, sstr))
  
  def AddInput(self, name, type = None, semantic = None):
    """Adds an input parameter."""
    self.AddParam("in", name, type, semantic)
  
  def AddOutput(self, name, type = None, semantic = None):
    """Adds an output parameter."""
    self.AddParam("out", name, type, semantic)
  
  def AddInputs(self, *args):
    """Adds a list of input parameters."""
    if len(args) == 1 and isinstance(args[0], list):
      args = args[0]
    for arg in args:
      if isinstance(arg, str):
        self.AddParam("in", arg)
      else:
        self.AddParam("in", *arg)
  
  def AddOutputs(self, *args):
    """Adds a list of output parameters."""
    if len(args) == 1 and isinstance(args[0], list):
      args = args[0]
    for arg in args:
      if isinstance(arg, str):
        self.AddParam("out", arg)
      else:
        self.AddParam("out", *arg)
  
  def AddNewTextureStage(self, type = Texture.TT2dTexture):
    """Adds a new texture input to Fragment and returns a two-tuple with
    the texnum and new TextureStage."""
    ts = TextureStage("tex_%d" % self.__curTex)
    if type == Texture.TT1dTexture:   type = "sampler1D"
    elif type == Texture.TT2dTexture: type = "sampler2D"
    elif type == Texture.TT3dTexture: type = "sampler2D"
    elif type == Texture.TTCubeMap:   type = "samplerCUBE"
    if not (isinstance(type, str) and type.startswith("sampler")):
      raise TypeError, "Unknown texture type %s!" % str(type)
    self.AddInput("tex_%d" % self.__curTex, "uniform " + type, "TEXUNIT%d" % self.__curTex)
    self.__curTex += 1
    ts.setSort(self.__curTex)
    return self.__curTex - 1, ts
  
  def __iadd__(self, code):
    """Appends shader code to the shader body."""
    if isinstance(code, VShaderProgram):
      code = code.Body
    assert isinstance(code, str)
    code = code.strip().split("\n")
    for line in code:
      if self.Body == "":
        self.Body += line.strip()
      else:
        self.Body += "\n" + line.strip()
    return self

class VShader:
  """A Shader with both Vertex and Fragment programs."""
  def __init__(self):
    self.Vertex = VShaderProgram("vshader")
    self.Fragment = VShaderProgram("fshader")
  
  def Write(self):
    """Returns the shader code as string."""
    sha = "//Cg\n"
    sha += self.Vertex.Write()
    sha += "\n"
    sha += self.Fragment.Write()
    return sha
  
  def Make(self):
    """Makes a new shader object."""
    return Shader.make(self.Write())
  
  def AddNewTextureStage(self, type = Texture.TT2dTexture):
    """Adds a new texture input to Fragment and returns a two-tuple with
    the texnum and new TextureStage."""
    return self.Fragment.AddNewTextureStage(type)
