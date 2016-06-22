from distutils.core import setup
from pip.req import parse_requirements

install_reqs = parse_requirements('./requirements.txt', session=False)
reqs = [str(ir.req) for ir in install_reqs]

setup(
  name = 'tracktotrip',
  packages = ['tracktotrip'],
  version = '0.1.4',
  description = 'Track processing library',
  author = 'Rui Gil',
  author_email = 'ruipgil@gmail.com',
  url = 'https://github.com/ruipgil/TrackToTrip',
  download_url = 'https://github.com/ruipgil/TrackToTrip/archive/master.zip',
  keywords = ['track', 'trip', 'GPS', 'GPX'],
  classifiers = [],
  install_requires=reqs,
)
