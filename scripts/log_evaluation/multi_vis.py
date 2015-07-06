import VisualiseProfileData as vpd
import os 

outfilename = "compare_file_systems.html"

folders = [
'/home/qmm55171/Documents/temp_docs/Profiling/process12'
]
#'/dls/science/users/qmm55171/final_logs/new_mpi_params/no_chunking/average_stats'
#]

multi_frames = []
for folder in folders:
    all_files = vpd.get_files(folder)
    sub_files = [f for f in all_files if 'stats' in f ]
    frame = vpd.convert(sub_files)
    path = os.path.dirname(sub_files[0])
    frame['link'] = [('file://'+ path + '/' + os.path.basename(sub).split('_stats')[0] + '.html') for sub in sub_files]
    multi_frames.append(frame)

#params = {'File system': 'lustre01', 'Chunk': 'false', 'Process': '01', 'Data size': '(91,135,160)'}
params = {'Process': '12', 'Data size': '(91,135,160)'}


#         'Original MPI parameters', 
#         'New MPI parameters'
#         ]


#==================== Filter frames here if necessary =========================

# filter dataframes here #

filter_frames = []
#fsystem = ['chunksOFF', 'chunksTrue', 'chunks1x68x160']
temp = multi_frames[0]
fsystem = temp.groupby('file_system').first()
fsystem = fsystem.index.values
for i in range(len(fsystem)):
    filter_frames.append(temp[temp.file_system == fsystem[i]])

title = [f for f in fsystem]

#multi_frames = [f[f.file_system == 'lustre03'] for f in multi_frames]

#==================== Filter frames here ======================================

max_std = [f.Std_time.max() for f in filter_frames]

multi_frames = [frame.values.tolist() for frame in filter_frames]    
#multi_frames = [frame.values.tolist() for frame in multi_frames]

size = [(85, 85), (100, 100)] # size of page, size of subplot (%)
header_shift = 4;
vpd.render_template(multi_frames, outfilename, title, size, params, header_shift, max(max_std))

