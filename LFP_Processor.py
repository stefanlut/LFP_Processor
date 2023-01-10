import sys
import matplotlib
from pylab import *
matplotlib.use('Qt5Agg')
import scipy.io as sio
from scipy import signal
from PyQt5 import QtCore, QtGui, QtWidgets
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
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
        pushb_widget = QtWidgets.QPushButton('Plot')
        pushb_widget.clicked.connect(self.plot)
        dropdown_widget = QtWidgets.QComboBox()
        dropdown_widget.addItems(['Delta','Theta','Alpha','Beta','Gamma'])
        # adding action to the button
        #self.button.clicked.connect(self.plot)
        
        
        # Just some button connected to 'plot' method
        #self.button = QtWidgets.QPushButton('Plot')
        for w in widgets:
            layout.addWidget(w)
        layout.addWidget(dropdown_widget)
        layout.addWidget(pushb_widget)
        # setting layout to the main window
        self.setLayout(layout)
 # action called by the push button
    def plot(self):
          
        # LFP data
        data = sio.loadmat('Ch7-LFP-1.mat')
        LFP = data['LFP'][0]
        t = data['t'][0]
        t1 = np.where(t==44.0)[0][0]
        t2 = np.where(t==47.0)[0][0]
        dt = t[1] - t[0]                     # Define the sampling interval,
        fNQ = 1 / dt / 2                     # ... and Nyquist frequency.
        Wn = [80, 120];                      # Set the passband [80-120] Hz,
        n = 100;                             # ... and filter order,
        b = signal.firwin(n, Wn, nyq=fNQ, pass_zero=False, window='hamming')
        Vhi = signal.filtfilt(b, 1, LFP);    # ... and apply it to the data.
        X_Gamma = signal.hilbert(Vhi)
        phi = angle(X_Gamma)     # Compute phase of low-freq signal
        amp = abs(X_Gamma)       # Compute amplitude of high-freq signal
        # clearing old figure
        self.figure.clear()
  
        # create an axis
        ax1 = self.figure.add_subplot(311)
        ax2 = self.figure.add_subplot(312)
        ax3 = self.figure.add_subplot(313)
        # plot data
        ax1.plot(t[t1:t2],LFP[t1:t2])
        ax2.plot(t[t1:t2],amp[t1:t2])
        ax3.plot(t[t1:t2],phi[t1:t2])
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