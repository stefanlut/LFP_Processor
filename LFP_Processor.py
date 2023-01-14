import sys

import matplotlib
from scipy import signal
import numpy as np
import scipy.io as sio

matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt5agg import \
    NavigationToolbar2QT as NavigationToolbar
from PyQt5 import QtCore, QtGui, QtWidgets


class Window(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
        self.setWindowTitle('LFP Processor')
        # a figure instance to plot on
        self.figure = plt.figure()
  
        # this is the Canvas Widget that
        # displays the 'figure'it takes the
        # 'figure' instance as a parameter to __init__
        self.canvas = FigureCanvasQTAgg(self.figure)
  
        # this is the Navigation widget
        # it takes the Canvas widget and a parent
        self.toolbar = NavigationToolbar(self.canvas, self)
        # creating a Vertical Box layout
        layout = QtWidgets.QVBoxLayout()
        # creaing widgets
        widgets = [
                self.toolbar,
                self.canvas,
                    ]
        pushplot_widget = QtWidgets.QPushButton('Load and Plot LFP Data')
        pushplot_widget.clicked.connect(lambda: self.plot(self.load_LFP_data(),dropdown_widget.currentIndex(),t1_widget.text(),t2_widget.text()))
        dropdown_widget = QtWidgets.QComboBox()
        dropdown_widget.addItems(['Delta','Theta','Alpha','Beta','Gamma'])
        dropdown_widget.setPlaceholderText("Choose Bandpass Region Here")
        t1_widget = QtWidgets.QLineEdit()
        t2_widget = QtWidgets.QLineEdit()
        t1_widget.setPlaceholderText("Enter t1 of interval [t1, t2] as a decimal")
        t2_widget.setPlaceholderText("Enter t2 of interval [t1, t2] as a decimal")
        for w in widgets:
            layout.addWidget(w)
        layout.addWidget(pushplot_widget)
        layout.addWidget(dropdown_widget)
        layout.addWidget(t1_widget)
        layout.addWidget(t2_widget)
        # layout.addWidget(pushselect_widget)
        # setting layout to the main window
        self.setLayout(layout)

    def load_LFP_data(self):
        dlg = QtWidgets.QFileDialog()
        dlg.setFileMode(QtWidgets.QFileDialog.AnyFile)
        dlg.setNameFilter("MATLAB Workspace Data (*.mat)")
        filenames = list()
        matname = None
        if dlg.exec_():
            filenames = dlg.selectedFiles()
            matname = filenames[0]
        
        return matname
        
 # action called by the push button
    def plot(self,fname = None, bandIndex=None, t1 = None,t2 = None):
        if fname == None:
            dlg = QtWidgets.QMessageBox()
            dlg.setWindowTitle("Error")
            dlg.setText("No File Selected")
            button = dlg.exec()
            return
        if bandIndex == 0:
            Wn = [0.5,4]
        elif bandIndex == 1:
            Wn = [4,8]
        elif bandIndex == 2:
            Wn = [8,12]
        elif bandIndex == 3:
            Wn = [12,35]
        elif bandIndex == 4:
            Wn = [35, 120]
        # LFP data
        data = sio.loadmat(fname)
        LFP = data['LFP'][0] - np.mean(data['LFP'][0]) # Recover LFP data and mean center LFP data
        t = data['t'][0] # Recover time data

        try:
            if t1 == "" or t2 == "":
                dlg = QtWidgets.QMessageBox()
                dlg.setWindowTitle("Error")
                dlg.setText("No Time Interval Requested")
                button = dlg.exec()
                return
            t1 = np.where(t== float(t1) )[0][0] # If this function fails
            t2 = np.where(t==float(t2) )[0][0] # ... or if this function fails see except block
        except:
            dlg = QtWidgets.QMessageBox()
            dlg.setWindowTitle("Error")
            dlg.setText("Invalid Time Interval Requested")
            button = dlg.exec()
            return
            
        dt = t[1] - t[0]                     # Define the sampling interval,
        Fs = 1/dt                       # Calculate sampling rate
        fNQ = Fs/ 2                     # ... and Nyquist frequency.
        n = 100;                             # define filter order,
        b = signal.firwin(n, Wn, nyq=fNQ, pass_zero=False, window='hamming') #calculate filter coefficients
        Vhi = signal.filtfilt(b, 1, LFP)    # ... and apply it to the data.
        X = signal.hilbert(Vhi)             # Calculate Hilbert Transform of filtered LFP data
        phi = np.angle(X)     # Compute phase of filtered signal
        amp = abs(X)       # Compute amplitude of filtered signal
        # clearing old figure
        self.figure.clear()
  
        # create axes
        ax1 = self.figure.add_subplot(311)
        ax2 = self.figure.add_subplot(312)
        ax3 = self.figure.add_subplot(313)
        ax3.set_xlabel("Time (s)")
        # plot data
        line1 = ax1.plot(t[t1:t2],LFP[t1:t2])
        line2 = ax1.plot(t[t1:t2], Vhi[t1:t2])
        ax1.set_ylabel('Voltage')
        ax1.get_xaxis().set_visible(False)
        ax1.legend(('LFP','Bandpass Filtered LFP'), loc = 'upper right')
        ax2.plot(t[t1:t2],amp[t1:t2])
        ax2.get_xaxis().set_visible(False)
        ax2.set_ylabel('Amplitude')
        ax3.plot(t[t1:t2],phi[t1:t2])
        ax3.set_ylabel('Phase (rad)')
        # refresh canvas
        self.canvas.draw() 



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    # creating a window object
    main = Window()
    # showing the window
    main.show()
    # loop
    sys.exit(app.exec_())