__all__ = ["Config"]

from core.pConfig import Config as BaseConfig

class Config(BaseConfig):
  @classmethod
  def loadConfig(self):
    # Load the global settings first.
    BaseConfig.loadConfig()
    
    # Then add our own vars.
    self.loadPrcFileData("direct-gui-edit #f")

