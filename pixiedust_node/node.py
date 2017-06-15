
import subprocess
import os
from .nodestdreader import NodeStdReader

# runs a Node sub-process and starts a NodeStdReader thread
# to listen to its stdout.
class Node:

    # process that runs the Node.js code
    ps = None

    # run a JavaScript script (path) with "node"
    def __init__(self, path):
        # get the home directory
        node = 'node';
        home = get_ipython().home_dir

        # check that node exists
        node_path = self.which(node)

        if node_path == None:
            print 'ERROR: Cannot find Node.js executable'
            raise FileNotFoundError('node executable not found in path')
        else:
            # create sub-process
            self.ps = subprocess.Popen( (node_path, path), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd = home)
            # print ("Node process id", self.ps.pid)

            # create thread to read this process's output          
            t = NodeStdReader(self.ps)


    def is_exe(self, fpath):
       return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    def which(self, program):
        fpath, fname = os.path.split(program)
        if fpath:
            if self.is_exe(program):
                return program
        else:
            for path in os.environ["PATH"].split(os.pathsep):
                path = path.strip('"')
                exe_file = os.path.join(path, program)
                if self.is_exe(exe_file):
                    return exe_file

        return None

    def write(self, s):
        self.ps.stdin.write(s)
        self.ps.stdin.write("\r\n")

    def cancel(self):
        self.write("\r\n.break")

    def clear(self):
        self.write("\r\n.clear")

    def help(self):
        self.cancel()
        self.write("help()\r\n")