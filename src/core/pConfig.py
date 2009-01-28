__all__ = ["Config"]

# Don't import this file directly, import from the pConfig.py files in the individual dirs instead.

from pandac.PandaModules import loadPrcFileData, Filename
import os, sys
DATADIR = Filename.fromOsSpecific(os.path.join(os.path.abspath(sys.argv[0]), "..", "..", "data")).getFullpath()

class Config:
  @classmethod
  def loadPrcFileData(self, cpage):
    loadPrcFileData("editor-config", cpage)
  
  @classmethod
  def loadConfig(self):
    loadPrcFileData("editor-startup", "window-type none") # Sic, this gets done in pWindow.py
    loadPrcFileData("editor-startup", "model-path %s" % DATADIR)
    loadPrcFileData("editor-startup", "basic-shaders-only #f")
    loadPrcFileData("editor-startup", "win-size 1024 768")
    #loadPrcFileData("editor-startup", "win-size 1024 768")

