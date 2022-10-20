import threading

from sPyMem import hippocampus_with_forgetting
import spynnaker8 as sim
import math
from threading import Condition, Thread
import time
import sys
from PyQt5 import QtWidgets
from gui import GUI


# Network and simulation parameters:
# + Number of directions of the memory
cueSize = 31
# + Size of the patterns in bits/neuron
contSize = 20

# + Time step of the simulation
timeStep = 1.0


# + Number of neurons in input layer: the number of bits neccesary to represent the number of directions in
# binary + the size of patterns
cueSizeInBin = math.ceil(math.log2(cueSize+1))
numInputLayerNeurons = cueSizeInBin + contSize


# + Create a condition to avoid overlapping prints
print_condition = Condition()
# + Create a semaphore to avoid concurrent overwriting var in receive callback to paint the GUI
semaphore = threading.Semaphore(1)

# Debug mode?
debug = True


# + Callback init function
def init_pop(label, n_neurons, run_time_ms, machine_timestep_ms):
    if debug:
        print_condition.acquire()
        print(str(label) + " has " + str(n_neurons) + " neurons")
        print("Simulation will run for " + str(run_time_ms) + "ms at " + str(machine_timestep_ms) + "ms timesteps")
        print_condition.release()
    # Indicate to the GUI that is the simulation is ready to receive spikes
    main_window.ready.emit()


# + Callback send live spikes
def send_spikes_to(label, sender):
    while (True):
        # Wait for operation ready in GUI
        while(not main_window.operation_ready):
            time.sleep(1)
        main_window.operation_ready = False
        # Get operation and neurons id
        numOperations = main_window.num_operations
        neuronIDs = main_window.in_bt_active
        # Debug information
        if debug:
            print_condition.acquire()
            print("Sending spikes to neurons ID = " + str(neuronIDs))
            print_condition.release()
        # For each neuron to send spikes, it sends the number of spikes necessary according to the operation
        for i in range(numOperations):
            sender.send_spikes(label, neuronIDs, send_full_keys=True)
            time.sleep(0.001)


# + Callback receive live spikes
def received_spikes(label, _time, neuron_ids):
    # Debug info
    if debug:
        print_condition.acquire()
        print("t=" + str(_time) + " p=" + label + " " + str(neuron_ids))
        print_condition.release()
    # Indicate to the GUI what output neurons are receiving spikes to change output neurons colors
    if label == "OLayer":
        semaphore.acquire()
        main_window.new_out_neurons.emit(neuron_ids)
        semaphore.release()


