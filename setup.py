"""
Setup script
"""
import os
from distutils.core import setup

def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()

setup(
    name='tracktotrip',
    packages=['tracktotrip'],
    version='0.3',
    description='Track processing library',
    author='Rui Gil',
    author_email='ruipgil@gmail.com',
    url='https://github.com/ruipgil/TrackToTrip',
    download_url='https://github.com/ruipgil/TrackToTrip/archive/master.zip',
    keywords=['track', 'trip', 'GPS', 'GPX'],
    classifiers=[],
    install_requires=read('requirements.txt').split('\n')
)
