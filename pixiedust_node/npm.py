
import subprocess

# npm helper
# allows npm modules to be installed, removed and listed
class Npm:

    # run an npm command
    def cmd(self, command, module):
        # create sub-process
        args = ['npm', command, '-s']
        if (module):
            if (isinstance(module, str)):
                args.append(module)
            else:
                args.extend(module)
        print ' '.join(args)
        output = subprocess.check_output(args)
        print output

    def install(self, module):
        self.cmd('install', module)

    def remove(self, module):
        self.cmd('remove', module)

    def list(self):
        self.cmd('list', None)
