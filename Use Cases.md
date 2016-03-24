# Test Cases

*TrackToTrip* considers a diverse set of use cases:
## A. Segmentation

1. Go from *A* to *B*: one trip from *A* to *B*
2. Go from *A* to *B*, stay in *B* less than 30 seconds, then go to *C*: one trip, *A* to *C*
3. Go from *A* to *B*, stay in *B* between 30 seconds and 1 minute, then go to *C*: two trips, *A* to *B* and *B* to *C*
4. Go from *A* to *B*, stay in *B* more than 1 minute, then go to *C*: two trips, *A* to *B* and *B* to *C*

### Why 30 seconds?
It is the time that we choose suitable to distinguish between a stay in one place.
This defined threshold allows us to test our system.

## B. Simplification

1. Simplify track with constant velocity
2. Simplify track with variable velocity

## C. Track cleaning

1. Starting point is a noise point
2. Destiny point is a noise point
3. Resolve tangling of points around a place. Tangled points should be approximated to more representative set of points
4. Track has 1 spike points between origin and destiny
5. Track has 2 consecutive spike points between origin and destiny
6. Track has 4 consecutive spike points between origin and destiny
7. Track has 8 consecutive spike points between origin and destiny
8. Track has more than 8 consecutive spike points between origin and destiny

## D. Track completion

1. Correct origin of a trip
2. Correct destination of a trip
3. Interpolate missing data

## E. Trip representation

1. Two identical trips should have the same representation

## F. Transportation mode inferring

1. Go from *A* to *B* and don't change transportation mode
  Label the segment *A* to *B* with *walk*, *bike*, *run*, *in-vehicle*
2. Go from *A* to *B* and change transportation mode once
  Label segments *A* to *A'* and *A'* to *B* with *stationary*, *walk*, *bike*, *run*, *in-vehicle*, there cannot be two segments with the same transportation mode
3. Go from *A* to *B* and change transportation mode twice
  Label segments *A* to *A'*, *A'* to *A''* and *A''* to *B* with *stationary*, *walk*, *bike*, *run*, *in-vehicle*, there cannot be two consecutive segments with the same transportation mode
4. Go from *A* to *B* and change transportation mode three times
  Label segments *A* to *A'*, *A'* to *A''*, *A''* to *A'''* and *A'''* to *B* with *stationary*, *walk*, *bike*, *run*, *in-vehicle*, there cannot be two consecutive segments with the same transportation mode

## G. Personal location identification

1. In a trip, from *A* to *B*, *A* and *B* are identified as personally relevant locations, if already visited
2. In a trip, from *A* to *B*, *A* and *B* are identified as personally relevant locations if either one is within 10 meters of an already visited place

# File format

Files representative of test cases are saved to the folder ``` TestFiles ```.

They must follow the naming formart:

``` [Test type].[Test case].[ISO time of the first point].gpx ```

Where,
+ ``` Test type ``` is the letter that identifies the test type (A to G)
+ ``` Test case ``` is the number that identifies the test case of the test type
+ ``` ISO time of the first point ``` is the time of the first point in the track

# Additional information

In some test cases, such as A and C, more details may be relevant. When additional information is required, a file with the same name, and ``` .info ``` extension, must be created. It should be a plain text file.

## Examples

+ ``` A.2.2016-02-15T14:21:35.408Z.gpx ```
  - ``` A.2.2016-02-15T14:21:35.408Z.info ``` which contains the approximated start and end time of each segment

+ ``` B.1.2016-01-11T14:08:46.108Z.gpx ```

+ ``` C.6.2016-02-21T18:43:12.408Z.gpx ```
  - ``` C.6.2016-02-21T18:43:12.408Z.info ```, optional, which contains the approximated start and end time of the region with spike points
