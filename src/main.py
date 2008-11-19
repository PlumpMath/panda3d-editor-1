__all__ = []

if __name__ == "__main__":
  # Global initialization
  USE_GUI = "wxgui"
  
  if USE_GUI == "dgui":
    from dgui.pConfig import Config
  elif USE_GUI == "wxgui":
    from wxgui.pConfig import Config
  Config.loadConfig()
  
  from direct.showbase.ShowBase import ShowBase
  ShowBase()
  
  from core.pMain import EditorClass
  editor = EditorClass( render )
  editor.loadEggModelsFile( 'testModelsFile.egg' )
  
  if USE_GUI == "dgui":
    from dgui.pEditorApp import EditorApp
    app = EditorApp( editor )
    app.toggle( True )
  # wxgui needs to be opened before the editor, as it open the window
  elif USE_GUI == "wxgui":
    from wxgui.pEditorApp import EditorApp
    app = EditorApp( editor )
  
  editor.toggle( True )
  
  run()

