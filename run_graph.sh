#!/bin/bash

# Open the second terminal tab and navigate to folder 2, then run Python script 2
gnome-terminal --tab --title="PyBurraco Plotter" --working-directory="/home/alessandro/Documents/Projects/Python/PyBurraco" -- bash -c "\
source venv/bin/activate && \
python3 -c '\
import sys; \
sys.path.append(\"/home/alessandro/Documents/Projects/Python/PyBurraco\"); \
from utils.plotter import plot_evolution; \
plot_evolution(save_plot=True)' && \
exit"

