#===========================================
# import modules, defs and variables
#===========================================
exec(open("./external.py").read())
exec(open("./defs.py").read())
exec(open("./config.py").read())

print('Finish modules, defs and variables import')

#===========================================
# import data 
#===========================================
df_pixel = pd.read_csv(InputDir, header = None) # use pandas, cause the print is interpretable
if MassList_FileDir != 0: 
    df_MassList = pd.read_csv(MassList_FileDir, header = None)
    MassList = df_MassList.values.astype(np.float64)

print('Finish pixel raw data import')

#===========================================
# L2.0.0 data processing
#===========================================
# parse info
NumLine = int(np.max(df_pixel[0]) + 1)
NumSpePerLine = int(np.max(df_pixel[1]) + 1)

# data organization
pixel = df_pixel.values.astype(np.float64)
img = pixel.T.reshape(pixel.shape[1], NumLine, NumSpePerLine)

# parameter for plotting
aspect = AspectRatio*NumSpePerLine/NumLine
index_999 = round(NumLine*NumSpePerLine*0.999)

# make folder for univariate thresholding analysis
OutputFolder = locate_OutputFolder2(L0outputDir)
OutputFolder = locate_OutputFolder3(OutputFolder, 'univariate thresholding')
os.mkdir(OutputFolder)

print('Finish L2.0.0 data processing, next step: thresholding')

#===========================================
# L2.0.1 thresholding
#===========================================
# accumulator 
img_thresholds = np.empty([n_classes-1, 0])
img_segs = np.empty([0, NumLine, NumSpePerLine])

# calculation
for i in index:
    thresholds = threshold_multiotsu(img[i+2], classes = n_classes) # first 2 columns are spatial index
    img_seg = np.digitize(img[i+2], bins = thresholds)
    img_thresholds = np.append(img_thresholds, thresholds.reshape(thresholds.shape[0],1), axis=1)
    img_segs = np.append(img_segs, img_seg.reshape(1, img_seg.shape[0], img_seg.shape[1]), axis=0)

# organize img_seg_flatten results
img_segs_flatten = img_segs.reshape(img_segs.shape[0], -1).T
df_img_segs_flatten = pd.DataFrame(img_segs_flatten, columns=index)  ## I shold add my index here and make them first 2two concate
df_img_segs_flatten.insert(0, 'spectrum_index', df_pixel[1])
df_img_segs_flatten.insert(0, 'line_index', df_pixel[0])

# save
SaveDir = OutputFolder + '\\pixel_label.csv'
df_img_segs_flatten.to_csv(SaveDir, index=False, sep=',')

print('Finish L2.0.1 thresholding, next step: plotting thresholding reuslts')

#===========================================
# L2.0.2 plots and save
#===========================================
# like mosaic img show
# parameters:
w_fig = 20 # default
ncols = 3  # default
nrows = len(index)
h_fig = w_fig * nrows * (AspectRatio + 0.16) / ncols # 0.2 is the space for title parameters

fig = plt.figure(figsize=(w_fig, h_fig))                 # start plotting
fig.subplots_adjust(hspace= 0, wspace=0.08, right=0.95)
for i in range(1, ncols*len(index)+1):
    k = math.ceil(i/3)-1                                 # trace back index for image selected 
    ax = fig.add_subplot(nrows, ncols, i)                # start subplotting
    
    if i%3 == 1: # column 1, utilizing period nature of this subplot
        im = ax.imshow(img[index[k]+2], cmap=colormap, aspect=aspect, interpolation='none')
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_title(str(index[k]) + '_ion image', pad=8, fontsize = 15)
        
    if i%3 == 2: # column 2, utilizing period nature of this subplot
        intensity_cutoff_999 = pixel[:,index[k]+2][np.argsort(pixel[:,index[k]+2])[index_999]]
        # plot histogram
        (n, bins, patches) = ax.hist(img[index[k]+2].ravel(), bins=500)     # hard coding
        ax.set_ylim(0,np.sort(n)[-5]*1.5)                                   # hard coding
        ax.set_xlim(-0.0001, intensity_cutoff_999)
        ax.set_aspect(intensity_cutoff_999/(np.sort(n)[-5]*1.5)*0.6)       # set aspect ratio for single pixel. (xlim/ylim)*factor
        # cutting lines
        for j in range(n_classes-1):
            ax.axvline(x=img_thresholds[:,k][j], linewidth=1.5, ymin=0, ymax=100, c='r')
            ax.set_xlabel('Normalized ion intensity', fontsize = 10)
            #ax.set_ylabel('Counts', fontsize = 15) # to save some space
        ax.set_title(str(index[k]) + '_ion image histogram', pad=8, fontsize = 15)
        
    if i%3 == 0: # column 3, utilizing period nature of this subplot
        im_seg = ax.imshow(img_segs[k], cmap=colormap_thresholding, aspect=aspect,vmin = 0, vmax=11, interpolation='none')
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_title(str(index[k]) + '_ion image segments', pad=8, fontsize = 15) 
# color bar
cbar_ax = fig.add_axes([0.96,0.1,0.01,0.8])
cbar = fig.colorbar(im_seg, cax=cbar_ax, ticks=[0.5,1.4,2.3,3.2,4.1,5,5.9,6.85,7.8,8.7,9.6,10.5, 11.4])
cbar.ax.set_yticklabels([0,1,2,3,4,5,6,7,8,9,10,11,12]) #hard code 
cbar.ax.tick_params(labelsize=15)

