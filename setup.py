"""
Setup script
"""
import os
from distutils.core import setup

def read(filename):
    """ Reads file
    """
    return open(os.path.join(os.path.dirname(__file__), filename)).read()

VERSION = '0.4.6'
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
    scripts=[
        'scripts/tracktotrip_util',
        'scripts/tracktotrip_build_classifier',
        'scripts/tracktotrip_geolife_dataset'
    ],
    install_requires=read('requirements.txt').split('\n')
)
