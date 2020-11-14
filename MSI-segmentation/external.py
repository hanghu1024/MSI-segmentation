#====================================================================
# EXTERNAL MSI-segmentation SETUP
#====================================================================

#====================================================================
# Library import
#====================================================================
import os
import time
import math

import numpy as np
import pandas as pd

import matplotlib as mtl
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.ticker import PercentFormatter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
import mplcursors

from sklearn.preprocessing import StandardScaler as SS
from sklearn.decomposition import PCA
from sklearn.mixture import GaussianMixture as GMM
import umap

from skimage.filters import threshold_multiotsu

import despike
#====================================================================