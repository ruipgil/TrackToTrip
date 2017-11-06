# TrackToTrip
*TrackToTrip* is a library to process GPS tracks.

The main goals are to transform a (gpx) **track into a trip**.

> **track**
> raw representation of a GPS recording. It is not precise, has noise and valuable information is hidden.


> **trip**
> result of one or more processed tracks. Its start and end points have semantic meaning, such as home, work or school. It has less errors and it's compressed, with as little information loss as possible. In short, a trip is an approximation of the true path recorded.

## Installing

You can install *TrackToTrip* with *[pip](https://pypi.python.org/pypi/tracktotrip)* or *EasyInstall*,

```
pip install tracktotrip
```

or

```
easy_install install tracktotrip
```

**Python 2.x** is required, mainly because of the [ikalman](https://github.com/ruipgil/ikalman) package.

You may want to install the dependencies with *easyinstall* first, to avoid building libraries such as *numpy*.

## Overview

The starting points are the [Track](../master/tracktotrip/track.py), [Segment](../master/tracktotrip/segment.py) and [Point](../master/tracktotrip/point.py) classes.

### [Track](../master/tracktotrip/track.py)

Can be loaded from a GPX file:

````python
from tracktotrip import Track, Segment, Point

track = Track.from_gpx('file_to_track.gpx')
```

A track can be transformed into a trip with the method ` to_trip `. Transforming a track into a trip executes the following steps:

1. Smooths the segments, using the [kalman filter](../master/tracktotrip/smooth.py)

2. Spatiotemporal segmentation for each segment, using the [DBSCAN algorithm](../master/tracktotrip/spatiotemporal_segmentation.py) to find spatiotemporal clusters

3. Compresses every segment, using [spatiotemporal-aware compression algorithm](../master/tracktotrip/compression.py)

A track is composed by ` Segment `s, and each segment by ` Point `s.

It can be saved to a GPX file:

````python
with open('file.gpx', 'w') as f:
  f.write(track.to_gpx())
```

### [Segment](../master/tracktotrip/segment.py)

A Segment holds the points, the transportation modes used, and the start and end semantic locations.

### [Point](../master/tracktotrip/point.py)

A Point holds the position and time. Currently the library doesn't support elevation.

### Other modules

+ [`tracktotrip.classifer.Classifier`](../master/tracktotrip/classifier.py) provides a wrapper around the [sklearn](http://scikit-learn.org/) classifiers.

+ [`tracktotrip.compression`](../master/tracktotrip/compression.py) implements path compression algorithm, such as:
  - ` drp `: Douglas Ramer Peucker Algorithm
  - ` td_sp `: Top-Down Speed-Based Trajectory Compression Algorithm [1]
  - ` td_tr `: Top-Down Time-Ratio Trajectory Compression Algorithm [1]
  - ` spt `: A combination of both `td_sp` and `td_tr` [1]

+ [`tracktotrip.kalman.kalman_filter`](../master/tracktotrip/kalman.py) executes the kalman filter in a list of point

+ [`tracktotrip.learn_trip`](../master/tracktotrip/learn_trip.py) implements
  - ` trip_learn ` used learn trips
  - ` complete_trip ` used to find trips between two points

+ [`tracktotrip.location.infer_location`](../master/tracktotrip/location.py) uses known locations, and web APIs such as Google's and Foursquare's.

+ [`tracktotrip.similarity`](../master/tracktotrip/similarity.py) implements function to find similarity between two ` Segment `s

+ [`tracktotrip.smooth`](../master/tracktotrip/smooth.py) implements functions mitigate kalman's lack of precision in the first predictions

+ [`tracktotrip.spatiotemporal_segmentation.spatiotemporal_segmentation`](../master/tracktotrip/spatiotemporal_segmentation.py) uses the DBSCAN algorithm to perform spatiotemporal segmentation

+ [`tracktotrip.transportation_mode`](../master/tracktotrip/transportation_mode.py) implements transportation learning and prediction functions, such as:
  - `extract_features_2` to extract features from a set of points
  - `learn_transportation_mode` to learn the transportation modes of a track
  - `speed_clustering` implements changepoint segmentation and classifies sub-segments between changepoints

*TrackToTrip* is flexible, with lots of parameters. For general parameters, refer to [` processmysteps.default_config `](https://github.com/ruipgil/ProcessMySteps/blob/master/processmysteps/default_config.py)

[1]: Spatiotemporal Compression Techniques for Moving Point Objects, Nirvana Meratnia and Rolf A. de By, 2004, in Advances in Database Technology - EDBT 2004: 9th International Conference on Extending Database Technology, Heraklion, Crete, Greece, March 14-18, 2004

## Transportation mode classification

For transportation mode classification, TrackToTrip uses a wrapper around sklearn's classifiers. We consider two different classifiers: the [Stochastic Gradient Descent Classifier](http://scikit-learn.org/stable/modules/generated/sklearn.linear_model.SGDClassifier.html#sklearn.linear_model.SGDClassifier), and [CART Decision Tree Classifier](http://scikit-learn.org/stable/modules/generated/sklearn.tree.DecisionTreeClassifier.html#sklearn.tree.DecisionTreeClassifier), both implemented by [sklearn](http://scikit-learn.org/).

To classify a segment (trip) we first do changepoint segmentation, which sub-divides a segment into points where there was a change in mean the absolute velocity difference.
For each sub-segment we then extract features.

Feature extraction is based on cumulative speed, and the amount of time spent at them. We create a [histogram](../master/docs/histogram.pdf), where the bins the velocity (rounded) and the bin values are the percentage of time spent at a certain velocity (bin 10 is 10km/h). Then we create a [cumulative histogram](../master/docs/cum_histograms.pdf), and extract the velocities where the cumulative value surpasses 10, 20 to 90% of the time.

For instance, for a sub-division marked as *walk*, we get the features:

```
[0, 0, 1, 1, 2, 2, 2, 3, 3]
```

This means that 90% (index 8)  of the velocity is 3km/h, and 50% (index 4) of the sub-division was spent below 2km/h.

To train the default classifier we used the [GeoLife GPS Trajectories](https://www.microsoft.com/en-us/download/details.aspx?id=52367) dataset. We provide command line scripts to download the dataset and transform it to GPX.

We used the labels: *foot*, *airplane*, *train* and (motor) *vehicle*. The foot label includes data marked as *run* and *walk*. The train label is composed of data marked as *train* and *subway*. And the *vehicle* label is the combination of *taxi*, *bus*, *motorcycle* and *car* samples. We compressed the possible labels because of two factors:
  + Lack of relevant data. Only 4 samples were marked as *run*;
  + Transportation modes that belong to the same category. *Taxi*, *car* and *bus* are similar transportation modes, with a similar feature set.
We also don't use tracks marked as *boat* and *bike*. Because there's only seven *boat* samples, and because *bike* features are reduce the quality of classification and is rarely used by us.

To evaluate the classifiers we perform [two-fold validation](../master/scripts/two_fold_validation.py) with a 50% split of the data.

Using a SGD Classifier obtain a score between 84% and 86% (we use random permutation during training). Using a decision tree we obtain a score of 83%. These values drop to around 70% using the *bike* labels.

[The ` classification_validation.txt ` file offers more details](../master/docs/classifier_validation.txt).

## Command line tools

In addition to the library, *TrackToTrip* offers three command line tools outside of the library to manipulate GPS tracks and to generate classifier.

### tracktotrip_utils

```
usage: tracktotrip_utils.py [-h] [-a] [-s] [-o] [--eps EPS]
                            [--mintime MINTIME] [--seed SEED]
                            track [track ...] output_folder

Manipulate tracks

positional arguments:
  track              track to process, must be a gpx file
  output_folder

optional arguments:
  -h, --help         show this help message and exit
  -a, --anonymize    anonymizes tracks, by doing random rotations and
                     translations
  -s, --split        splits tracks so that each file contains a segment
  -o, --organize     takes all tracks and split them, naming them according
                     with their start date
  --eps EPS          max distance to other points. Used when spliting.
                     Defaults to 1.0
  --mintime MINTIME  minimum time required to split, in seconds. Defaults to
                     120
  --seed SEED        random number generator seed. Used when anonymizing
```

### tracktotrip_geolife_dataset

```
usage: tracktotrip_geolife_dataset.py [-h] [-o outputFolder] [-d]
                                      datasetFolder

GeoLife Trajectory dataset transportation mode extractor. Extracts
transportation mode from the dataset, into individual files, annotated with
the following format: [transporation mode].[control].[nPoints].[original file
name].gpx

positional arguments:
  datasetFolder         Path to the GeoLife dataset folder

optional arguments:
  -h, --help            show this help message and exit
  -o outputFolder, --output outputFolder
                        Path to processed dataset
  -d, --download        Pass this flag to download the GeoLife dataset to the
                        specified folder and to process it

```
### tracktotrip_build_classifier

```
usage: tracktotrip_build_classifier.py [-h] [-o outputFolder] [-f features]
                                       [-l labels]
                                       datasetFolder

positional arguments:
  datasetFolder         Path to the dataset, such as the GeoLife dataset

optional arguments:
  -h, --help            show this help message and exit
  -o outputFolder, --output outputFolder
                        Folder to store the classifier
  -f features, --features features
                        Path to features file to use
  -l labels, --labels labels
                        Path to features file to use

```

## Parallel projects

[*GatherMySteps*](https://github.com/ruipgil/GatherMySteps) is a webapp, that doubles as a track editor and semantic annotator. It is supported by [*ProcessMySteps*](https://github.com/ruipgil/ProcessMySteps), a python backend application that uses *TrackToTrip*.

[*GPXplorer*](http://ruipgil.com/GatherMySteps) is the track editor-only fork of [*GatherMySteps*](https://github.com/ruipgil/GatherMySteps)

These three projects are part of my master thesis.

## Contributing

1. Fork
2. Make changes
3. Create test cases
4. Lint with *pylint*
5. Send PR

This project also follows the [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html).

## License

[MIT license](../master/LICENSE)
