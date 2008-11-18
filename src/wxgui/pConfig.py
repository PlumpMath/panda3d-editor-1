__all__ = ["Config"]

from core.pConfig import Config as BaseConfig

class Config(BaseConfig):
  @classmethod
  def loadConfig(self):
    # Load the global settings first.
    BaseConfig.loadConfig()
    
    # Then add our own vars.
    self.loadPrcFileData("window-type none")
    self.loadPrcFileData("client-sleep 0.01")
    self.loadPrcFileData("want-wx #f") # Sic, false

