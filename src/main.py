__all__ = []

if __name__ == "__main__":
  # Global initialization
  USE_GUI = "dgui"
  
  if USE_GUI == "dgui":
    from dgui.pConfig import Config
  elif USE_GUI == "wxgui":
    from wxgui.pConfig import Config
  
  from direct.showbase.ShowBase import ShowBase
  ShowBase()
  
  if USE_GUI == "dgui":
    # Reto, add the start code here
    pass
  elif USE_GUI == "wxgui":
    from wxgui.pEditorApp import EditorApp
    app = EditorApp()
  
  run()

