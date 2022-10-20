
from PyQt5 import QtWidgets, uic
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QPainter


class TraceGUI(QtWidgets.QMainWindow):
    def __init__(self, path):
        # Load ui file
        super(TraceGUI, self).__init__()
        uic.loadUi('trace.ui', self)
        self.setWindowTitle("Memory trace app")

        # Path to the spikes file of a simulation
        self.path = path

        # Open the simulation info
        simInfo = self.open_file()
        self.spikes = simInfo["spikes"]
        self.metainfo = simInfo["metainfo"]
        # Change the spikes format to a list of spikes in each time step
        self.sort_spike_by_timestep()

        # Index of the current timestep shown
        self.timestepIndex = 0
        # Num of timesteps in the simulations with spike information
        self.numTimestep = len(self.spikesByTimestep.values())
        # List of synapses
        self.synapses = {"IN": ["DG", "CA3cont"], "DG": ["CA3cue"], "CA3cue": ["CA1"], "CA1": ["OUT"], "CA3cont": ["OUT"]}

        # Search items in ui
        # + Previous and back buttons
        self.bt_back = self.findChild(QtWidgets.QPushButton, "bt_back")
        self.bt_back.setEnabled(False)
        self.bt_next = self.findChild(QtWidgets.QPushButton, "bt_next")
        self.bt_next.setEnabled(False)

        # + Layer buttons
        self.bt_layer = {}
        self.bt_layer.update({"IN": self.findChild(QtWidgets.QPushButton, "bt_in")})
        self.bt_layer.update({"OUT": self.findChild(QtWidgets.QPushButton, "bt_out")})
        self.bt_layer.update({"DG": self.findChild(QtWidgets.QPushButton, "bt_dg")})
        self.bt_layer.update({"CA3cue": self.findChild(QtWidgets.QPushButton, "bt_ca3cue")})
        self.bt_layer.update({"CA3cont": self.findChild(QtWidgets.QPushButton, "bt_ca3cont")})
        self.bt_layer.update({"CA1": self.findChild(QtWidgets.QPushButton, "bt_ca1")})
        # Disable all layers
        for bt in self.bt_layer.values():
            bt.setEnabled(False)
        # Reset all layers colors
        self.reset_color()

        # + Text fields
        self.text_trace = self.findChild(QtWidgets.QTextEdit, "text_trace")
        self.text_cuesize = self.findChild(QtWidgets.QTextEdit, "text_cuesize")
        self.text_cuesize.setPlainText(str(self.metainfo["cueSize"]))
        self.text_contsize = self.findChild(QtWidgets.QTextEdit, "text_contsize")
        self.text_contsize.setPlainText(str(self.metainfo["contSize"]))
        self.text_simtime = self.findChild(QtWidgets.QTextEdit, "text_simtime")
        self.text_simtime.setPlainText(str(self.metainfo["simTime"]))

        # Create synapses
        self.update()

        # Connect items to functions
        self.bt_next.clicked.connect(self.next)
        self.bt_back.clicked.connect(self.back)

        # Activate buttons to begin the trace
        # self.bt_back.setEnabled(True)
        self.bt_next.setEnabled(True)

        # First updating of trace text window
        self.updateGUI()

        # Show the GUI to the user
        self.show()

    # Next buttons callbacks: pass to the next timestep
    def next(self):
        if self.timestepIndex < self.numTimestep-1:
            self.bt_back.setEnabled(True)
            self.timestepIndex = self.timestepIndex+1
            self.updateGUI()
        if self.timestepIndex >= self.numTimestep-1:
            self.bt_next.setEnabled(False)

    # Back buttons callbacks: pass to the previous timestep
    def back(self):
        if self.timestepIndex > 0:
            self.bt_next.setEnabled(True)
            self.timestepIndex = self.timestepIndex - 1
            self.updateGUI()
        if self.timestepIndex <= 0:
            self.bt_back.setEnabled(False)

    # Update the text windows and layer colors depend on the current timestep
    def updateGUI(self):
        # Reset all layers colors
        self.reset_color()
        # Get current timestep information and show it in the GUI
        currentTimestep = list(self.spikesByTimestep.keys())[self.timestepIndex]
        text = "Timestep=" + str(currentTimestep) + "ms:\n"
        for population in self.spikesByTimestep[currentTimestep].keys():
            self.bt_layer[population].setStyleSheet("background-color : green")
            text = text + " + " + population + " -> " + str(self.spikesByTimestep[currentTimestep][population]) + "\n"
        self.text_trace.setPlainText(text)

    # Reset all layers buttons colors
    def reset_color(self):
        for bt in self.bt_layer.values():
            bt.setStyleSheet("background-color : grey")

    # Create lines to simulate synapses
    def paintEvent(self, event):
        # Create the tools to draw lines
        painter = QPainter(self)
        # Draw one line for each synapse
        for pop_pre in self.synapses.keys():
            for pop_post in self.synapses[pop_pre]:
                painter.drawLine(self.bt_layer[pop_pre].x() + self.bt_layer[pop_pre].width()/2,
                                 self.bt_layer[pop_pre].y() + self.bt_layer[pop_pre].height()/2,
                                 self.bt_layer[pop_post].x() + self.bt_layer[pop_post].width()/2,
                                 self.bt_layer[pop_post].y() + self.bt_layer[pop_post].height()/2)

    # Finish the update thread and GUI windows
    def finished(self):
        self.finish = True
        QApplication.closeAllWindows()

    # Callback of close button
    def closeEvent(self, event):
        self.finished()

    # Change the spikes format to a list of spikes in each time step
    def sort_spike_by_timestep(self):
        self.spikesByTimestep = {}
        # For each timestep
        for timestep in range(self.metainfo["simTime"]):
            spikesInTimestep = {}
            # For each population
            for pop in self.spikes.keys():
                spikesInPop = []
                # For each neuron
                for index, neuron in enumerate(self.spikes[pop]):
                    # If neuron fire a spike in the current timestep, add it to the list
                    if timestep in neuron:
                        spikesInPop.append(index)
                if not(spikesInPop == []):
                    spikesInTimestep.update({pop:spikesInPop})
            # If any neuron has fired in the current timestep, add it to the dict
            if not(spikesInTimestep == {}):
                self.spikesByTimestep.update({timestep:spikesInTimestep})

    # Open file
    def open_file(self):
        try:
            file = open(self.path, "r")
            return eval(file.read())
        except FileNotFoundError:
            return False


if __name__ == "__main__":
    # Full path to the file with the spikes of a simulation
    if len(sys.argv) <= 1:
        # Hardcoded default trace file
        path = "data/2022_10_20__11_35_30_trace.txt"
    else:
        # Take the path from command argument
        path = sys.argv[1]
    # Init GUI
    app = QtWidgets.QApplication(sys.argv)
    main_window = TraceGUI(path)
    app.exec_()