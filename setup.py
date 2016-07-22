"""
Setup script
"""
from distutils.core import setup

REQS = [
    'numpy==1.11.0',
    'pandas==0.18.1',
    'pykalman==0.9.5',
    'python-dateutil==2.5.3',
    'pytz==2016.4',
    'Rtree==0.8.2',
    'scikit-learn==0.17.1',
    'scipy==0.17.1',
    'six==1.10.0',
    'sklearn==0.0',
    'ikalman',
    'changepy'
]

setup(
    name='tracktotrip',
    packages=['tracktotrip'],
    version='0.2',
    description='Track processing library',
    author='Rui Gil',
    author_email='ruipgil@gmail.com',
    url='https://github.com/ruipgil/TrackToTrip',
    download_url='https://github.com/ruipgil/TrackToTrip/archive/master.zip',
    keywords=['track', 'trip', 'GPS', 'GPX'],
    classifiers=[],
    install_requires=REQS
)
