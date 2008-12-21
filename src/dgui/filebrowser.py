#!/usr/bin/env python

#########################################################
# Author:  Geri Schneider Winters
# Panda3D-1.3.2
# May 19, 2007
#
# Sample Basic File Browser using Panda3D and Python
#
#########################################################

from pandac.PandaModules import TextNode
from direct.showbase import DirectObject
from direct.gui.OnscreenText import OnscreenText 
from direct.gui.DirectGui import *
import os
from os.path import join

class FileBrowser(DirectObject.DirectObject):

   def __init__(self):


      self.dot = os.getcwd()     # this is part of the file browser, and shows the
                                 # last directory where we opened or saved a file
                                 # initialize to cwd, then update it whenever a
                                 # person saves or opens a file

      self.prevdir = os.getcwd()

      self.selectedFile = ' '

      self.browserCreated = False
      self.browser = None
      self.fileList = None
      self.namebox = None


##################################################################################
#callback functions
 

   def dirbuttonpushed(self, name, dirpath):
      self.selectedFile = ' '
      self.namebox.enterText('')
      self.cleanCanvas()
      self.dot = os.path.join(dirpath,name)
      self.createFileList (self.dot)

   def filebuttonpushed(self, name, dirpath):
      self.selectedFile = os.path.join(dirpath, name)
      self.dot = dirpath
      self.namebox.enterText(name)

   def upSelected(self):
      self.selectedFile = ' '
      self.namebox.enterText('')
      self.cleanCanvas()
      self.dot = os.path.dirname(self.dot)
      self.createFileList (self.dot)

   def entryCR (self, textentered):
      if os.path.isabs(textentered):
      # the person typed in an absolute path name
         words = os.path.split(textentered)
      else:
      # the person typed in a path relative to the displayed directory
         words = (self.dot, textentered)

      if os.path.isdir(os.path.join(words[0], words[1])):
         self.dirbuttonpushed (words[1], words[0])
      else:
         self.filebuttonpushed(words[1], words[0])
         self.openSelected()


   def openSelected(self):
      temp = self.namebox.get()
      if os.path.isabs(temp):
      # the person typed in an absolute path name
         words = os.path.split(temp)
      else:
      # the person typed in a path relative to the displayed directory
         words = (self.dot, temp)

      if os.path.isdir(os.path.join(words[0], words[1])):
         self.dirbuttonpushed (words[1], words[0])
      else:
         self.selectedFile = os.path.join (words[0], words[1])
         messenger.send('selectionMade', [self.selectedFile])
         self.closeFileBrowser()



   def cancelSelected(self):
      self.selectedFile = ' '
      self.dot = self.prevdir
      self.namebox.enterText('')
      messenger.send('selectionMade', [self.selectedFile])
      self.closeFileBrowser()

##################################################################################

   def showFileBrowser(self):
      self.browser.show()


   def closeFileBrowser(self):
      self.browser.hide()
      self.selectedFile = ' '
      self.namebox.enterText('')


   def openFileBrowser(self):
      self.prevdir = self.dot
      if self.browserCreated:
         self.showFileBrowser()
      else:
         self.createFileBrowser()

##################################################################################

   def cleanCanvas(self):
      canvas = self.fileList.getCanvas()
      kids = canvas.getChildren()
      for I in range (kids.getNumPaths()):
         temp = kids.getPath(I)
         if temp.getTag('mytype') == 'button':
            temp.removeNode()

##################################################################################

   def createFileList(self, mydir):

      canvas=self.fileList.getCanvas()
      for dirpath, dirnames, filenames in os.walk(mydir):
         nextPos = (-.93, 0.95)
         dirnames.sort()
         for name in dirnames:
            dirbutton = DirectButton (text=name, text_scale=(0.05, 0.05), text_align=TextNode.ALeft,
               frameSize=(-.95, .6, -.01, .037), frameColor=(0.9414,1.0,0.9414, 1.0), 
               relief=DGG.GROOVE, borderWidth=(0.003,0.003), 
               command=self.dirbuttonpushed, extraArgs=[name, dirpath])
            dirbutton.reparentTo (canvas)
            dirbutton.setPos(nextPos[0], 0, nextPos[1])
            dirbutton.setTag ('mytype', 'button')
            nextPos = (-.95, nextPos[1]-.06)

         filenames.sort()
         for name in filenames:
            filebutton = DirectButton (text=name, text_scale=(0.05, 0.05), text_align=TextNode.ALeft,
               frameSize=(-.95, .6, -.01, .037), frameColor=(1.0,0.9414,0.96,1.0), 
               relief=DGG.GROOVE, borderWidth=(0.003,0.003), 
               command=self.filebuttonpushed, extraArgs=[name, dirpath])
            filebutton.reparentTo (canvas)
            filebutton.setPos(nextPos[0], 0, nextPos[1])
            filebutton.setTag ('mytype', 'button')
            nextPos = (-.95, nextPos[1]-.06)
         break
      self.fileList['canvasSize'] = (-1, 0, nextPos[1], 1)


