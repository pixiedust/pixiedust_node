# -------------------------------------------------------------------------------
# Copyright IBM Corp. 2017
# 
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
# http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed unde
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# -------------------------------------------------------------------------------

from IPython.core.magic import (Magics, magics_class, cell_magic)
import warnings
from .node import Node
from .npm import Npm
import os

# pixiedust magics to interpret cells starting with %%node
@magics_class
class PixiedustNodeMagics(Magics):

    def __init__(self, shell):
        super(PixiedustNodeMagics,self).__init__(shell=shell) 
        # create Node.js sub-process
        path = os.path.join(__path__[0], 'pixiedustNodeRepl.js')
        self.n = Node(path)

    @cell_magic
    def node(self, line, cell):
        # write the cell contents to the Node.js process
        self.n.write(cell)

    def npm(self, module):
        n = Npm(module)

    def cancel(self):
        self.n.write("\r\n.break\r\n")

    def clear(self):
        self.n.write("\r\n.clear\r\n")
 
try:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        get_ipython().register_magics(PixiedustNodeMagics)
except NameError:
    #IPython not available we must be in a spark executor\
    pass