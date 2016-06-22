from distutils.core import setup

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
  name = 'tracktotrip',
  packages = ['tracktotrip'],
  version = '0.1.2',
  description = 'Track processing library',
  author = 'Rui Gil',
  author_email = 'ruipgil@gmail.com',
  url = 'https://github.com/ruipgil/TrackToTrip',
  download_url = 'https://github.com/ruipgil/TrackToTrip/archive/master.zip',
  keywords = ['track', 'trip', 'GPS', 'GPX'],
  classifiers = [],
  install_requires=required,
)