def test():
    # Wait until user push simulation init button
    while (not main_window.simulation_ready):
        time.sleep(1)
    # Get simTime value from user input in GUI
    simTime = main_window.simTime*1000

    ######################################
    # Simulation parameters
    ######################################
    # Setup simulation
    sim.setup(timeStep)

    ######################################
    # Live tools
    ######################################
    # LIVE SENDER CONNECTION
    # Set up the live connection for sending spikes
    live_spikes_connection_send = sim.external_devices.SpynnakerLiveSpikesConnection(receive_labels=None,
                                                                                     local_port=None,
                                                                                     send_labels=["LiveInjectionLayer"])
    # Set up callbacks to occur at initialisation
    live_spikes_connection_send.add_init_callback("LiveInjectionLayer", init_pop)
    # Set up callbacks to occur at the start of simulation
    live_spikes_connection_send.add_start_resume_callback("LiveInjectionLayer", send_spikes_to)

    # LIVE RECEIVER CONNECTION
    # A new spynnaker live spikes connection is created to define that there is a python function which receives
    # the spikes.
    live_spikes_connection_receive = sim.external_devices.SpynnakerLiveSpikesConnection(
        receive_labels=["OLayer", "ILayer"], local_port=None, send_labels=None)
    # Set up callbacks to occur when spikes are received
    live_spikes_connection_receive.add_receive_callback("OLayer", received_spikes)
    live_spikes_connection_receive.add_receive_callback("ILayer", received_spikes)

    ######################################
    # Create network
    ######################################
    # Input layer (live injection)
    LiveInjectionLayer = sim.Population(numInputLayerNeurons, sim.external_devices.SpikeInjector(database_notify_port_num=live_spikes_connection_send.local_port),
                                        label='LiveInjectionLayer',
                                        additional_parameters={'virtual_key': 0x70000,})
    # Input layer (real input population to debug): fire a spike when receive a spike
    neuronParameters = {"cm": 0.27, "i_offset": 0.0, "tau_m": 3.0, "tau_refrac": 1.0, "tau_syn_E": 0.3,
                        "tau_syn_I": 0.3,
                        "v_reset": -60.0, "v_rest": -60.0, "v_thresh": -57.5}
    ILayer = sim.Population(numInputLayerNeurons, sim.IF_curr_exp(**neuronParameters), label="ILayer")
    # Output layer: fire a spike when receive a spike
    OLayer = sim.Population(numInputLayerNeurons, sim.IF_curr_exp(**neuronParameters), label="OLayer")
    OLayer.set(v=-60)
    # Create memory
    memory = hippocampus_with_forgetting.Memory(cueSize, contSize, sim, LiveInjectionLayer, OLayer)
    # Create extra synapses
    sim.Projection(LiveInjectionLayer, ILayer, sim.OneToOneConnector(), sim.StaticSynapse(weight=6.0))

    ######################################
    # Parameters to store
    ######################################
    # Record spikes from output layer
    OLayer.record(["spikes"])
    ILayer.record(["spikes"])
    memory.CA3cueLayer.record(["spikes"])
    memory.CA3contLayer.record(["spikes"])
    for gate in memory.DGLayer.and_gates.and_array:
        gate.output_neuron.record(("spikes"))
    for gate in memory.CA1Layer.or_gates.or_array:
        gate.output_neuron.record(("spikes"))
    # Activate the sending of live spikes
    sim.external_devices.activate_live_output_for(OLayer,
                                                  database_notify_port_num=live_spikes_connection_receive.local_port)
    sim.external_devices.activate_live_output_for(ILayer,
                                                  database_notify_port_num=live_spikes_connection_receive.local_port)

    ######################################
    # Execute the simulation
    ######################################
    sim.run(simTime)

    ######################################
    # Retrieve output data
    ######################################
    inputSpikes = ILayer.get_data(variables=["spikes"]).segments[0].spiketrains
    outputSpikes = OLayer.get_data(variables=["spikes"]).segments[0].spiketrains
    CA3cueSpikes = memory.CA3cueLayer.get_data(variables=["spikes"]).segments[0].spiketrains
    CA3contSpikes = memory.CA3contLayer.get_data(variables=["spikes"]).segments[0].spiketrains
    DGSpikes = []
    for gate in memory.DGLayer.and_gates.and_array:
        DGSpikes.append(gate.output_neuron.get_data(variables=["spikes"]).segments[0].spiketrains[0])
    CA1Spikes = []
    for gate in memory.CA1Layer.or_gates.or_array:
        CA1Spikes.append(gate.output_neuron.get_data(variables=["spikes"]).segments[0].spiketrains[0])
    # Format to remove innecesary information and store it
    formatDGspikes = format_spike_stream(DGSpikes)
    formatDGspikes[0] = []
    spikes = {"metainfo":{"simTime":simTime, "cueSize":cueSize, "contSize":contSize},
              "spikes":{"IN": format_spike_stream(inputSpikes), "OUT": format_spike_stream(outputSpikes),
                    "DG": formatDGspikes, "CA3cue": format_spike_stream(CA3cueSpikes),
                    "CA3cont": format_spike_stream(CA3contSpikes), "CA1": format_spike_stream(CA1Spikes)}}

    ######################################
    # End simulation
    ######################################
    sim.end()
    if debug:
        #print(outputSpikes)
        print(main_window.memoryState)

    print("Finished!")
    main_window.memory_spikes = spikes
    main_window.bt_save.setEnabled(True)


# Format the input spike stream from np array to simple array
def format_spike_stream(spikesStream):
    formatSpikes = []
    for neuron in spikesStream:
        formatSpikes.append(neuron.as_array().tolist())
    return formatSpikes


if __name__ == "__main__":
    # Create GUI
    app = QtWidgets.QApplication(sys.argv)
    global main_window
    main_window = GUI(cueSize, cueSizeInBin, contSize)
    # Init the test in secondary thread
    thread_test = Thread(target=test)
    thread_test.start()
    # Init GUI in main thread
    app.exec_()


