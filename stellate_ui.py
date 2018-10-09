# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'stellate.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1600, 849)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(0, 0, 1600, 900))
        self.tabWidget.setObjectName("tabWidget")
        self.tabViewer = QtWidgets.QWidget()
        self.tabViewer.setObjectName("tabViewer")
        self.openGLWidget = QtWidgets.QOpenGLWidget(self.tabViewer)
        self.openGLWidget.setGeometry(QtCore.QRect(10, 10, 1333, 750))
        self.openGLWidget.setObjectName("openGLWidget")
        self.pushButton = QtWidgets.QPushButton(self.tabViewer)
        self.pushButton.setGeometry(QtCore.QRect(1360, 10, 221, 61))
        self.pushButton.setCheckable(True)
        self.pushButton.setDefault(False)
        self.pushButton.setFlat(False)
        self.pushButton.setObjectName("pushButton")
        self.tabWidget.addTab(self.tabViewer, "")
        self.tabStacker = QtWidgets.QWidget()
        self.tabStacker.setObjectName("tabStacker")
        self.tabWidget.addTab(self.tabStacker, "")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1600, 22))
        self.menubar.setDefaultUp(False)
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionSave_FITS = QtWidgets.QAction(MainWindow)
        self.actionSave_FITS.setObjectName("actionSave_FITS")
        self.actionOpen_FITS = QtWidgets.QAction(MainWindow)
        self.actionOpen_FITS.setObjectName("actionOpen_FITS")
        self.actionClose = QtWidgets.QAction(MainWindow)
        self.actionClose.setObjectName("actionClose")
        self.menuFile.addAction(self.actionOpen_FITS)
        self.menuFile.addAction(self.actionSave_FITS)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionClose)
        self.menubar.addAction(self.menuFile.menuAction())

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        self.actionClose.triggered.connect(MainWindow.close)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.pushButton.setText(_translate("MainWindow", "Auto Stretch"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabViewer), _translate("MainWindow", "Viewer"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabStacker), _translate("MainWindow", "Stacker"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.actionSave_FITS.setText(_translate("MainWindow", "Save FITS ..."))
        self.actionSave_FITS.setShortcut(_translate("MainWindow", "Ctrl+S"))
        self.actionOpen_FITS.setText(_translate("MainWindow", "Open FITS ..."))
        self.actionOpen_FITS.setShortcut(_translate("MainWindow", "Ctrl+O"))
        self.actionClose.setText(_translate("MainWindow", "Close"))
        self.actionClose.setShortcut(_translate("MainWindow", "Ctrl+W"))

