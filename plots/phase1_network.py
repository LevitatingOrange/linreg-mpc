from matplotlib import rc, pyplot as plt
import numpy as np
import os
import sys
import json

ns = [i * 10**j for j in [3,4,5] for i in [1,2,5]] + [1000000]
ds = [10, 20, 50, 100, 200]#500]
num_samples = 1
ps = [2,3,5]#[1, 2, 5, 10, 20]

# n x d x num_parties x sample x party -> (cputime, waittime, realtime, bytes sent, flush count)
data = np.zeros((len(ns), len(ds), len(ps), num_samples, max(ps)+2, 5), dtype=np.float64)
data[:] = np.NAN

for i_n, n in enumerate(ns):
    for i_d, d in enumerate(ds):
        for i_p, num_parties in enumerate(ps):
            for sample in xrange(num_samples):
                for party in xrange(num_parties+2): 
                    try:
                        filename = "../experiments/results/phase1_network/test_LR_{}x{}_{}_{}_p{}.out".format(n, d, num_parties, sample, party+1)
                        lines = open(filename).read().splitlines()
                        if party == 0:
                            lines = lines[1:] # ignore first line for CSP (contains only info we already know)
                        current_data = json.loads(lines[0]) # TODO make sure that the times are on the first line
                        data[i_n, i_d, i_p, sample, party, :3] = [current_data[key] for key in ['cputime', 'wait_time', 'realtime']]
                        data[i_n, i_d, i_p, sample, party, 3] = np.sum(np.fromstring(lines[1][1:-1], sep=',')) # bytes sent
                    except IOError, e:
                        #pass
                         print e

            
# thanks http://stackoverflow.com/a/1094933
def sizeof_fmt(num, suffix='B'):
    for unit in ['', '\kibi', '\mebi', '\gibi', '\tebi']:
    #for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
    # for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f \si{%s%s}" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)
            
# bytes sent
print "\n"
for i_n, n in enumerate(ns):
    sys.stdout.write("\midrule\n\\multirow{%d}{*}{%d}\n" % (len(ds),n))
    for i_d, d in enumerate(ds):
        #if i_d != 0:
        #    sys.stdout.write(10 * " ")
        sys.stdout.write("& {:<10d} & {:10}".format(d, sizeof_fmt(n * d * 8, suffix='\\byte'),))
        for i_p, num_parties in enumerate(ps):
            bytes_ti = np.nanmean(data[i_n, i_d, i_p, :, 0, 3])
            bytes_parties = np.nanmean(data[i_n, i_d, i_p, :, 2:, 3])
            sys.stdout.write("& {:10} & {:10}".format(
                    sizeof_fmt(bytes_ti, suffix='\\byte'), 
                    sizeof_fmt(bytes_parties, suffix='\\byte')))
        sys.stdout.write("\\\\\n")
            
