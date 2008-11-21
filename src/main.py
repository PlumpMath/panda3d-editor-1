__all__ = []

if __name__ == "__main__":
  # Whether to load dgui or wxgui.
  USE_GUI = "dgui"
  
  # First phase: load the configurations.
  if USE_GUI == "dgui":
    from dgui.pConfig import Config
  elif USE_GUI == "wxgui":
    from wxgui.pConfig import Config
  Config.loadConfig()
  
  # Second phase: initialize the window manager (which starts ShowBase)
  from core.pWindow import WindowManager
  if USE_GUI == "dgui":
    WindowManager.startBase(showDefaultWindow = True, allowMultipleWindows = False)
  elif USE_GUI == "wxgui":
    WindowManager.startBase(showDefaultWindow = False, allowMultipleWindows = True)
  
  # Third phase: load up the core of the editor.
  from core.pMain import EditorClass
  editor = EditorClass(render)
  editor.loadEggModelsFile("testModelsFile.egg")
  
  # Fourth phase: load one of the two interface layers.
  if USE_GUI == "dgui":
    from dgui.pEditorApp import EditorApp
    app = EditorApp(editor)
    app.toggle(True)
  elif USE_GUI == "wxgui":
    # wxgui needs to be opened before the editor, as it opens the window later
    from wxgui.pEditorApp import EditorApp
    app = EditorApp(editor)
  
  # Now, get it running :)
  editor.toggle(True)
  run()