##################################################################################

   def createFileBrowser(self):

      self.browserCreated = True
# create the main browser window

      self.browser = DirectFrame (frameSize=(-0.6, 0.6, -0.8, 0.95), frameColor=(1.0,0.98,0.80,1.0),
         relief=DGG.GROOVE, borderWidth=(0.01,0.01))
      self.browser.setPos (-.7,0,0)


# add scrolling window frame

      self.fileList = DirectScrolledFrame(frameSize=(-0.55, 0.55, -0.4, 0.75), relief=DGG.GROOVE, 
         borderWidth=(0.01,0.01), frameColor=(1.0,1.0,1.0,1.0), 
         manageScrollBars=True, autoHideScrollBars=True, 
         canvasSize=(-1, 0, -10, 1))
      self.fileList.reparentTo(self.browser)

#add entry box
      self.namebox = DirectEntry(frameColor=(1.0,1.0,1.0,1.0), relief=DGG.GROOVE, 
         borderWidth=(0.01,0.01), text = "" ,scale=.05, width=18, command=self.entryCR,
         numLines = 1,focus=1)
      self.namebox.reparentTo (self.browser)
      self.namebox.setPos (-.35, 0, -.55)
      nameboxlabel = DirectLabel (text="File name:", text_scale=(0.05, 0.05), 
         frameColor=(1.0,0.98,0.80,1.0))
      nameboxlabel.reparentTo (self.browser)
      nameboxlabel.setPos (-.48, 0, -.55)

# add cancel button
      canbut = DirectButton(frameSize=(-0.11, 0.11, -0.05, 0.05),relief=DGG.RAISED, 
         borderWidth=(0.01,0.01), text="Cancel", text_pos=(0,-0.02), text_scale=(0.07, 0.07),
         command=self.cancelSelected)
      canbut.reparentTo(self.browser)
      canbut.setPos (-.25,0,-.7)

# add Open button
      openbut = DirectButton(frameSize=(-0.11, 0.11, -0.05, 0.05),relief=DGG.RAISED, 
         borderWidth=(0.01,0.01), text="Open", text_pos=(-0.01,-0.02), text_scale=(0.07, 0.07),
         command=self.openSelected)
      openbut.reparentTo(self.browser)
      openbut.setPos (.25,0,-.7)


# add Up button to go to parent directory
      upbut = DirectButton(frameSize=(-0.3, 0.3, -0.04, 0.04),relief=DGG.RAISED, 
         borderWidth=(0.01,0.01), text="Browse Up One Level", text_pos=(-0.01,-0.015), text_scale=(0.05, 0.05),
         command=self.upSelected)
      upbut.reparentTo(self.browser)
      upbut.setPos (0,0,.85)

      self.createFileList(self.dot)


# end class FileBrowser


FG = FileBrowser()


class Processor:

   def __init__(self):

      self.myButton = DirectButton (text='Click Here', text_scale=(0.1, 0.1),
         text_align=TextNode.ALeft, frameSize=(-.95,.6, -.1, 0.1),
         frameColor=(0.9414, 1.0, 0.9414, 1.0), relief=DGG.RAISED,
         borderWidth=(0.01,0.01), command=self.personClickedButton)
      self.myButton.setPos(0,0,0)

      FG.accept ('selectionMade', self.finishButtonClickAction)


   def personClickedButton (self):
      # assume you have a button somewhere for someone to click to save
      # their game. When they click that button, it calls this function
      # but you do not know what file to save the game into, so you
      # start up a browser and quit until the browser calls back with
      # a filename

      self.myButton.hide()
      FG.openFileBrowser()

   def finishButtonClickAction (self, filename):
      # at this point, the person has seen the file browser and has
      # either selected a file or canceled. In either case, filename
      # has the name that is returned from the browser, maybe ' '

      textmsg = 'Here is the file you selected: ' + filename
      message=OnscreenText(text=textmsg, pos=(0,0), scale=0.07)

