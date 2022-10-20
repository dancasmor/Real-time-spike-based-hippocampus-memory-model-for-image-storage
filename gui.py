import functools
import os
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QApplication, QCheckBox, QLabel, QPushButton
import threading
import time


class GUI(QtWidgets.QMainWindow):
    # Signal for update out image when new out neuron activity
    new_out_neurons = pyqtSignal(list)
    # Signal to enable interactive input
    ready = pyqtSignal()
    # Semaphore to avoid multiple concurrent execution of update out image
    semaphore = threading.Semaphore(1)

    def __init__(self, cueSize, cueSizeInBin, contSize):
        # Load ui file
        super(GUI, self).__init__()
        uic.loadUi('gui.ui', self)
        self.setWindowTitle("Real time memory app")

        # Memory size
        self.cueSize = cueSize
        self.cueSizeInBin = cueSizeInBin
        self.contSize = contSize
        # If there is some operation to send to spinnaker: learn or recall
        self.operation_ready = False
        # If the user has input a simTime number to init the simiulation
        self.simulation_ready = False
        # Number of repetitions of the input spikes depend on the operation
        self.num_operations = 3
        # Input image buttons actives = input neuron to send spikes
        self.in_bt_active = []
        # If the program has ended
        self.finish = False
        # Current memory state
        self.memoryState = {}
        for i in range(1, self.cueSize+1):
            self.memoryState.update({i: []})
        # Spike trace of the memory
        self.memory_spikes = None

        # Search items in ui
        self.bt_init_sim = self.findChild(QtWidgets.QPushButton, "bt_init_sim")
        self.box_simtime = self.findChild(QtWidgets.QSpinBox, "box_simtime")
        self.bt_learn = self.findChild(QtWidgets.QPushButton, "bt_learn")
        self.bt_recall = self.findChild(QtWidgets.QPushButton, "bt_recall")
        self.bt_save = self.findChild(QtWidgets.QPushButton, "bt_save")
        self.inputCueBt = []
        self.inputContBt = []
        self.outputCueBt = []
        self.outputContBt = []
        for i in range(cueSizeInBin+contSize):
            if i < cueSizeInBin:
                self.inputCueBt.append(self.findChild(QtWidgets.QPushButton, "bt_in_" + str(i)))
                self.outputCueBt.append(self.findChild(QtWidgets.QPushButton, "bt_out_" + str(i)))
            else:
                self.inputContBt.append(self.findChild(QtWidgets.QPushButton, "bt_in_" + str(i)))
                self.outputContBt.append(self.findChild(QtWidgets.QPushButton, "bt_out_" + str(i)))

        # Total number of "pixel" in in/out image
        self.numPixel = len(self.inputCueBt) + len(self.inputContBt)

        # Connect items to functions
        self.bt_init_sim.clicked.connect(self.init_sim)
        self.bt_learn.clicked.connect(functools.partial(self.send_op, 3))
        self.bt_recall.clicked.connect(functools.partial(self.send_op, 1))
        for id, bt in enumerate(self.inputCueBt):
            bt.clicked.connect(functools.partial(self.in_bt_change, id, 0))
        for id, bt in enumerate(self.inputContBt):
            bt.clicked.connect(functools.partial(self.in_bt_change, id, 1))
        self.bt_save.clicked.connect(self.save_memory_trace)

        # Create a thread to wait for new output neurons
        self.new_out_neurons.connect(self.update_out_neurons_activity)
        self.ready.connect(self.enable_input_activity)

        # Show the GUI to the user
        self.show()

    ################################################################
    # Create or update GUI
    ################################################################

    # Enable input components in GUI when init simulation
    def enable_input_activity(self):
        self.bt_recall.setEnabled(True)
        self.bt_learn.setEnabled(True)
        for bt in self.inputCueBt:
            bt.setEnabled(True)
            bt.setStyleSheet("background-color: black;")
        for bt in self.inputContBt:
            bt.setEnabled(True)
            bt.setStyleSheet("background-color: black;")

    ################################################################
    # Callbacks
    ################################################################

    # Callback of init simulation
    def init_sim(self):
        self.simTime = self.box_simtime.value()
        self.box_simtime.setEnabled(False)
        self.bt_init_sim.setEnabled(False)
        self.simulation_ready = True

    # Callback of close button
    def closeEvent(self, event):
        self.finished()

    # Finish the update thread and GUI windows
    def finished(self):
        self.finish = True
        QApplication.closeAllWindows()

    def send_op(self, num_operations):
        self.num_operations = num_operations
        self.operation_ready = True

    # Callback of in buttons image: store current matrix state
    def in_bt_change(self, id, type):
        if type == 0:
            if self.inputCueBt[id].styleSheet() == "background-color: black;":
                self.in_bt_active.append(id)
                self.inputCueBt[id].setStyleSheet("background-color: white;")
            else:
                self.in_bt_active.remove(id)
                self.inputCueBt[id].setStyleSheet("background-color: black;")
        else:
            if self.inputContBt[id].styleSheet() == "background-color: black;":
                self.in_bt_active.append(id + len(self.inputCueBt))
                self.inputContBt[id].setStyleSheet("background-color: white;")
            else:
                self.in_bt_active.remove(id + len(self.inputCueBt))
                self.inputContBt[id].setStyleSheet("background-color: black;")

    # Callback of save button: save the spike trace through the memory network and memory state
    def save_memory_trace(self):
        # Check and create the path if it not exists
        path = "data/"
        if not os.path.isdir(path):
            try:
                os.mkdir(path)
            except OSError as e:
                print("Error to create directory")
                return False
        # Create path to the files
        common_path = path + time.strftime("%Y_%m_%d__%H_%M_%S")
        fullPathTrace = common_path + "_trace" + ".txt"
        fullPathState = common_path + "_memory" + ".txt"
        # Create and write content
        file = open(fullPathTrace, "w")
        file.write(str(self.memory_spikes))
        file.close()
        file = open(fullPathState, "w")
        file.write(str(self.memoryState))
        file.close()
        print(fullPathTrace)
        print(fullPathState)

    ################################################################
    # Communication thread
    ################################################################

    # Function that communicate SpiNNaker simulation with GUI in other thread
    def update_out_neurons_activity(self, out_neurons):
        self.semaphore.acquire()
        # Check buttons, if receive spikes change color to white
        cue = 0
        cont = []
        for bt_id in range(self.numPixel):
            if bt_id in out_neurons:
                if bt_id < len(self.outputCueBt):
                    self.outputCueBt[bt_id].setStyleSheet("background-color: white;")
                    cue = cue + pow(2, bt_id)
                else:
                    self.outputContBt[bt_id - len(self.outputCueBt)].setStyleSheet("background-color: white;")
                    cont.append(bt_id - len(self.outputCueBt))
            else:
                if bt_id < len(self.outputCueBt):
                    self.outputCueBt[bt_id].setStyleSheet("background-color: black;")
                else:
                    self.outputContBt[bt_id - len(self.outputCueBt)].setStyleSheet("background-color: black;")
        # If learning operation, store the new content corresponding the cue
        if self.num_operations == 3:
            self.memoryState[cue] = cont
        self.semaphore.release()