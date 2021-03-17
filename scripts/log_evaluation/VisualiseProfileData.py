from . import GraphicalThreadProfiler as GTP
from . import GraphicalThreadProfiler_multi as GTP_m
import fnmatch
import os


def convert(files):
    import pandas as pd
    # calculate the mean and std

    test = []
    index = ['file_system', 'nNodes_x_nCores', 'Mean_time', 'nNodes',
             'Std_time']
    for file in files:
        temp_frame = pd.read_csv(file, header=None)
        a = (file.split('/')[-1]).split('_')

        vals = pd.Series([a[3],
                         int(a[-6].split('N')[1])*int(a[-5].split('C')[1]),
                         int(temp_frame.iloc[1, 1])*0.001,
                         int(a[-6].split('N')[1]),
                         int(temp_frame.iloc[2, 1])*0.001], index=index)
        test.append(vals)

    all_vals = (pd.concat(test, axis=1).transpose())

    frame = all_vals

    return frame


def get_files(dir_path):
    from os import listdir
    from os.path import isfile, join

    all_files = [f for f in listdir(dir_path) if isfile(join(dir_path, f))]
    files = [(dir_path + '/' + f) for f in all_files]

    return files


def render_template(frame, outfilename, title, size, params, header_shift,
                    max_std):
    from jinja2 import Template
    from . import template_strings as ts

    nVals = len(frame)

    f_out = open(outfilename, 'w')
    template = Template(ts.set_template_string_vis(nVals, title, size, params,
                                                   header_shift))

    style = os.path.dirname(__file__) + '/style_sheet.css'
    print(outfilename)
    f_out.write(template.render(frame=[list(map(list, f)) for f in frame],
                                style_sheet=style, max_bubble=max_std))
    f_out.close()

    return


def convert_all_files():
    all_files = get_files(os.getcwd())
    single_files = [f for f in all_files if f.split('.')[-1][0] == 'o']
    GTP.convert(single_files)

    wildcard_files = [(os.path.dirname(f) + '/' +
                       os.path.basename(f).split('.')[-2] + '*')
                      for f in single_files]
    for wildcard in set(wildcard_files):
        matching_files = []
        for file in single_files:
            if fnmatch.fnmatch(file, wildcard):
                matching_files.append(file)
        GTP_m.convert(matching_files)

    create_bubble_chart(get_files(os.getcwd()))


def create_bubble_chart(all_files):

    stats_files = [f for f in all_files if 'stats.csv' in f]
    frame = convert(stats_files)

    max_std = frame.Std_time.max()

    frame['link'] = [('file://' + f.split('_stats')[0] + '.html')
                     for f in stats_files]

    size = [(70, 70), (100, 100)]
    #params = {}
    params = {'Chunk': 'false', 'Process': '12', 'Data size': '(91,135,160)'}
    render_template([frame.values.tolist()], 'analysis.html', ['Nodes'], size,
                    params, 0, max_std)


if __name__ == "__main__":
    import optparse
    usage = "%prog [options] input_file"

    parser = optparse.OptionParser(usage=usage)

    (options, args) = parser.parse_args()

    if len(args) == 1:
        filename = (os.getcwd() if args[0] == '.' else args[0])
        create_bubble_chart(get_files(filename))
    else:
        convert_all_files()
