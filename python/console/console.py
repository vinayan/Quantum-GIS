# -*- coding:utf-8 -*-
"""
/***************************************************************************
Python Conosle for QGIS
                             -------------------
begin                : 2012-09-10
copyright            : (C) 2012 by Salvatore Larosa
email                : lrssvtml (at) gmail (dot) com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
Some portions of code were taken from https://code.google.com/p/pydee/
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.utils import iface
from console_sci import ShellScintilla
from console_output import ShellOutputScintilla
from console_editor import EditorTabWidget
from console_help import HelpDialog
from console_settings import optionsDialog
from qgis.core import QgsApplication

import sys
import os

_console = None

def show_console():
  """ called from QGIS to open the console """
  global _console
  if _console is None:
    parent = iface.mainWindow() if iface else None
    _console = PythonConsole( parent )
    _console.show() # force show even if it was restored as hidden
    # set focus to the console so the user can start typing
    # defer the set focus event so it works also whether the console not visible yet
    QTimer.singleShot(0, _console.activate)
  else:
    _console.setVisible(not _console.isVisible())
    # set focus to the console so the user can start typing
    if _console.isVisible():
      _console.activate()

_old_stdout = sys.stdout
_console_output = None

# hook for python console so all output will be redirected
# and then shown in console
def console_displayhook(obj):
    global _console_output
    _console_output = obj

class PythonConsole(QDockWidget):
    def __init__(self, parent=None):
        QDockWidget.__init__(self, parent)
        self.setObjectName("PythonConsole")
        self.setWindowTitle(QCoreApplication.translate("PythonConsole", "Python Console"))
        #self.setAllowedAreas(Qt.BottomDockWidgetArea)

        self.console = PythonConsoleWidget(self)
        self.setWidget( self.console )
        self.setFocusProxy( self.console )

        # try to restore position from stored main window state
        if iface and not iface.mainWindow().restoreDockWidget(self):
            iface.mainWindow().addDockWidget(Qt.BottomDockWidgetArea, self)

    def activate(self):
        self.activateWindow()
        self.raise_()
        QDockWidget.setFocus(self)

    def closeEvent(self, event):
        self.console.saveSettingsConsole()
        QWidget.closeEvent(self, event)

class PythonConsoleWidget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.setWindowTitle(QCoreApplication.translate("PythonConsole", "Python Console"))

        self.options = optionsDialog(self)
        self.helpDlg = HelpDialog(self)

        self.shell = ShellScintilla(self)
        self.setFocusProxy(self.shell)
        self.shellOut = ShellOutputScintilla(self)
        self.tabEditorWidget = EditorTabWidget(self)

        ##------------ UI -------------------------------

        self.splitterEditor = QSplitter(self)
        self.splitterEditor.setOrientation(Qt.Horizontal)
        self.splitterEditor.setHandleWidth(6)
        self.splitterEditor.setChildrenCollapsible(True)
        self.splitter = QSplitter(self.splitterEditor)
        self.splitter.setOrientation(Qt.Vertical)
        self.splitter.setHandleWidth(3)
        self.splitter.setChildrenCollapsible(False)
        self.splitter.addWidget(self.shellOut)
        self.splitter.addWidget(self.shell)
        #self.splitterEditor.addWidget(self.tabEditorWidget)
        
        self.splitterObj = QSplitter(self.splitterEditor)
        self.splitterObj.setHandleWidth(3)
        self.splitterObj.setOrientation(Qt.Horizontal)
        #self.splitterObj.setSizes([0, 0])
        #self.splitterObj.setStretchFactor(0, 1)
        
        self.widgetEditor = QWidget(self.splitterObj)
        
        self.listClassMethod = QTreeWidget(self.splitterObj)
        self.listClassMethod.setColumnCount(2)
        self.listClassMethod.setHeaderLabels(['Object', 'Line'])
        self.listClassMethod.setColumnHidden(1, True)
        self.listClassMethod.setAlternatingRowColors(True)

        
        #self.splitterEditor.addWidget(self.widgetEditor)
        #self.splitterObj.addWidget(self.listClassMethod)
        #self.splitterObj.addWidget(self.widgetEditor)

        # Hide side editor on start up
        self.splitterObj.hide()
        self.listClassMethod.hide()

        sizes = self.splitter.sizes()
        self.splitter.setSizes(sizes)

        ##----------------Restore Settings------------------------------------

        self.restoreSettingsConsole()

        ##------------------Toolbar Editor-------------------------------------

        ## Action for Open File
        openFileBt = QCoreApplication.translate("PythonConsole", "Open file")
        self.openFileButton = QAction(parent)
        self.openFileButton.setCheckable(False)
        self.openFileButton.setEnabled(True)
        self.openFileButton.setIcon(QgsApplication.getThemeIcon("console/iconOpenConsole.png"))
        self.openFileButton.setMenuRole(QAction.PreferencesRole)
        self.openFileButton.setIconVisibleInMenu(True)
        self.openFileButton.setToolTip(openFileBt)
        self.openFileButton.setText(openFileBt)
        ## Action for Save File
        saveFileBt = QCoreApplication.translate("PythonConsole", "Save")
        self.saveFileButton = QAction(parent)
        self.saveFileButton.setCheckable(False)
        self.saveFileButton.setEnabled(True)
        self.saveFileButton.setIcon(QgsApplication.getThemeIcon("console/iconSaveConsole.png"))
        self.saveFileButton.setMenuRole(QAction.PreferencesRole)
        self.saveFileButton.setIconVisibleInMenu(True)
        self.saveFileButton.setToolTip(saveFileBt)
        self.saveFileButton.setText(saveFileBt)
        ## Action for Save File As
        saveAsFileBt = QCoreApplication.translate("PythonConsole", "Save As..")
        self.saveAsFileButton = QAction(parent)
        self.saveAsFileButton.setCheckable(False)
        self.saveAsFileButton.setEnabled(True)
        self.saveAsFileButton.setIcon(QgsApplication.getThemeIcon("console/iconSaveAsConsole.png"))
        self.saveAsFileButton.setMenuRole(QAction.PreferencesRole)
        self.saveAsFileButton.setIconVisibleInMenu(True)
        self.saveAsFileButton.setToolTip(saveAsFileBt)
        self.saveAsFileButton.setText(saveAsFileBt)
        ## Action Cut
        cutEditorBt = QCoreApplication.translate("PythonConsole", "Cut")
        self.cutEditorButton = QAction(parent)
        self.cutEditorButton.setCheckable(False)
        self.cutEditorButton.setEnabled(True)
        self.cutEditorButton.setIcon(QgsApplication.getThemeIcon("console/iconCutEditorConsole.png"))
        self.cutEditorButton.setMenuRole(QAction.PreferencesRole)
        self.cutEditorButton.setIconVisibleInMenu(True)
        self.cutEditorButton.setToolTip(cutEditorBt)
        self.cutEditorButton.setText(cutEditorBt)
        ## Action Copy
        copyEditorBt = QCoreApplication.translate("PythonConsole", "Copy")
        self.copyEditorButton = QAction(parent)
        self.copyEditorButton.setCheckable(False)
        self.copyEditorButton.setEnabled(True)
        self.copyEditorButton.setIcon(QgsApplication.getThemeIcon("console/iconCopyEditorConsole.png"))
        self.copyEditorButton.setMenuRole(QAction.PreferencesRole)
        self.copyEditorButton.setIconVisibleInMenu(True)
        self.copyEditorButton.setToolTip(copyEditorBt)
        self.copyEditorButton.setText(copyEditorBt)
        ## Action Paste
        pasteEditorBt = QCoreApplication.translate("PythonConsole", "Paste")
        self.pasteEditorButton = QAction(parent)
        self.pasteEditorButton.setCheckable(False)
        self.pasteEditorButton.setEnabled(True)
        self.pasteEditorButton.setIcon(QgsApplication.getThemeIcon("console/iconPasteEditorConsole.png"))
        self.pasteEditorButton.setMenuRole(QAction.PreferencesRole)
        self.pasteEditorButton.setIconVisibleInMenu(True)
        self.pasteEditorButton.setToolTip(pasteEditorBt)
        self.pasteEditorButton.setText(pasteEditorBt)
        ## Action Run Script (subprocess)
        runScriptEditorBt = QCoreApplication.translate("PythonConsole", "Run script")
        self.runScriptEditorButton = QAction(parent)
        self.runScriptEditorButton.setCheckable(False)
        self.runScriptEditorButton.setEnabled(True)
        self.runScriptEditorButton.setIcon(QgsApplication.getThemeIcon("console/iconRunScriptConsole.png"))
        self.runScriptEditorButton.setMenuRole(QAction.PreferencesRole)
        self.runScriptEditorButton.setIconVisibleInMenu(True)
        self.runScriptEditorButton.setToolTip(runScriptEditorBt)
        self.runScriptEditorButton.setText(runScriptEditorBt)
        ## Action Run Script (subprocess)
        commentEditorBt = QCoreApplication.translate("PythonConsole", "Comment code")
        self.commentEditorButton = QAction(parent)
        self.commentEditorButton.setCheckable(False)
        self.commentEditorButton.setEnabled(True)
        self.commentEditorButton.setIcon(QgsApplication.getThemeIcon("console/iconCommentEditorConsole.png"))
        self.commentEditorButton.setMenuRole(QAction.PreferencesRole)
        self.commentEditorButton.setIconVisibleInMenu(True)
        self.commentEditorButton.setToolTip(commentEditorBt)
        self.commentEditorButton.setText(commentEditorBt)
        ## Action Run Script (subprocess)
        uncommentEditorBt = QCoreApplication.translate("PythonConsole", "Uncomment code")
        self.uncommentEditorButton = QAction(parent)
        self.uncommentEditorButton.setCheckable(False)
        self.uncommentEditorButton.setEnabled(True)
        self.uncommentEditorButton.setIcon(QgsApplication.getThemeIcon("console/iconUncommentEditorConsole.png"))
        self.uncommentEditorButton.setMenuRole(QAction.PreferencesRole)
        self.uncommentEditorButton.setIconVisibleInMenu(True)
        self.uncommentEditorButton.setToolTip(uncommentEditorBt)
        self.uncommentEditorButton.setText(uncommentEditorBt)
        ## Action for Object browser
        objList = QCoreApplication.translate("PythonConsole", "Object browser")
        self.objectListButton = QAction(parent)
        self.objectListButton.setCheckable(True)
        self.objectListButton.setEnabled(True)
        self.objectListButton.setIcon(QgsApplication.getThemeIcon("console/iconClassBrowserConsole.png"))
        self.objectListButton.setMenuRole(QAction.PreferencesRole)
        self.objectListButton.setIconVisibleInMenu(True)
        self.objectListButton.setToolTip(objList)
        self.objectListButton.setText(objList)

        ##----------------Toolbar Console-------------------------------------

        ## Action Show Editor
        showEditor = QCoreApplication.translate("PythonConsole", "Show editor")
        self.showEditorButton = QAction(parent)
        self.showEditorButton.setEnabled(True)
        self.showEditorButton.setCheckable(True)
        self.showEditorButton.setIcon(QgsApplication.getThemeIcon("console/iconShowEditorConsole.png"))
        self.showEditorButton.setMenuRole(QAction.PreferencesRole)
        self.showEditorButton.setIconVisibleInMenu(True)
        self.showEditorButton.setToolTip(showEditor)
        self.showEditorButton.setText(showEditor)
        ## Action for Clear button
        clearBt = QCoreApplication.translate("PythonConsole", "Clear console")
        self.clearButton = QAction(parent)
        self.clearButton.setCheckable(False)
        self.clearButton.setEnabled(True)
        self.clearButton.setIcon(QgsApplication.getThemeIcon("console/iconClearConsole.png"))
        self.clearButton.setMenuRole(QAction.PreferencesRole)
        self.clearButton.setIconVisibleInMenu(True)
        self.clearButton.setToolTip(clearBt)
        self.clearButton.setText(clearBt)
        ## Action for settings
        optionsBt = QCoreApplication.translate("PythonConsole", "Settings")
        self.optionsButton = QAction(parent)
        self.optionsButton.setCheckable(False)
        self.optionsButton.setEnabled(True)
        self.optionsButton.setIcon(QgsApplication.getThemeIcon("console/iconSettingsConsole.png"))
        self.optionsButton.setMenuRole(QAction.PreferencesRole)
        self.optionsButton.setIconVisibleInMenu(True)
        self.optionsButton.setToolTip(optionsBt)
        self.optionsButton.setText(optionsBt)
        ## Action menu for class
        actionClassBt = QCoreApplication.translate("PythonConsole", "Import Class")
        self.actionClass = QAction(parent)
        self.actionClass.setCheckable(False)
        self.actionClass.setEnabled(True)
        self.actionClass.setIcon(QgsApplication.getThemeIcon("console/iconClassConsole.png"))
        self.actionClass.setMenuRole(QAction.PreferencesRole)
        self.actionClass.setIconVisibleInMenu(True)
        self.actionClass.setToolTip(actionClassBt)
        self.actionClass.setText(actionClassBt)
        ## Import Sextante class
        loadSextanteBt = QCoreApplication.translate("PythonConsole", "Import Sextante class")
        self.loadSextanteButton = QAction(parent)
        self.loadSextanteButton.setCheckable(False)
        self.loadSextanteButton.setEnabled(True)
        self.loadSextanteButton.setIcon(QgsApplication.getThemeIcon("console/iconSextanteConsole.png"))
        self.loadSextanteButton.setMenuRole(QAction.PreferencesRole)
        self.loadSextanteButton.setIconVisibleInMenu(True)
        self.loadSextanteButton.setToolTip(loadSextanteBt)
        self.loadSextanteButton.setText(loadSextanteBt)
        ## Import QtCore class
        loadQtCoreBt = QCoreApplication.translate("PythonConsole", "Import PyQt.QtCore class")
        self.loadQtCoreButton = QAction(parent)
        self.loadQtCoreButton.setCheckable(False)
        self.loadQtCoreButton.setEnabled(True)
        self.loadQtCoreButton.setIcon(QgsApplication.getThemeIcon("console/iconQtCoreConsole.png"))
        self.loadQtCoreButton.setMenuRole(QAction.PreferencesRole)
        self.loadQtCoreButton.setIconVisibleInMenu(True)
        self.loadQtCoreButton.setToolTip(loadQtCoreBt)
        self.loadQtCoreButton.setText(loadQtCoreBt)
        ## Import QtGui class
        loadQtGuiBt = QCoreApplication.translate("PythonConsole", "Import PyQt.QtGui class")
        self.loadQtGuiButton = QAction(parent)
        self.loadQtGuiButton.setCheckable(False)
        self.loadQtGuiButton.setEnabled(True)
        self.loadQtGuiButton.setIcon(QgsApplication.getThemeIcon("console/iconQtGuiConsole.png"))
        self.loadQtGuiButton.setMenuRole(QAction.PreferencesRole)
        self.loadQtGuiButton.setIconVisibleInMenu(True)
        self.loadQtGuiButton.setToolTip(loadQtGuiBt)
        self.loadQtGuiButton.setText(loadQtGuiBt)
        ## Action for Run script
        runBt = QCoreApplication.translate("PythonConsole", "Run command")
        self.runButton = QAction(parent)
        self.runButton.setCheckable(False)
        self.runButton.setEnabled(True)
        self.runButton.setIcon(QgsApplication.getThemeIcon("console/iconRunConsole.png"))
        self.runButton.setMenuRole(QAction.PreferencesRole)
        self.runButton.setIconVisibleInMenu(True)
        self.runButton.setToolTip(runBt)
        self.runButton.setText(runBt)
        ## Help action
        helpBt = QCoreApplication.translate("PythonConsole", "Help")
        self.helpButton = QAction(parent)
        self.helpButton.setCheckable(False)
        self.helpButton.setEnabled(True)
        self.helpButton.setIcon(QgsApplication.getThemeIcon("console/iconHelpConsole.png"))
        self.helpButton.setMenuRole(QAction.PreferencesRole)
        self.helpButton.setIconVisibleInMenu(True)
        self.helpButton.setToolTip(helpBt)
        self.helpButton.setText(helpBt)

        self.toolBar = QToolBar()
        self.toolBar.setEnabled(True)
        self.toolBar.setFocusPolicy(Qt.NoFocus)
        self.toolBar.setContextMenuPolicy(Qt.DefaultContextMenu)
        self.toolBar.setLayoutDirection(Qt.LeftToRight)
        self.toolBar.setIconSize(QSize(24, 24))
        self.toolBar.setOrientation(Qt.Vertical)
        self.toolBar.setMovable(True)
        self.toolBar.setFloatable(True)
        self.toolBar.addAction(self.clearButton)
        self.toolBar.addAction(self.actionClass)
        self.toolBar.addAction(self.runButton)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.showEditorButton)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.optionsButton)
        self.toolBar.addAction(self.helpButton)

        if sys.platform.startswith('win'):
            bkgrcolor = ['170', '170', '170']
            bordercl = ['125', '125', '125']
        else:
            bkgrcolor = ['200', '200', '200']
            bordercl = ['155', '155', '155']

        self.toolBarEditor = QToolBar()
        self.toolBarEditor.setStyleSheet('QToolBar{background-color: rgb(%s, %s, %s' % tuple(bkgrcolor) + ');\
                                          border-right: 1px solid rgb(%s, %s, %s' % tuple(bordercl) + ');}')
        self.toolBarEditor.setEnabled(False)
        self.toolBarEditor.setFocusPolicy(Qt.NoFocus)
        self.toolBarEditor.setContextMenuPolicy(Qt.DefaultContextMenu)
        self.toolBarEditor.setLayoutDirection(Qt.LeftToRight)
        self.toolBarEditor.setIconSize(QSize(18, 18))
        self.toolBarEditor.setOrientation(Qt.Vertical)
        self.toolBarEditor.setMovable(True)
        self.toolBarEditor.setFloatable(True)
        self.toolBarEditor.addAction(self.openFileButton)
        self.toolBarEditor.addSeparator()
        self.toolBarEditor.addAction(self.saveFileButton)
        self.toolBarEditor.addAction(self.saveAsFileButton)
        self.toolBarEditor.addSeparator()
        self.toolBarEditor.addAction(self.cutEditorButton)
        self.toolBarEditor.addAction(self.copyEditorButton)
        self.toolBarEditor.addAction(self.pasteEditorButton)
        self.toolBarEditor.addSeparator()
        self.toolBarEditor.addAction(self.commentEditorButton)
        self.toolBarEditor.addAction(self.uncommentEditorButton)
        self.toolBarEditor.addSeparator()
        self.toolBarEditor.addAction(self.objectListButton)
        self.toolBarEditor.addSeparator()
        self.toolBarEditor.addAction(self.runScriptEditorButton)

        ## Menu Import Class
        self.classMenu = QMenu(self)
        self.classMenu.addAction(self.loadSextanteButton)
        self.classMenu.addAction(self.loadQtCoreButton)
        self.classMenu.addAction(self.loadQtGuiButton)
        cM = self.toolBar.widgetForAction(self.actionClass)
        cM.setMenu(self.classMenu)
        cM.setPopupMode(QToolButton.InstantPopup)

        self.widgetButton = QWidget()
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.widgetButton.sizePolicy().hasHeightForWidth())
        self.widgetButton.setSizePolicy(sizePolicy)

        self.widgetButtonEditor = QWidget(self.widgetEditor)
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.widgetButtonEditor.sizePolicy().hasHeightForWidth())
        self.widgetButtonEditor.setSizePolicy(sizePolicy)

        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.shellOut.sizePolicy().hasHeightForWidth())
        self.shellOut.setSizePolicy(sizePolicy)

        self.shellOut.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.shell.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        ##------------ Layout -------------------------------

        self.mainLayout = QGridLayout(self)
        self.mainLayout.setMargin(0)
        self.mainLayout.setSpacing(0)
        self.mainLayout.addWidget(self.widgetButton, 0, 0, 1, 1)
        self.mainLayout.addWidget(self.splitterEditor, 0, 1, 1, 1)

        self.layoutEditor = QGridLayout(self.widgetEditor)
        self.layoutEditor.setMargin(0)
        self.layoutEditor.setSpacing(0)
        self.layoutEditor.addWidget(self.widgetButtonEditor, 0, 0, 1, 1)
        self.layoutEditor.addWidget(self.tabEditorWidget, 0, 1, 1, 1)

        self.toolBarLayout = QGridLayout(self.widgetButton)
        self.toolBarLayout.setMargin(0)
        self.toolBarLayout.setSpacing(0)
        self.toolBarLayout.addWidget(self.toolBar)
        self.toolBarEditorLayout = QGridLayout(self.widgetButtonEditor)
        self.toolBarEditorLayout.setMargin(0)
        self.toolBarEditorLayout.setSpacing(0)
        self.toolBarEditorLayout.addWidget(self.toolBarEditor)

        ##------------ Add first Tab in Editor -------------------------------

        #self.tabEditorWidget.newTabEditor(tabName='first', filename=None)

        ##------------ Signal -------------------------------

        self.objectListButton.toggled.connect(self.toggleObjectListWidget)
        self.commentEditorButton.triggered.connect(self.commentCode)
        self.uncommentEditorButton.triggered.connect(self.uncommentCode)
        self.runScriptEditorButton.triggered.connect(self.runScriptEditor)
        self.cutEditorButton.triggered.connect(self.cutEditor)
        self.copyEditorButton.triggered.connect(self.copyEditor)
        self.pasteEditorButton.triggered.connect(self.pasteEditor)
        self.showEditorButton.toggled.connect(self.toggleEditor)
        self.clearButton.triggered.connect(self.shellOut.clearConsole)
        self.optionsButton.triggered.connect(self.openSettings)
        self.loadSextanteButton.triggered.connect(self.sextante)
        self.loadQtCoreButton.triggered.connect(self.qtCore)
        self.loadQtGuiButton.triggered.connect(self.qtGui)
        self.runButton.triggered.connect(self.shell.entered)
        self.openFileButton.triggered.connect(self.openScriptFile)
        self.saveFileButton.triggered.connect(self.saveScriptFile)
        self.saveAsFileButton.triggered.connect(self.saveAsScriptFile)
        self.helpButton.triggered.connect(self.openHelp)
        self.connect(self.options.buttonBox, SIGNAL("accepted()"),
                     self.prefChanged)
        self.connect(self.listClassMethod, SIGNAL('itemClicked(QTreeWidgetItem*, int)'),
                     self.onClickGoToLine)

    def onClickGoToLine(self, item, column):
        linenr = int(item.text(1))
        itemName = str(item.text(0))
        charPos = itemName.find(' ')
        if charPos != -1:
            objName = itemName[0:charPos]
        else:
            objName = itemName
        self.tabEditorWidget.currentWidget().newEditor.goToLine(objName, linenr)

    def sextante(self):
       self.shell.commandConsole('sextante')

    def qtCore(self):
       self.shell.commandConsole('qtCore')

    def qtGui(self):
       self.shell.commandConsole('qtGui')

    def toggleEditor(self, checked):
        self.splitterObj.show() if checked else self.splitterObj.hide()
        self.tabEditorWidget.enableToolBarEditor(checked)

    def toggleObjectListWidget(self, checked):
        self.listClassMethod.show() if checked else self.listClassMethod.hide()

    def pasteEditor(self):
        self.tabEditorWidget.currentWidget().newEditor.paste()

    def cutEditor(self):
        self.tabEditorWidget.currentWidget().newEditor.cut()

    def copyEditor(self):
        self.tabEditorWidget.currentWidget().newEditor.copy()

    def runScriptEditor(self):
        self.tabEditorWidget.currentWidget().newEditor.runScriptCode()

    def commentCode(self):
        self.tabEditorWidget.currentWidget().newEditor.commentEditorCode(True)

    def uncommentCode(self):
        self.tabEditorWidget.currentWidget().newEditor.commentEditorCode(False)

#    def openScriptFile(self):
#       settings = QSettings()
#       lastDirPath = settings.value("pythonConsole/lastDirPath").toString()
#       scriptFile = QFileDialog.getOpenFileName(
#                       self, "Open File", lastDirPath, "Script file (*.py)")
#       if scriptFile.isEmpty() == False:
#           oF = open(scriptFile, 'r')
#           listScriptFile = []
#           for line in oF:
#               if line != "\n":
#                   listScriptFile.append(line)
#           self.shell.insertTextFromFile(listScriptFile)
#    
#           lastDirPath = QFileInfo(scriptFile).path()
#           settings.setValue("pythonConsole/lastDirPath", QVariant(scriptFile))
#
#
#    def saveScriptFile(self):
#        scriptFile = QFileDialog()
#        scriptFile.setDefaultSuffix(".py")
#        fName = scriptFile.getSaveFileName(
#                        self, "Save file", QString(), "Script file (*.py)")
#    
#        if fName.isEmpty() == False:
#            filename = str(fName)
#            if not filename.endswith(".py"):
#                fName += ".py"
#            sF = open(fName,'w')
#            listText = self.shellOut.getTextFromEditor()
#            is_first_line = True
#            for s in listText:
#                if s[0:3] in (">>>", "..."):
#                    s.replace(">>> ", "").replace("... ", "")
#                    if is_first_line:
#                        is_first_line = False
#                    else:
#                        sF.write('\n')
#                    sF.write(s)
#            sF.close()
#            self.callWidgetMessageBar('Script was correctly saved.')

    def openScriptFile(self):
        settings = QSettings()
        lastDirPath = settings.value("pythonConsole/lastDirPath").toString()
        filename = QFileDialog.getOpenFileName(
                        self, "Open File", lastDirPath, "Script file (*.py)")
        if not filename.isEmpty():
            for i in range(self.tabEditorWidget.count()):
                tabWidget = self.tabEditorWidget.widget(i)
                if tabWidget.path == filename:
                    self.tabEditorWidget.setCurrentWidget(tabWidget)
                    break
            else:
                tabName = filename.split('/')[-1]
                self.tabEditorWidget.newTabEditor(tabName, filename)

        lastDirPath = QFileInfo(filename).path()
        settings.setValue("pythonConsole/lastDirPath", QVariant(filename))
        self.tabListScript.append(filename)
        self.updateTabListScript(script=None)

    def saveScriptFile(self):
        tabWidget = self.tabEditorWidget.currentWidget()
        try:
            tabWidget.save()
        except (IOError, OSError), e:
            QMessageBox.warning(self, "Save Error",
                    "Failed to save %s: %s" % (tabWidget.path, e))

    def saveAsScriptFile(self):
        tabWidget = self.tabEditorWidget.currentWidget()
        if tabWidget is None:
            return
        filename = QFileDialog.getSaveFileName(self,
                        "Save File As",
                        tabWidget.path, "Script file (*.py)")
        if not filename.isEmpty():
            #print tabWidget.path
            self.tabListScript.remove(unicode(tabWidget.path))
            tabWidget.path = filename
            self.saveScriptFile()

    def openHelp(self):
        self.helpDlg.show()
        self.helpDlg.activateWindow()

    def openSettings(self):
        self.options.exec_()

    def prefChanged(self):
        self.shell.settingsShell()
        self.shellOut.refreshLexerProperties()
        self.tabEditorWidget.refreshSettingsEditor()

    def callWidgetMessageBar(self, text):
        self.shellOut.widgetMessageBar(iface, text)

    def callWidgetMessageBarEditor(self, text):
        self.tabEditorWidget.widgetMessageBar(iface, text)

    def updateTabListScript(self, script, action=None): 
        if script != '':
            settings = QSettings()
            if script == 'empty':
                self.tabListScript = []
            if script is not None and not action and script != 'empty':
                self.tabListScript.remove(script)
            if action:
                if script not in self.tabListScript:
                    self.tabListScript.append(script)
            settings.setValue("pythonConsole/tabScripts",
                                   QVariant(self.tabListScript))

    def saveSettingsConsole(self):
        settings = QSettings()
        #settings.setValue("pythonConsole/geometry", self.saveGeometry())
        settings.setValue("pythonConsole/splitterObj", self.splitterObj.saveState())
        settings.setValue("pythonConsole/splitterEditor", self.splitterEditor.saveState())

        self.shell.writeHistoryFile()

    def restoreSettingsConsole(self):
        # List for tab script
        settings = QSettings()
        storedTabScripts = settings.value("pythonConsole/tabScripts")
        self.tabListScript = storedTabScripts.toList()
        #self.restoreGeometry(settings.value("pythonConsole/geometry").toByteArray())
        self.splitterEditor.restoreState(settings.value("pythonConsole/splitterEditor").toByteArray())
        self.splitterObj.restoreState(settings.value("pythonConsole/splitterObj").toByteArray())

if __name__ == '__main__':
    a = QApplication(sys.argv)
    console = PythonConsoleWidget()
    console.show()
    a.exec_()