SaveDir = OutputFolder + '\\univariate thresholding analysis.png'
plt.savefig(SaveDir, dpi=dpi)
plt.close()

print('Finish L2.0.2 plotting, next step: interactive visualization')

#===========================================
# L2.0.2 interactive visualization
#===========================================
# omit some parameter defines 
w_fig = 20 # default
ncols = 3  # default
nrows = len(index)
h_fig = w_fig * nrows * (AspectRatio + 0.16) / ncols # 0.2 is the space for title parameters
# omit fig define, since these objects are in caches 

# initiate tk
root = tk.Tk()
root.title('ensemble clustering result')
frame = tk.Frame(root) 
frame.pack(expand = True, fill = tk.BOTH) 

fig = plt.figure(figsize=(w_fig, h_fig))                 # start plotting
fig.subplots_adjust(hspace= -0.2, wspace=0.08, right=0.95)
for i in range(1, ncols*len(index)+1):
    k = math.ceil(i/3)-1                                 # trace back index for image selected 
    ax = fig.add_subplot(nrows, ncols, i)                # start subplotting
    
    if i%3 == 1: # column 1, utilizing period nature of this subplot
        im = ax.imshow(img[index[k]+2], cmap=colormap, aspect=aspect, interpolation='none')
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_title(str(index[k]) + '_ion image', pad=5, fontsize = 10)
        
    if i%3 == 2: # column 2, utilizing period nature of this subplot
        intensity_cutoff_999 = pixel[:,index[k]+2][np.argsort(pixel[:,index[k]+2])[index_999]]
        # plot histogram
        (n, bins, patches) = ax.hist(img[index[k]+2].ravel(), bins=500)     # hard coding
        ax.set_ylim(0,np.sort(n)[-5]*1.5)                                   # hard coding
        ax.set_xlim(-0.0001, intensity_cutoff_999)
        ax.set_aspect(intensity_cutoff_999/(np.sort(n)[-5]*1.5)*0.6)       # set aspect ratio for single pixel. (xlim/ylim)*factor
        # cutting lines
        for j in range(n_classes-1):
            ax.axvline(x=img_thresholds[:,k][j], linewidth=1.5, ymin=0, ymax=100, c='r')
            ax.set_xlabel('Normalized ion intensity', fontsize = 10)
            ax.tick_params(axis='x', labelsize=5)
            ax.tick_params(axis='y', labelsize=5)
        ax.set_title(str(index[k]) + '_ion image histogram', pad=5, fontsize = 10)
        
    if i%3 == 0: # column 3, utilizing period nature of this subplot
        im_seg = ax.imshow(img_segs[k], cmap=colormap_thresholding, aspect=aspect,vmin = 0, vmax=11, interpolation='none')
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_title(str(index[k]) + '_ion image segments', pad=5, fontsize = 10) 
# color bar
cbar_ax = fig.add_axes([0.96,0.1,0.01,0.8])
cbar = fig.colorbar(im_seg, cax=cbar_ax, ticks=[0.5,1.4,2.3,3.2,4.1,5,5.9,6.85,7.8,8.7,9.6,10.5, 11.4])
cbar.ax.set_yticklabels([0,1,2,3,4,5,6,7,8,9,10,11,12]) #hard code 
cbar.ax.tick_params(labelsize=15)

# scrollbars
vbar=tk.Scrollbar(frame,orient=tk.VERTICAL)

# embed and configurate the canvas
canvas=FigureCanvasTkAgg(fig, master=frame)
canvas.get_tk_widget().config(bg='#FFFFFF',scrollregion=(0,0,0,(canvas_width_L2+200)/ncols*nrows))  # these 2 are keys, one defines the region your scroll can reach
canvas.get_tk_widget().config(width=canvas_width_L2,height=canvas_width_L2/ncols*nrows)                    # one defines the size canvas can show.(this is like root geometry I previously set, width is more important)
canvas.get_tk_widget().config(yscrollcommand=vbar.set)                        # makes the scroll region setting solid
canvas.get_tk_widget().grid(row=0, column=0, sticky=tk.W+tk.E+tk.N+tk.S) # organize the geometry

# add cursor
cursor = mplcursors.cursor(fig, hover=True)

vbar.grid(row=0, column=1, sticky=tk.N+tk.S)
vbar.config(command=canvas.get_tk_widget().yview)  # this makes scrollbar work

frame.rowconfigure( 0, weight=1 )    
frame.columnconfigure( 0, weight=1 )

tk.mainloop()
plt.close() 

