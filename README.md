# Live Demonstration: Bio-inspired implementation of a sparse-learning spike-based hippocampus memory model


<h2 name="Description">Description</h2>
<p align="justify">
Code on which the paper entitled "Live Demonstration: Bio-inspired implementation of a sparse-learning spike-based hippocampus memory model" is based, sent to a congress and awaiting review.
</p>
<p align="justify">
A real-time demonstration of hippocampal bio-inspired spiking memory operation, presented in <a href="https://arxiv.org/abs/2206.04924">trabajos anteriores</a> and present in the Python <a href="https://pypi.org/project/sPyMem/">sPyMem</a> library, is presented through an image learning and recall application. The user is allowed through a GUI to create 5x5 pixel black and white images that will be spatially encoded and sent to memory. The result of the simulation during both operations is represented as a reconstructed image based on the output spiking activity of the network. Moreover, an additional application is included that allows to visualise the internal spiking activity of the network during the simulation in detail for each time step.
</p>
<p align="justify">
Please go to section <a href="#CiteThisWork">cite this work</a> to learn how to properly reference the works cited here.
</p>

<h2>Table of contents</h2>
<p align="justify">
<ul>
<li><a href="#Description">Description</a></li>
<li><a href="#Article">Article</a></li>
<li><a href="#Instalation">Instalation</a></li>
<li><a href="#Usage">Usage</a></li>
<li><a href="#RepositoryContent">Repository content</a></li>
<li><a href="#CiteThisWork">Cite this work</a></li>
<li><a href="#Credits">Credits</a></li>
<li><a href="#License">License</a></li>
</ul>
</p>


<h2 name="Article">Article</h2>
<p align="justify">
<strong>Title</strong>: Live Demonstration: Bio-inspired implementation of a sparse-learning spike-based hippocampus memory model

<strong>Abstract</strong>: The hippocampus acts as a short-term memory capable of recalling a previously-learned complete memory from a fragment of it. Inspired by the hippocampus and taking into account its input from the visual stream, a neuromorphic system capable of learning images and remembering them from a fragment of it in real time was developed. The system contains a bio-inspired hippocampal spiking memory that acts as an autoassociative network that, for each input image, associates the spatial activation patterns of the pixels of the image. A monitor has been designed to visualize the internal spiking activity of the network during the simulation.

<strong>Keywords</strong>: Hippocampus model, Spiking neural networks, Spiking memory, Neuromorphic engineering, SpiNNaker

<strong>Author</strong>: Daniel Casanueva-Morato

<strong>Contact</strong>: dcasanueva@us.es
</p>


<h2 name="Instalation">Instalation</h2>
<p align="justify">
<ol>
	<li>Have or have access to the SpiNNaker hardware platform. In case of local use, follow the installation instructions available on the <a href="http://spinnakermanchester.github.io/spynnaker/6.0.0/index.html">official website</a></li>
	<li>Python version 3.8.10</li>
	<li>Python libraries:</li>
	<ul>
		<li><strong>sPyNNaker8</strong>: last stable version <a href="http://spinnakermanchester.github.io/development/gitinstall.html">compiled from source</a></li>
		<li><strong>PyQt5</strong> 5.15.6</li>
		<li><strong>sPyMem</strong>: 0.0.4</li>
	</ul>
</ol>
</p>
<p align="justify">
To run any script, follow the python nomenclature: 
<code>
python script.py
</code>
</p>


