"""
Setup script
"""
import os
from distutils.core import setup

def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()

VERSION='0.3.4'
setup(
    name='tracktotrip',
    packages=['tracktotrip'],
    version=VERSION,
    description='Track processing library',
    author='Rui Gil',
    author_email='ruipgil@gmail.com',
    url='https://github.com/ruipgil/TrackToTrip',
    download_url='https://github.com/ruipgil/TrackToTrip/releases/tag/%s' % VERSION,
    keywords=['track', 'trip', 'GPS', 'GPX'],
    classifiers=[],
    install_requires=read('requirements.txt').split('\n')
)
