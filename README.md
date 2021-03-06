# MSI-segmentation

It is an unsupervised data processing pipeline for mass spectrometry imaging (MSI) segmentation by combining multivariate clustering and univariate thresholding. 

The pipeline comprises four independent data processing modules, as illustrated as follows. First, we perform data preprocessing (not included in this repository), in which peak picking, peak detection + m/z binning, pixel alignment, peak intensity normalization are performed to organize MSI data for downstream data mining. Next, pixels are clustered based on their spectral similarity in multivariate analysis. In particular, both PCA and UMAP are applied: the former generates compressed features for GMM clustering, while the latter helps estimate the number of clusters. Given these inputs, GMM is repeatedly fitted, assigned with a range (5) of mixture component numbers around UMAP estimation. In parallel, ion images that are poorly represented in multivariate analysis are detected and independently partitioned using multi-Otsu thresholding. As a result, ensemble generation of both multivariate and univariate analyses approximates a pool of spatial segment candidates. Finally, we assemble the segmentation map. 

<div align="center">
<img src="images/image1.png" width="400">
</div>

Herein we limit the user effort to validation and selection of segment candidates. Computational results are exported in forms of .csv and .png. Results are also visualized by Tkinter interactive interface. You may set parameters and select segment candidates by editing config.py. Representative analysis results of a mouse kidney section data set (included in example) are as follows. 

<div align="center">
<img src="images/analysis_results.png" width="600">
</div>
Ion image generated from peak intensities (A), UMAP + HDBSCAN analysis (B) and PCA scree plot (C) produced by L0 module. (D) Outlier ion image detection by ward's hierarchical clustering and PCA loading analysis. (E) Ion image thresholding analysis. (F) Automatically assemble the ensemble clustering results by a co-occurrence majority vote method. (G) Ensemble segment candidates and auto-assembled segmentation map. (H) A simplified map to highlight kidney anatomical regions.

# Requirements
numpy 1.18.1
pandas 1.1.0
matplotlib 3.1.3
mplcursors 0.3
tkinter 8.6
scipy 1.4.1
scikit-learn 0.22.1
scikit-image 0.16.2
umap-learn 0.3.10
hdbscan 0.8.26
despike 0.1.0

# How to use 
## Data preparation
Two data preparation strategies are used: 1. peak picking for PCA analysis. 2. peak detection + m/z binning for UMAP analysis. After pixel alignment, peak intensity normalization, denoise, etc, flaten the MSI data sets as input data. 2D spatial indexes are kept in first two columns. A sample mouse kidney section data set is provided in the example foler.
<div align="center">
<img src="images/image3.png" width="600">
</div>

## Main programs
Run *MSI-segmentation_LX* modules sequentially, outputs of one module may be the input for the following module. Edit corresponding levels in config.py along the pipeline. <br>To test the mouse kidney MSI sample, clone repository and run MSI-segmentation_L0.py. Note: only partial peak intensities are included in the sample data, because of the upload limit. Analysis results are slightly different from the manuscript.

*MSI-segmentation_L0.py*<br>
Show ion images, reduce the dimensionality of MSI data by PCA and UMAP. 

*MSI-segmentation_L1.0.py*<br>
Multivariate clustering by Gaussian mixture model.

*MSI-segmentation_L1.1.py (validation)*<br>
Show clustering results by interactive tkinter interface. 

*MSI-segmentation_L1.2.py*<br>
Detect ion images which are not captured by PCA analysis. A ward's hierarchical clustering method is used to cluster ion distribution patterns.

*MSI-segmentation_L2.0.py*<br>
Univariate thresholding by multi-Otsu thresholding algorithm.

*MSI-segmentation_L2.1.py (selection)*<br>
Binarization of selected ion images with selected thresholding labels. 

*MSI-segmentation_L3.0.py*<br>
Automatically assemble the clustering analysis with a co-occurrence majority vote method. Compuation could be expensive for large size MSI data.

*MSI-segmentation_L3.1.py (validation)*<br>
Show ensemble segment candidates by interactive tkinter interface. 

*MSI-segmentation_L3.2.py (selection)*<br>
Simplify the auto-assembled segmentation map or manually assemble the final segmentation map.

# Reference
Hang Hu, Ruichuan Yin, Hilary M. Brown, and Julia Laskin, Spatial Segmentation of Mass Spectrometry Imaging Data by Combining Multivariate Clustering and Univariate Thresholding, Anal. Chem. 2021. https://pubs.acs.org/doi/full/10.1021/acs.analchem.0c04798
