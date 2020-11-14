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
df_pixel_label = pd.read_csv(EnOutputDir)

print('Finish pixel raw data import')

#===========================================
# L3.1 data process
#===========================================
pixel_label = df_pixel_label.values.astype(int)

# parse dimension
NumLine = np.max(pixel_label[:,0])+1
NumSpePerLine = np.max(pixel_label[:,1])+1
# parameter for plotting
aspect = AspectRatio*NumSpePerLine/NumLine
# relabel pixels

# organize img
img = pixel_label.T.reshape(pixel_label.shape[1], NumLine, NumSpePerLine)

# make folders for multivariate analysis
OutputFolder = locate_OutputFolder2(EnOutputDir)
OutputFolder = locate_OutputFolder3(OutputFolder, 'final segmentation')
os.mkdir(OutputFolder)

print('Finish L3.1 data process')

#===========================================
# L3.1 ensemble results in mosaic plot, save images 
#===========================================
# mosaic img show
# parameters:
w_fig = 20 # default setting
ncols = ncols_L1
nrows = math.ceil((img.shape[0]-2)/ncols)
h_fig = w_fig * nrows * (AspectRatio + 0.16) / ncols # 0.2 is the space for title parameters
columns = df_pixel_label.columns.values

fig = plt.figure(figsize=(w_fig, h_fig))
fig.subplots_adjust(hspace= 0, wspace=0.01, right=0.95)
for i in range(1, img.shape[0]-1):
    ax = fig.add_subplot(nrows, ncols, i)
    im = ax.imshow(img[i+1], cmap=cm.tab20, aspect = aspect, vmin=0,vmax=19)
    ax.set_xticks([])
    ax.set_yticks([])
    
    # title
    title = columns[i+1]
    ax.set_title(title, pad=8, fontsize = 15)

# colorbar
cbar_ax = fig.add_axes([0.96,0.1,0.01,0.8])
cbar = fig.colorbar(im, cax=cbar_ax, ticks=[0.5,1.4,2.3,3.3,4.3,5.1,6.2,7,8.1,9,10,10.9,11.8,12.7,13.6,14.7,15.6,16.6,17.5,18.5])
cbar.ax.set_yticklabels([0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19]) #hard code 
cbar.ax.tick_params(labelsize=10)

SaveDir = OutputFolder + '\\ensemble_result_plot.png'
plt.savefig(SaveDir, dpi=dpi)
plt.close()

print('Finish L3.1 ensemble result plotting, next step: interactive visualization')

#===========================================
# L3.1 ensemble results embed in tk.
#===========================================
# mosaic img show
# parameters for plt.plot:
w_fig = 20 # default setting
ncols = ncols_L3
nrows = math.ceil((img.shape[0]-2)/ncols)
h_fig = w_fig * nrows * (AspectRatio + 0.16) / ncols # 0.2 is the space for title parameters
columns = df_pixel_label.columns.values
# parameters for tk window
canvas_width = canvas_width

# initiate tk
root = tk.Tk()
root.title('ensemble clustering result')
frame = tk.Frame(root) 
frame.pack(expand = True, fill = tk.BOTH) 

fig = mtl.figure.Figure(figsize=(w_fig, h_fig))
fig.subplots_adjust(hspace= 0, wspace=0.01, right=0.95)
for i in range(img.shape[0]-2):
    ax = fig.add_subplot(nrows, ncols, i+1)
    im = ax.imshow(img[i+2], cmap=cm.tab20, aspect = aspect, vmin=0,vmax=19)
    ax.set_xticks([])
    ax.set_yticks([])
    
    # title
    title = columns[i+2]    # first 2 columns are spatial index
    ax.set_title(title, pad=5, fontsize = 10)

# colorbar
cbar_ax = fig.add_axes([0.96,0.1,0.01,0.8])
cbar = fig.colorbar(im, cax=cbar_ax, ticks=[0.5,1.4,2.3,3.3,4.3,5.1,6.2,7,8.1,9,10,10.9,11.8,12.7,13.6,14.7,15.6,16.6,17.5,18.5])
cbar.ax.set_yticklabels([0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19]) #hard code 
cbar.ax.tick_params(labelsize= 10)

# add cursor
cursor = mplcursors.cursor(fig, hover=True)

# scrollbars
vbar=tk.Scrollbar(frame,orient=tk.VERTICAL)

# embed and configurate the canvas
canvas=FigureCanvasTkAgg(fig, master=frame)
canvas.get_tk_widget().config(bg='#FFFFFF',scrollregion=(0,0,0,(canvas_width+200)/ncols*nrows))  # these 2 are keys, one defines the region your scroll can reach
canvas.get_tk_widget().config(width=canvas_width,height=canvas_width/ncols*nrows)                    # one defines the size canvas can show.(this is like root geometry I previously set, width is more important)
canvas.get_tk_widget().config(yscrollcommand=vbar.set)                 # makes the scroll region setting solid
canvas.get_tk_widget().grid(row=0, column=0, sticky=tk.W+tk.E+tk.N+tk.S) # organize the geometry

# add cursor
cursor = mplcursors.cursor(fig, hover=True)

vbar.grid(row=0, column=1, sticky=tk.N+tk.S)
vbar.config(command=canvas.get_tk_widget().yview)  # this makes scrollbar work

frame.rowconfigure( 0, weight=1 )     # You need to add this. 
frame.columnconfigure( 0, weight=1 )

tk.mainloop()