import pandas


def evaluate(selected_data):
    starts = selected_data[selected_data[5].str.startswith("Start::")]
    ends = selected_data[selected_data[5].str.startswith("Finish::")]

    summed = {}
    count = {}

    for i in range(len(starts)):
        start = starts[i:i+1]
        aa = ends[ends[1] >= start[1].base[0]]
        key = start[5].base[0].split("Start::")[1].strip()
        end = aa[aa[5].str.contains(key)]
        if key not in summed:
            summed[key] = 0
            count[key] = 0
        elapsed = end[1].base[0] - start[1].base[0]
        summed[key] += elapsed
        count[key] += 1
    return (summed, count)


#def process_file(filename="../../test_data/trimmed_out.log"):
def process_file(filename="log_mpi_test.o8612338"):
    data = pandas.io.parsers.read_fwf(filename, widths=[2, 13, 5, 5, 6, 1000], header=None)
    machinepds = {}
    for machine in data[2].unique():
        threadpds = {}
        for thread in data[3].unique():
            sel = data[data[2] == machine][data[3] == thread][data[4] == "INFO"]
            (summed, count) = evaluate(sel)
            combined_data = zip(summed.keys(), summed.values(), count.values())
            df = pandas.DataFrame(data = combined_data, columns=['function', 'total_time','num_calls'])
            df = df.set_index('function')
            threadpds[thread] = df
        machinepds[machine] = pandas.concat(threadpds)
    result = pandas.concat(machinepds)
    result.index = result.index.reorder_levels((2, 0, 1))
    return result.sort_index(0)

df = process_file()
pandas.set_option('display.height',1000)
pandas.set_option('display.max_rows',1000)
print df