<h2 name="RepositoryContent">Repository content</h3>
<p align="justify">
<ul>
    <li><p align="justify"><a href="real_time_image_memory_app.py">real_time_image_memory_app.py</a>: script in charge of building and launching the simulation of the spiking neuromorphic system, as well as launching the graphical user interface (GUI). This system consists of a hippocampus bio-inspired spiking memory from the library <a href="https://pypi.org/project/sPyMem/">sPyMem</a> and allows the learning and recall of 5x5 pixel black and white images with spiking spatial coding, all in real time. At the end of the simulation, the simulation results can be saved in two files in the <a href="data/">data</a> folder.</p></li>
    <li><p align="justify"><a href="gui.py">gui.py</a>: script in charge of managing the GUI for communication with the spiking memory. It allows the user to construct the input images to the network, manage the operations (learning and recall) to be performed with the memory and the reconstruction of the network output images from its output spiking activity.</p></li>
    <li><p align="justify"><a href="trace_app.py">trace_app.py</a>: script that allows the user through a GUI to navigate and visualise the spiking activity of the whole network throughout the simulation. To select the simulation to visualise, the path to the file "_trace.txt" can be passed as an argument in the execution command or the internal *path* parameter of the code can be modified.</p></li>
    <li><p align="justify"><a href="gui.ui">gui.ui</a> and <a href="trace.ui">trace.ui</a>: files with the information needed in PyQt5 to generate the GUI.</p></li>
    <li><p align="justify"><a href="data/">data</a> folder: contains the results of the saved simulations. For each simulation, 2 files are generated and stored. The file ending in "_memory.txt" stores the contents of the memory at the end of the simulation. The file ending "_trace.txt" contains the spiking activity trace of the whole network which can be visualised with the script <a href="trace_app.py">trace_app.py</a>.</p></li>
    <li><p align="justify"><a href="media/">media</a> folder: contains the GUI images of both applications in operation, as well as a video demonstration of their operation.</p></li>
</ul>
</p>


<h2 name="Usage">Usage</h2>
<p align="justify">
To run the live demonstration of the bio-inspired hippocampus spiking memory with the ability to learn and recall 5x5 pixel black and white images, run <a href="real_time_image_memory_app.py">real_time_image_memory_app.py</a>. This will display the GUI in charge of user interaction with the spiking system. Initially, it will be necessary to indicate the simulation time to be used. After that, press the start simulation button. When the simulation is ready, the panel for drawing the 5x5 image (by clicking with the mouse on each pixel) and the buttons for learning and recall operations will be unlocked. The 5x5 panel on the right represents the reconstruction of the output image of the network from its output pulsed activity.
</p>
<p align="justify">
After finishing the simulation, the simulation result can be saved by clicking on the *save* button. This will generate two data files which are detailed in <a href="#RepositoryContent">Repository content</a>. To check the spiking activity trace of the network during the simulation you can run <a href="trace_app.py">trace_app.py</a> by passing the path to the generated "_trace.txt" file as an execution parameter (or you can also modify the *path* parameter of the script). In the application window that will open, the characteristics of the simulation and the network can be observed, as well as the visualisation of the spiking activity of the network both schematically (drawing of the network with green activation of the populations that are being activated) and in detail (indicating each neuron of each population that is activated) at each instant of time.
</p>


<h2 name="CiteThisWork">Cite this work</h2>
<p align="justify">
Still under construction.
</p>

<h2 name="Credits">Credits</h2>
<p align="justify">
The author of the original idea is Daniel Casanueva-Morato while working on a research project of the <a href="http://www.rtc.us.es/">RTC Group</a>.

This research was partially supported by the Spanish grant MINDROB (PID2019-105556GB-C33/AEI/10.13039/501100011033). 

D. C.-M. was supported by a "Formación de Profesor Universitario" Scholarship from the Spanish Ministry of Education, Culture and Sport.
</p>


<h2 name="License">License</h2>
<p align="justify">
This project is licensed under the GPL License - see the <a href="https://github.com/dancasmor/
Real-time-spike-based-hippocampus-memory-model-for-image-storage/blob/main/LICENSE">LICENSE.md</a> file for details.
</p>
<p align="justify">
Copyright © 2022 Daniel Casanueva-Morato<br>
<a href="mailto:dcasanueva@us.es">dcasanueva@us.es</a>
</p>

[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](http://www.gnu.org/licenses/gpl-3.0)
