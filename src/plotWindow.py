#!/usr/bin/env python

# Copyright 2016 - 2017 Bas van Meerten and Wouter Franssen

# This file is part of ssNake.
#
# ssNake is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ssNake is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ssNake. If not, see <http://www.gnu.org/licenses/>.

try:
    from PyQt4 import QtGui, QtCore
    from PyQt4 import QtGui as QtWidgets
    from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
except ImportError:
    from PyQt5 import QtGui, QtCore, QtWidgets
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib
matplotlib.rc('svg', fonttype='none')
from matplotlib.colors import colorConverter
from widgetClasses import QLabel
from safeEval import safeEval
import numpy as np
import os
import copy

#####################################################################################


class MainPlotWindow(QtWidgets.QWidget):

    def __init__(self, father, oldMainWindow):
        QtWidgets.QWidget.__init__(self, father)
        self.father = father
        self.oldMainWindow = oldMainWindow
        self.fig = oldMainWindow.current.fig
        self.canvas = FigureCanvas(self.fig)
        self.canvas.mpl_connect('pick_event', self.pickHandler)
        self.ax = oldMainWindow.current.ax
        grid = QtWidgets.QGridLayout(self)
        scroll2 = QtWidgets.QScrollArea()
        grid.addWidget(scroll2, 0, 0)
        scroll2.setWidget(self.canvas)
        self.frame1 = QtWidgets.QGridLayout()
        grid.addLayout(self.frame1, 0, 1)
        scroll = QtWidgets.QScrollArea()
        self.frame1.addWidget(scroll, 0, 0)
        scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        content = QtWidgets.QWidget()
        self.optionFrame = QtWidgets.QGridLayout(content)
        self.optionFrame.addWidget(QLabel("Title:"), 0, 0)
        self.titleEntry = QtWidgets.QLineEdit()
        self.titleEntry.setAlignment(QtCore.Qt.AlignHCenter)
        self.titleBackup = oldMainWindow.get_masterData().name
        self.titleEntry.setText(self.titleBackup)
        self.titleEntry.returnPressed.connect(self.updatePlot)
        self.optionFrame.addWidget(self.titleEntry, 1, 0)
        self.optionFrame.addWidget(QLabel("x-label:"), 2, 0)
        self.xlabelEntry = QtWidgets.QLineEdit()
        self.xlabelEntry.setAlignment(QtCore.Qt.AlignHCenter)
        self.xlabelBackup = self.ax.get_xlabel()
        self.xlabelEntry.setText(self.xlabelBackup)
        self.xlabelEntry.returnPressed.connect(self.updatePlot)
        self.optionFrame.addWidget(self.xlabelEntry, 3, 0)
        self.optionFrame.addWidget(QLabel("y-label:"), 4, 0)
        self.ylabelEntry = QtWidgets.QLineEdit()
        self.ylabelEntry.setAlignment(QtCore.Qt.AlignHCenter)
        self.ylabelBackup = self.ax.get_ylabel()
        self.ylabelEntry.setText(self.ylabelBackup)
        self.ylabelEntry.returnPressed.connect(self.updatePlot)
        self.optionFrame.addWidget(self.ylabelEntry, 5, 0)
        self.xlimBackup = self.ax.get_xlim()
        self.optionFrame.addWidget(QLabel("x-limit left:"), 6, 0)
        self.xlimLeftEntry = QtWidgets.QLineEdit()
        self.xlimLeftEntry.setAlignment(QtCore.Qt.AlignHCenter)
        self.xlimLeftEntry.setText(str(self.xlimBackup[0]))
        self.xlimLeftEntry.returnPressed.connect(self.updatePlot)
        self.optionFrame.addWidget(self.xlimLeftEntry, 7, 0)
        self.optionFrame.addWidget(QLabel("x-limit right:"), 8, 0)
        self.xlimRightEntry = QtWidgets.QLineEdit()
        self.xlimRightEntry.setAlignment(QtCore.Qt.AlignHCenter)
        self.xlimRightEntry.setText(str(self.xlimBackup[1]))
        self.xlimRightEntry.returnPressed.connect(self.updatePlot)
        self.optionFrame.addWidget(self.xlimRightEntry, 9, 0)
        self.ylimBackup = self.ax.get_ylim()
        self.optionFrame.addWidget(QLabel("y-limit down:"), 10, 0)
        self.ylimLeftEntry = QtWidgets.QLineEdit()
        self.ylimLeftEntry.setAlignment(QtCore.Qt.AlignHCenter)
        self.ylimLeftEntry.setText(str(self.ylimBackup[0]))
        self.ylimLeftEntry.returnPressed.connect(self.updatePlot)
        self.optionFrame.addWidget(self.ylimLeftEntry, 11, 0)
        self.optionFrame.addWidget(QLabel("y-limit up:"), 12, 0)
        self.ylimRightEntry = QtWidgets.QLineEdit()
        self.ylimRightEntry.setAlignment(QtCore.Qt.AlignHCenter)
        self.ylimRightEntry.setText(str(self.ylimBackup[1]))
        self.ylimRightEntry.returnPressed.connect(self.updatePlot)
        self.optionFrame.addWidget(self.ylimRightEntry, 13, 0)
        self.widthBackup, self.heightBackup = self.fig.get_size_inches()
        self.widthBackup = self.widthBackup * 2.54
        self.heightBackup = self.heightBackup * 2.54
        self.optionFrame.addWidget(QLabel("Width [cm]:"), 26, 0)
        self.widthEntry = QtWidgets.QLineEdit()
        self.widthEntry.setAlignment(QtCore.Qt.AlignHCenter)
        self.widthEntry.setText(str(self.widthBackup))
        self.widthEntry.returnPressed.connect(self.updatePlot)
        self.optionFrame.addWidget(self.widthEntry, 27, 0)
        self.optionFrame.addWidget(QLabel("Height [cm]:"), 28, 0)
        self.heightEntry = QtWidgets.QLineEdit()
        self.heightEntry.setAlignment(QtCore.Qt.AlignHCenter)
        self.heightEntry.setText(str(self.heightBackup))
        self.heightEntry.returnPressed.connect(self.updatePlot)
        self.optionFrame.addWidget(self.heightEntry, 29, 0)
        self.optionFrame.addWidget(QLabel("dpi:"), 30, 0)
        self.dpiEntry = QtWidgets.QLineEdit()
        self.dpiEntry.setAlignment(QtCore.Qt.AlignHCenter)
        self.dpiEntry.setText(str(self.fig.dpi))
        self.dpiEntry.returnPressed.connect(self.updatePlot)
        self.optionFrame.addWidget(self.dpiEntry, 31, 0)
        self.titleFontSizeBackup = 12
        self.optionFrame.addWidget(QLabel("Title font size:"), 32, 0)
        self.titleFontSizeEntry = QtWidgets.QLineEdit()
        self.titleFontSizeEntry.setAlignment(QtCore.Qt.AlignHCenter)
        self.titleFontSizeEntry.setText(str(self.titleFontSizeBackup))
        self.titleFontSizeEntry.returnPressed.connect(self.updatePlot)
        self.optionFrame.addWidget(self.titleFontSizeEntry, 33, 0)
        self.xlabelFontSizeBackup = 12
        self.optionFrame.addWidget(QLabel("X-label font size:"), 34, 0)
        self.xlabelFontSizeEntry = QtWidgets.QLineEdit()
        self.xlabelFontSizeEntry.setAlignment(QtCore.Qt.AlignHCenter)
        self.xlabelFontSizeEntry.setText(str(self.xlabelFontSizeBackup))
        self.xlabelFontSizeEntry.returnPressed.connect(self.updatePlot)
        self.optionFrame.addWidget(self.xlabelFontSizeEntry, 35, 0)
        self.ylabelFontSizeBackup = 12
        self.optionFrame.addWidget(QLabel("Y-label font size:"), 36, 0)
        self.ylabelFontSizeEntry = QtWidgets.QLineEdit()
        self.ylabelFontSizeEntry.setAlignment(QtCore.Qt.AlignHCenter)
        self.ylabelFontSizeEntry.setText(str(self.ylabelFontSizeBackup))
        self.ylabelFontSizeEntry.returnPressed.connect(self.updatePlot)
        self.optionFrame.addWidget(self.ylabelFontSizeEntry, 37, 0)
        self.xtickFontSizeBackup = 12
        self.optionFrame.addWidget(QLabel("X-ticks font size:"), 38, 0)
        self.xtickFontSizeEntry = QtWidgets.QLineEdit()
        self.xtickFontSizeEntry.setAlignment(QtCore.Qt.AlignHCenter)
        self.xtickFontSizeEntry.setText(str(self.xtickFontSizeBackup))
        self.xtickFontSizeEntry.returnPressed.connect(self.updatePlot)
        self.optionFrame.addWidget(self.xtickFontSizeEntry, 39, 0)
        self.ytickFontSizeBackup = 12
        self.optionFrame.addWidget(QLabel("Y-ticks font size:"), 40, 0)
        self.ytickFontSizeEntry = QtWidgets.QLineEdit()
        self.ytickFontSizeEntry.setAlignment(QtCore.Qt.AlignHCenter)
        self.ytickFontSizeEntry.setText(str(self.ytickFontSizeBackup))
        self.ytickFontSizeEntry.returnPressed.connect(self.updatePlot)
        self.optionFrame.addWidget(self.ytickFontSizeEntry, 41, 0)
        self.legend = self.ax.legend()
        if self.legend is not None:
            if self.oldMainWindow.current.__class__.__name__ == 'CurrentMulti': #If from multiplot
                order = list(self.oldMainWindow.current.extraOffset)
                order.append(0)
                self.legendOrder = list(np.argsort(order))[::-1]
            elif self.oldMainWindow.current.__class__.__name__ == 'CurrentStacked' or self.oldMainWindow.current.__class__.__name__ == 'CurrentSkewed':
                    self.legendOrder = list(np.arange(0,len(self.legend.get_texts())))[::-1]
            else:
                self.legendOrder = list(np.arange(0,len(self.legend.get_texts())))
            self.legend.draggable(True)
            self.legendPos = 'best'
            self.legendTextList = []
            for line in self.legend.get_texts():
                self.legendTextList.append(line.get_text())

            self.legend.set_visible(False)
            self.legendCheck = QtWidgets.QCheckBox('Legend')
            self.legendCheck.stateChanged.connect(self.updateLegend)
            self.optionFrame.addWidget(self.legendCheck, 42, 0)
            legendButton = QtWidgets.QPushButton('Legend settings')
            legendButton.clicked.connect(lambda: LegendWindow(self))
            self.optionFrame.addWidget(legendButton, 43, 0)

        execFileButton = QtWidgets.QPushButton('Execute file')
        execFileButton.clicked.connect(self.exFile)
        self.optionFrame.addWidget(execFileButton, 44, 0)

        self.inFrame = QtWidgets.QGridLayout()
        self.frame1.addLayout(self.inFrame, 1, 0)
        self.inFrame.addWidget(QLabel("File type:"), 0, 0, 1, 2)
        self.filetypeEntry = QtWidgets.QComboBox()
        self.fileOptions = ['svg', 'png', 'eps', 'jpg', 'pdf']
        self.filetypeEntry.addItems(self.fileOptions)
        self.inFrame.addWidget(self.filetypeEntry, 1, 0, 1, 2)
        cancelButton = QtWidgets.QPushButton("&Close")
        cancelButton.clicked.connect(self.cancel)
        self.inFrame.addWidget(cancelButton, 2, 0)
        okButton = QtWidgets.QPushButton("&Save")
        okButton.clicked.connect(self.save)
        self.inFrame.addWidget(okButton, 2, 1)
        grid.setColumnStretch(0, 1)
        grid.setRowStretch(0, 1)
        self.optionFrame.setAlignment(QtCore.Qt.AlignTop)
        self.grid = grid
        scroll.setWidget(content)
        self.updatePlot()

    def rename(self, name):
        self.oldMainWindow.rename(name)

    def updateLegend(self, *args):
        if self.legendCheck.isChecked():
            orderedLines = [self.ax.lines[x] for x in self.legendOrder]
            orderedLegendText = [self.legendTextList[x] for x in self.legendOrder] 
            self.legend = self.ax.legend(orderedLines,orderedLegendText, loc=self.legendPos)
            self.legend.draggable(True)
        else:
            if self.legend is not None:
                self.legend.set_visible(False)
        self.updatePlot()

    def updatePlot(self, *args):
        self.fig.suptitle(self.titleEntry.text(), fontsize=safeEval(self.titleFontSizeEntry.text()))
        self.ax.set_xlabel(self.xlabelEntry.text(), fontsize=safeEval(self.xlabelFontSizeEntry.text()))
        self.ax.set_ylabel(self.ylabelEntry.text(), fontsize=safeEval(self.ylabelFontSizeEntry.text()))
        self.ax.set_xlim((safeEval(self.xlimLeftEntry.text()), safeEval(self.xlimRightEntry.text())))
        self.ax.set_ylim((safeEval(self.ylimLeftEntry.text()), safeEval(self.ylimRightEntry.text())))
        self.ax.tick_params(axis='x', labelsize=safeEval(self.xtickFontSizeEntry.text()))
        self.ax.xaxis.get_offset_text().set_fontsize(safeEval(self.xtickFontSizeEntry.text()))
        self.ax.tick_params(axis='y', labelsize=safeEval(self.ytickFontSizeEntry.text()))
        self.ax.yaxis.get_offset_text().set_fontsize(safeEval(self.ytickFontSizeEntry.text()))
        self.fig.set_size_inches((int(safeEval(self.widthEntry.text())) / 2.54, int(safeEval(self.heightEntry.text())) / 2.54))
        self.canvas.draw()
        self.canvas.adjustSize()

    def pickHandler(self, pickEvent):
        if pickEvent.mouseevent.dblclick and (pickEvent.mouseevent.button == 1):
            if isinstance(pickEvent.artist, matplotlib.lines.Line2D):
                EditLineWindow(self, pickEvent.artist)
        
    def exFile(self):
        warning_msg = "This is an advanced feature. Do not execute files you haven't inspected yourself. Are you sure you want to continue?"
        reply = QtWidgets.QMessageBox.question(self, 'Warning', warning_msg, QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            filename = QtWidgets.QFileDialog.getOpenFileName(self, 'Execute File', self.father.LastLocation)
            if type(filename) is tuple:
                filename = filename[0]        
            fig = self.fig
            ax = self.ax
            if filename:
                try:
                    exec(open(filename).read())
                except Exception as e:
                    self.father.dispMsg(str(e))
                self.canvas.draw()

    def get_mainWindow(self):
        return self.oldMainWindow

    def get_masterData(self):
        return self.oldMainWindow.get_masterData()

    def get_current(self):
        return self.oldMainWindow.get_current()

    def kill(self):
        for i in reversed(range(self.grid.count())):
            item = self.grid.itemAt(i).widget()
            if item is not None:
                item.deleteLater()
        self.grid.deleteLater()
        self.oldMainWindow.kill()
        del self.fig
        del self.canvas
        self.deleteLater()

    def save(self):
        self.updatePlot()
        self.fig.set_size_inches((int(safeEval(self.widthEntry.text())) / 2.54, int(safeEval(self.heightEntry.text())) / 2.54))
        WorkspaceName = self.father.workspaceNames[self.father.workspaceNum]  # Set name of file to be saved to workspace name to start
        f = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File', self.father.LastLocation + os.path.sep + WorkspaceName + '.' + self.fileOptions[self.filetypeEntry.currentIndex()],filter = '(*.' + self.fileOptions[self.filetypeEntry.currentIndex()] + ')')
        if type(f) is tuple:
            f = f[0]        
        if f:
            self.father.LastLocation = os.path.dirname(f)
            dpi = safeEval(self.dpiEntry.text())
            if dpi is None:
                dpi = self.fig.dpi
            self.fig.savefig(f, format=self.fileOptions[self.filetypeEntry.currentIndex()], dpi=dpi)
            if self.fileOptions[self.filetypeEntry.currentIndex()] == 'svg':
                with open(f) as fd: #workarround for stroke miter limit
                    s = fd.read()
                with open(f, 'w') as fd:
                    fd.write(s.replace('stroke-miterlimit:100000;', ''))
            

    def cancel(self):
        self.fig.suptitle(self.titleBackup, fontsize=self.titleFontSizeBackup)
        self.ax.set_xlabel(self.xlabelBackup, fontsize=self.xlabelFontSizeBackup)
        self.ax.set_ylabel(self.ylabelBackup, fontsize=self.ylabelFontSizeBackup)
        self.ax.set_xlim((self.xlimBackup[0], self.xlimBackup[1]))
        self.ax.set_ylim((self.ylimBackup[0], self.ylimBackup[1]))
        self.ax.tick_params(axis='x', labelsize=self.xtickFontSizeBackup)
        self.ax.xaxis.get_offset_text().set_fontsize(self.xtickFontSizeBackup)
        self.ax.tick_params(axis='y', labelsize=self.ytickFontSizeBackup)
        self.ax.yaxis.get_offset_text().set_fontsize(self.ytickFontSizeBackup)
        if self.legend is not None:
            self.legend.set_visible(False)
        self.fig.set_size_inches((self.widthBackup / 2.54, self.heightBackup / 2.54))
        self.grid.deleteLater()
        del self.canvas
        del self.fig
        self.father.closeSaveFigure(self.oldMainWindow)
        self.deleteLater()

#####################################################################################################################


class LegendWindow(QtWidgets.QWidget):

    def __init__(self, parent):
        QtWidgets.QWidget.__init__(self, parent)
        self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.Tool)
        self.father = parent
        self.setWindowTitle("Legend")
        layout = QtWidgets.QGridLayout(self)
        grid = QtWidgets.QGridLayout()
        layout.addLayout(grid, 0, 0, 1, 2)
        grid.addWidget(QLabel("Legend position:"), 0, 0)
        self.posVal = self.father.legendPos
        self.posEntry = QtWidgets.QLineEdit()
        self.posEntry.setAlignment(QtCore.Qt.AlignHCenter)
        self.posEntry.setText(self.posVal)
        self.posEntry.returnPressed.connect(self.preview)
        grid.addWidget(self.posEntry, 1, 0)
        grid.addWidget(QLabel("Legend order:"), 2, 0)
        self.orderVal = self.father.legendOrder
        self.orderEntry = QtWidgets.QLineEdit()
        self.orderEntry.setAlignment(QtCore.Qt.AlignHCenter)
        self.orderEntry.setText(str(self.orderVal))
        self.orderEntry.returnPressed.connect(self.preview)
        grid.addWidget(self.orderEntry, 3, 0)
        grid.addWidget(QLabel("Legend:"), 4, 0)
        self.father.legendCheck.setChecked(True)
        self.spinBox = QtWidgets.QSpinBox()
        self.spinBox.setMaximum(len(self.father.legendTextList) - 1)
        self.spinBox.valueChanged.connect(self.changeEdit)
        grid.addWidget(self.spinBox, 5, 0)
        self.legendEditList = []
        for i in range(len(self.father.legendTextList)):
            self.legendEditList.append(QtWidgets.QLineEdit())
            self.legendEditList[i].setAlignment(QtCore.Qt.AlignHCenter)
            self.legendEditList[i].setText(self.father.legendTextList[i])
            self.legendEditList[i].returnPressed.connect(self.preview)
            grid.addWidget(self.legendEditList[i], 6, 0)
            self.legendEditList[i].setVisible(False)
        self.legendEditList[0].setVisible(True)
        cancelButton = QtWidgets.QPushButton("&Cancel")
        cancelButton.clicked.connect(self.closeEvent)
        layout.addWidget(cancelButton, 1, 0)
        okButton = QtWidgets.QPushButton("&Ok")
        okButton.clicked.connect(self.applyAndClose)
        layout.addWidget(okButton, 1, 1)
        self.show()
        self.setFixedSize(self.size())
        self.setGeometry(self.frameSize().width() - self.geometry().width(), self.frameSize().height() - self.geometry().height(), 0, 0)

    def changeEdit(self, num):
        for i in range(len(self.legendEditList)):
            self.legendEditList[i].setVisible(False)
        self.legendEditList[num].setVisible(True)

    def preview(self, *args):
        tmp = copy.deepcopy(self.father.legendTextList)
        order = eval(self.orderEntry.text())
        for i in range(len(self.legendEditList)):
            tmp[i] = self.legendEditList[i].text()
        env = vars(np).copy()
        try:
            inp = eval(self.posEntry.text(), env)
        except:
            inp = self.posEntry.text()
        orderedLines = [self.father.ax.lines[x] for x in order]
        orderedLegendText = [tmp[x] for x in order] 
        self.father.ax.legend(orderedLines,orderedLegendText, loc=inp)
        self.father.legend.draggable(True)
        self.father.canvas.draw()

    def closeEvent(self, *args):
        self.deleteLater()
        self.father.updateLegend()

    def applyAndClose(self):
        for i in range(len(self.legendEditList)):
            self.father.legendTextList[i] = self.legendEditList[i].text()
        self.father.legendOrder = eval(self.orderEntry.text())
        env = vars(np).copy()
        try:
            inp = eval(self.posEntry.text(), env)
        except:
            inp = self.posEntry.text()
        self.father.legendPos = inp
        self.closeEvent()


