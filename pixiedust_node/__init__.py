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
from IPython.display import display, HTML
import warnings
from .node import Node, Npm
import os
from pixiedust.utils.shellAccess import ShellAccess

# pixiedust magics to interpret cells starting with %%node
@magics_class
class PixiedustNodeMagics(Magics):

    def __init__(self, shell):
        super(PixiedustNodeMagics,self).__init__(shell=shell) 
        display(HTML(
"""
            <div style="margin:10px"> 
            <a href="https://github.com/ibm-cds-labs/pixiedust_node" target="_new"> 
            <img src="https://github.com/ibm-cds-labs/pixiedust_node/raw/master/docs/_images/pdn_icon32.png" style="float:left;margin-right:10px"/> 
            </a> 
            <span>Pixiedust Node.js</span> 
            </div> 
"""
        ))
        # create Node.js sub-process
        path = os.path.join(__path__[0], 'pixiedustNodeRepl.js')
        self.n = Node(path)
        ShellAccess.npm = Npm()
        ShellAccess.node = self.n

    @cell_magic
    def node(self, line, cell):
        # write the cell contents to the Node.js process
        self.n.write(cell)


try:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        get_ipython().register_magics(PixiedustNodeMagics)
except NameError:
    # IPython not available we must be in a spark executor\
    pass
