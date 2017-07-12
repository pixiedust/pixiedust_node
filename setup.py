from setuptools import setup, find_packages

setup(name='pixiedust_node',
      version='0.1.2',
      description='Pixiedust extension for Node.js',
      url='https://github.com/ibm-cds-labs/pixiedust_node',
      install_requires=['pixiedust'],
      package_data={
        '': ['*.js','*.json']
      },
      author='David Taieb, Glynn Bird',
      author_email='david_taieb@us.ibm.com, glynn.bird@gmail.com',
      license='Apache 2.0',
      packages=find_packages(),
      include_package_data=False,
      zip_safe=False)
