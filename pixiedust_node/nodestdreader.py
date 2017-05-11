from pixiedust.display import *
from pixiedust.utils.shellAccess import ShellAccess
from threading import Thread
import IPython
import json
import pandas

# a thread that is given a process in the contructor
# the thead listens to each line coming out of the
# process's stdout and checks to see if it is JSON.
# if it is, and it's a special Pixiedust command,
# then the pixiedust display/print function is called
class NodeStdReader(Thread):   

    # the process to read stdout from     
    ps = None

    def __init__(self, ps):
        super(NodeStdReader, self).__init__() 
        self.ps = ps
        self.daemon = True
        self.start()

    def run(self):
        
        # forever
        while(True):
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
                        variable = 'pdf'
                        if 'variable' in obj:
                            variable = obj['variable']
                        ShellAccess[variable] = pandas.DataFrame(obj['data'])
                    elif obj['type'] == 'html':
                        IPython.display.display(IPython.display.HTML(obj['data']))
                    elif obj['type'] == 'image':
                        IPython.display.display(IPython.display.HTML('<img src="{0}" />'.format(obj['data'])))
  
            except Exception as e:
                print(line)
                print(e)