
import subprocess
from .nodestdreader import NodeStdReader

# runs a Node sub-process and starts a NodeStdReader thread
# to listen to its stdout.
class Npm:

    # run a JavaScript script (path) with "node"
    def __init__(self, module):

        # create sub-process
        self.ps = subprocess.Popen( ('npm', module), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        print("npm process id", self.ps.pid)

        # create thread to read this process's output          
        t = NodeStdReader(self.ps)
