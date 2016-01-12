from setuptools import setup

setup(name='TrackToTrip',
      version='0.0.1',
      description='GPS processing library',
      url='http://github.com/ruipgil/TrackToTrip',
      author='Rui Gil',
      author_email='ruipgil@gmail.com',
      license='MIT',
      packages=['TrackToTrip'],
      install_requires=[
          'gpxpy',
          'numpy',
          'pykalman',
          'sklearn'
      ],
      zip_safe=False)