#####################################################################################################################


class EditLineWindow(QtWidgets.QWidget):

    def __init__(self, parent, line=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.Tool)
        self.father = parent
        self.canvas = self.father.canvas
        self.ax = self.father.ax
        self.lineList = self.ax.lines
        if line is None:
            self.line = line[0]
        else:
            self.line = line
        self.setWindowTitle("Line")
        layout = QtWidgets.QGridLayout(self)
        grid = QtWidgets.QGridLayout()
        layout.addLayout(grid, 0, 0, 1, 2)        
        grid.addWidget(QLabel("Index:"), 0, 0)
        self.indexSpinBox = QtWidgets.QSpinBox()
        self.indexSpinBox.setMaximum(len(self.lineList)-1)
        self.indexSpinBox.setValue(self.lineList.index(self.line))
        self.indexSpinBox.valueChanged.connect(self.setIndex)
        grid.addWidget(self.indexSpinBox, 1, 0)
        grid.addWidget(QLabel("Line:"), 2, 0)
        colorbutton = QtWidgets.QPushButton("Color", self)
        colorbutton.clicked.connect(self.setColor)
        grid.addWidget(colorbutton, 3, 0)
        grid.addWidget(QLabel("Linewidth:"), 4, 0)
        self.lwSpinBox = QtWidgets.QDoubleSpinBox()
        self.lwSpinBox.setSingleStep(0.1)
        self.lwSpinBox.valueChanged.connect(self.setLineWidth)
        grid.addWidget(self.lwSpinBox, 5, 0)
        grid.addWidget(QLabel("Linestyle:"), 6, 0)
        self.LINESTYLES = ['-', '--', '-.', ':', 'None']
        self.LINENAMES = ['solid', 'dashed', 'dashdot', 'dotted', 'none']
        self.lineDrop = QtWidgets.QComboBox()
        self.lineDrop.addItems(self.LINENAMES)
        self.lineDrop.activated.connect(self.setLineStyle)
        grid.addWidget(self.lineDrop, 7, 0)
        grid.addWidget(QLabel("Marker:"), 8, 0)
        self.MARKERSTYLES = ['o', 'v', '^', '<', '>', '1', '2', '3', '4', '8', 's', 'p', '*', 'h', '+', 'x', 'd', 'None']
        self.MARKERNAMES = ['circle', 'triangle down', 'triangle up', 'triangle left', 'triangle right', 'tri up', 'tri down', 'tri left', 'tri right', 'octagon', 'square', 'pentagon', 'star', 'hexagon', 'plus', 'x', 'diamond', 'none']
        self.markerDrop = QtWidgets.QComboBox()
        self.markerDrop.addItems(self.MARKERNAMES)
        self.markerDrop.activated.connect(self.setMarker)
        grid.addWidget(self.markerDrop, 9, 0)
        colorbutton = QtWidgets.QPushButton("Facecolor", self)
        colorbutton.clicked.connect(self.setFaceColor)
        grid.addWidget(colorbutton, 10, 0)
        colorbutton = QtWidgets.QPushButton("Edgecolor", self)
        colorbutton.clicked.connect(self.setEdgeColor)
        grid.addWidget(colorbutton, 11, 0)
        grid.addWidget(QLabel("Markersize:"), 12, 0)
        self.msSpinBox = QtWidgets.QDoubleSpinBox()
        self.msSpinBox.setSingleStep(0.1)
        self.msSpinBox.valueChanged.connect(self.setMarkerSize)
        grid.addWidget(self.msSpinBox, 13, 0)

        cancelButton = QtWidgets.QPushButton("&Close")
        cancelButton.clicked.connect(self.cancelAndClose)
        layout.addWidget(cancelButton, 1, 0)
        okButton = QtWidgets.QPushButton("&Apply")
        okButton.clicked.connect(self.apply)
        layout.addWidget(okButton, 1, 1)
        self.setup()
        self.show()

    def setup(self):
        self.backupColor = colorConverter.to_rgba(self.line.get_color())
        self.backupLineWidth = self.line.get_linewidth()
        self.lwSpinBox.setValue(self.backupLineWidth)
        self.backupLineStyle = self.line.get_linestyle()
        self.lineDrop.setCurrentIndex(self.LINESTYLES.index(self.backupLineStyle))
        self.backupMarker = self.line.get_marker()
        self.markerDrop.setCurrentIndex(self.MARKERSTYLES.index(self.backupMarker))
        self.backupFaceColor = colorConverter.to_rgba(self.line.get_markerfacecolor())
        self.backupEdgeColor = colorConverter.to_rgba(self.line.get_markeredgecolor())
        self.backupMarkerSize = self.line.get_markersize()
        self.msSpinBox.setValue(self.backupMarkerSize)

    def setIndex(self, val):
        self.reset()
        self.line = self.lineList[val]
        self.setup()
        
    def setColor(self, *args):
        color = QtWidgets.QColor()
        color.setRgbF(*self.backupColor)
        color = QtWidgets.QColorDialog.getColor(color, self, 'Color', QtWidgets.QColorDialog.ColorDialogOption(1))
        if not color.isValid():
            return
        self.line.set_color(color.getRgbF())
        self.canvas.draw()

    def setEdgeColor(self, *args):
        color = QtWidgets.QColor()
        color.setRgbF(*self.backupEdgeColor)
        color = QtWidgets.QColorDialog.getColor(color, self, 'Edgecolor', QtWidgets.QColorDialog.ColorDialogOption(1))
        if not color.isValid():
            return
        self.line.set_markeredgecolor(color.getRgbF())
        self.canvas.draw()

    def setFaceColor(self, *args):
        color = QtWidgets.QColor()
        color.setRgbF(*self.backupFaceColor)
        color = QtWidgets.QColorDialog.getColor(color, self, 'Facecolor', QtWidgets.QColorDialog.ColorDialogOption(1))
        if not color.isValid():
            return
        self.line.set_markerfacecolor(color.getRgbF())
        self.canvas.draw()

    def setLineWidth(self, val):
        self.line.set_linewidth(val)
        self.canvas.draw()

    def setLineStyle(self, val):
        self.line.set_linestyle(self.LINESTYLES[val])
        self.canvas.draw()

    def setMarker(self, val):
        self.line.set_marker(self.MARKERSTYLES[val])
        self.canvas.draw()

    def setMarkerSize(self, val):
        self.line.set_markersize(val)
        self.canvas.draw()

    def reset(self):
        self.line.set_color(self.backupColor)
        self.line.set_linewidth(self.backupLineWidth)
        self.line.set_linestyle(self.backupLineStyle)
        self.line.set_marker(self.backupMarker)
        self.line.set_markeredgecolor(self.backupEdgeColor)
        self.line.set_markerfacecolor(self.backupFaceColor)
        self.line.set_markersize(self.backupMarkerSize)
        self.canvas.draw()
        
    def closeEvent(self, *args):
        self.deleteLater()
        self.father.updateLegend()

    def apply(self):
        self.setup()

    def cancelAndClose(self):
        self.reset()
        self.closeEvent()
