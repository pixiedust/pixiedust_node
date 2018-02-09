from setuptools import setup, find_packages

setup(name='pixiedust_node',
      version='0.2.3',
      description='Pixiedust extension for Node.js',
      url='https://github.com/ibm-watson-data-lab/pixiedust_node',
      install_requires=['pixiedust', 'pandas', 'ipython'],
      package_data={
        '': ['*.js','*.json']
      },
      author='David Taieb, Glynn Bird',
      author_email='david_taieb@us.ibm.com, glynn.bird@gmail.com',
      license='Apache 2.0',
      packages=find_packages(),
      include_package_data=False,
      zip_safe=False)
