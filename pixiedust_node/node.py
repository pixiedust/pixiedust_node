
import subprocess
from .nodestdreader import NodeStdReader

# runs a Node sub-process and starts a NodeStdReader thread
# to listen to its stdout.
class Node:

    # process that runs the Node.js code
    ps = None

    # run a JavaScript script (path) with "node"
    def __init__(self, path):

        # create sub-process
        self.ps = subprocess.Popen( ('node', path), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        print("Node process id", self.ps.pid)

        # create thread to read this process's output          
        t = NodeStdReader(self.ps)

    def write(self, s):
        self.ps.stdin.write(s)
        self.ps.stdin.write("\r\n")