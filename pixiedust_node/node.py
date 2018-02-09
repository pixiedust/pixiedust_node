
import json
import os
import sys
import platform
import subprocess
from functools import partial
from threading import Thread, Event

import IPython
import pandas
from pixiedust.display import display
from pixiedust.utils.environment import Environment
from pixiedust.utils.shellAccess import ShellAccess

RESERVED = ['true', 'false','self','this','In','Out']

try:
    VARIABLE_TYPES = (str, int, float, bool, unicode, dict, list)
except:
    # Python 3 => no unicode type
    VARIABLE_TYPES = (str, int, float, bool, dict, list)

class VarWatcher(object):
    """
    this class watches for cell "post_execute" events. When one occurs, it examines
    the IPython shell for variables that have been set (only numbers and strings).
    New or changed variables are moved over to the JavaScript environment.
    """

    def __init__(self, ip, ps):
        self.shell = ip
        self.ps = ps
        ip.events.register('post_execute', self.post_execute)
        self.clearCache()

    def clearCache(self):
        self.cache = {}

    def post_execute(self):
        for key in self.shell.user_ns:
            v = self.shell.user_ns[key]
            t = type(v)
            # if this is one of our varables, is a number or a string or a float
            if not key.startswith('_') and (not key in RESERVED) and (t in VARIABLE_TYPES):
                # if it's not in our cache or it is an its value has changed
                if not key in self.cache or (key in self.cache and self.cache[key] != v):
                    # move it to JavaScript land and add it to our cache
                    self.ps.stdin.write("var " + key + " = " + json.dumps(v) + ";\r\n")
                    self.cache[key] = v

class NodeStdReader(Thread):
    """
    Thread class that is given a process in the constructor
    the thead listens to each line coming out of the
    process's stdout and checks to see if it is JSON.
    if it is, and it's a special Pixiedust command,
    then the pixiedust display/print function is called
    """

    def __init__(self, ps):
        super(NodeStdReader, self).__init__()
        self._stop_event = Event()
        self.ps = ps
        self.daemon = True
        self.start()

    def stop(self):
        self._stop_event.set()

    def run(self):

        # forever
        while not self._stop_event.is_set():
            # read line from Node's stdout
            line = self.ps.stdout.readline()

            # see if it parses as JSON
            obj = None
            try:
                if line:
                    obj = json.loads(line)
            except Exception as e:
                # output the original line when we don't have JSON
                line = line.strip()
                if len(line) > 0:
                    print(line)

            try:
                # if it does and is a pixiedust object
                if obj and obj['_pixiedust']:
                    if obj['type'] == 'display':
                        pdf = pandas.DataFrame(obj['data'])
                        ShellAccess.pdf = pdf
                        display(pdf)
                    elif obj['type'] == 'print':
                        print(json.dumps(obj['data']))
                    elif obj['type'] == 'store':
                        print('!!! Warning: store is now deprecated - Node.js global variables are automatically propagated to Python !!!')
                        variable = 'pdf'
                        if 'variable' in obj:
                            variable = obj['variable']
                        ShellAccess[variable] = pandas.DataFrame(obj['data'])
                    elif obj['type'] == 'html':
                        IPython.display.display(IPython.display.HTML(obj['data']))
                    elif obj['type'] == 'image':
                        IPython.display.display(IPython.display.HTML('<img src="{0}" />'.format(obj['data'])))
                    elif obj['type'] == 'variable':
                        ShellAccess[obj['key']] = obj['value']
 

            except Exception as e:
                print(line)
                print(e)


class NodeBase(object):
    """
    Node base class with common tasks for Node.js and NPM process runs.
    """
    @staticmethod
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    @staticmethod
    def which(program):
        fpath, fname = os.path.split(program)
        if fpath:
            if NodeBase.is_exe(program):
                return program
        else:
            for path in os.environ["PATH"].split(os.pathsep):
                path = path.strip('"')
                exe_file = os.path.join(path, program)
                if NodeBase.is_exe(exe_file):
                    return exe_file

        return None

    def __init__(self):
        """
        Establishes the Node's home directories and executable paths
        """
        # get the home directory
        home = Environment.pixiedustHome

        # Node home directory
        self.node_home = os.path.join(home, 'node')
        if not os.path.exists(self.node_home):
            os.makedirs(self.node_home)

        # Node modules home directory
        self.node_modules = os.path.join(self.node_home, 'node_modules')
        if not os.path.exists(self.node_modules):
            os.makedirs(self.node_modules)

        self.node_prog = 'node'
        self.npm_prog = 'npm'
        if platform.system() == 'Windows':
            self.node_prog += '.exe'
            self.npm_prog += '.cmd'

        self.node_path = NodeBase.which(self.node_prog)
        if self.node_path is None:
            print('ERROR: Cannot find Node.js executable')
            raise FileNotFoundError('node executable not found in path')

        self.npm_path = NodeBase.which(self.npm_prog)
        if self.npm_path is None:
            print('ERROR: Cannot find npm executable')
            raise FileNotFoundError('npm executable not found in path')

        # Create popen partial, that will be used later
        popen_kwargs = {
            'stdin': subprocess.PIPE,
            'stdout': subprocess.PIPE,
            'stderr': subprocess.STDOUT,
            'cwd': self.node_home
        }
        if sys.version_info.major == 3:
            popen_kwargs['encoding'] = 'utf-8'
        self.popen = partial(subprocess.Popen, **popen_kwargs)


class Node(NodeBase):
    """
    Class runs a Node sub-process and starts a NodeStdReader thread
    to listen to its stdout.
    """
    def __init__(self, path):
        """
        Constructor runs a JavaScript script (path) with "node"
        :param path: JavaScript path
        """
        super(Node, self).__init__()

        # process that runs the Node.js code
        args = (self.node_path, path)
        self.ps = self.popen(args)
        print ("Node process id", self.ps.pid)

        # create thread to read this process's output
        NodeStdReader(self.ps)

        # watch Python variables for changes
        self.vw = VarWatcher(get_ipython(), self.ps)

    def terminate(self):
        self.ps.terminate()

    def write(self, s):
        self.ps.stdin.write(s)
        self.ps.stdin.write("\r\n")
        self.ps.stdin.flush()

    def cancel(self):
        self.write("\r\n.break")

    def clear(self):
        self.write("\r\n.clear")
        self.vw.clearCache()

    def help(self):
        self.cancel()
        self.write("help()\r\n")


class Npm(NodeBase):
    """
    npm helper class
    allows npm modules to be installed, removed and listed
    """
    def __init__(self):
        super(Npm, self).__init__()

    # run an npm command
    def cmd(self, command, module):
        args = [self.npm_path, command, '-s']
        if module:
            if isinstance(module, str):
                args.append(module)
            else:
                args.extend(module)
        print(' '.join(args))
        ps = self.popen(args)

        # create thread to read this process's output
        t = NodeStdReader(ps)

        # wait for the sub-process to exit
        ps.wait()

        # tell the thread reading its output to stop too, to prevent 100% CPU usage
        t.stop()

    def install(self, module):
        self.cmd('install', module)

    def remove(self, module):
        self.cmd('uninstall', module)

    def uninstall(self, module):
        self.cmd('uninstall', module)

    def list(self):
        self.cmd('list', None)



