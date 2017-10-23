
import subprocess
import os
from .nodestdreader import NodeStdReader
from pixiedust.utils.environment import Environment

# npm helper
# allows npm modules to be installed, removed and listed
class Npm:

    # run an npm command
    def cmd(self, command, module):
        # create node_modules
        home = Environment.pixiedustHome
        node_home = os.path.join(home,'node')
        node_modules = os.path.join(node_home,'node_modules')
        if not os.path.exists(node_modules):
            os.makedirs(node_modules)

        # create sub-process
        npm_path = self.which('npm')
        args = [npm_path, command, '-s']
        if (module):
            if (isinstance(module, str)):
                args.append(module)
            else:
                args.extend(module)
        print (' '.join(args))
        ps = subprocess.Popen( args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd = node_home)
        
        # create thread to read this process's output          
        t = NodeStdReader(ps)
        ps.wait()

    def install(self, module):
        self.cmd('install', module)

    def remove(self, module):
        self.cmd('uninstall', module)

    def uninstall(self, module):
        self.cmd('uninstall', module)

    def list(self):
        self.cmd('list', None)

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
