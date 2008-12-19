__all__ = []

if __name__ == "__main__":
  # Whether to load dgui or wxgui.
  from optparse import OptionParser
  parser = OptionParser()
  parser.add_option("-d", "--dgui",  action="store_true", dest="usedgui",  default=False, help="use the DirectGUI editor interface")
  parser.add_option("-w", "--wxgui", action="store_true", dest="usewxgui", default=False, help="use the wxWidgets editor interface")
  parser.add_option("-n", "--nogui", action="store_true", dest="usenogui", default=False, help="don't use any editor interface")
  options = parser.parse_args()[0]
  USE_GUI = None
  if options.usewxgui:  USE_GUI = "wxgui"
  elif options.usedgui: USE_GUI = "dgui"
  print "I: main: using interface:", USE_GUI
  
  # First phase: load the configurations.
  if USE_GUI == "dgui":
    from dgui.pConfig import Config
  elif USE_GUI == "wxgui":
    from wxgui.pConfig import Config
  if USE_GUI is not None:
    Config.loadConfig()
  
  # Second phase: initialize the window manager (which starts ShowBase)
  from core.pWindow import WindowManager
  if USE_GUI == "dgui":
    WindowManager.startBase(showDefaultWindow = True, allowMultipleWindows = False)
  elif USE_GUI == "wxgui":
    WindowManager.startBase(showDefaultWindow = False, allowMultipleWindows = True)
  else:
    # mouse not working with this
    #WindowManager.startBase(showDefaultWindow = True, allowMultipleWindows = False)
    from direct.directbase import DirectStart
  
  # Third phase: load up the core of the editor.
  from core.pMain import EditorClass
  editor = EditorClass(render)
  editor.loadEggModelsFile("examples/save-1.egg")
  
  # Fourth phase: load one of the two interface layers.
  if USE_GUI == "dgui":
    from dgui.pEditorApp import EditorApp
    app = EditorApp(editor)
    app.toggle(True)
  elif USE_GUI == "wxgui":
    # wxGui needs to be opened before the editor, as it opens the window later
    from wxgui.pEditorApp import EditorApp
    app = EditorApp(editor)
  
  # Now, get it running :)
  if USE_GUI == "dgui":
    editor.toggle(True)
  
  run()
