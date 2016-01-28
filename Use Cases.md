# Use Cases

*TrackToTrip* considers a diverse set of use cases:
## Segmentation

+ Go from *A* to *B*: one trip from *A* to *B*
+ Go from *A* to *B*, stay in *B* less than 30 seconds, then go to *C*: one trip, *A* to *C*
+ Go from *A* to *B*, stay in *B* between 30 seconds and 1 minute, then go to *C*: two trips, *A* to *B* and *B* to *C*
+ Go from *A* to *B*, stay in *B* more than 1 minute, then go to *C*: two trips, *A* to *B* and *B* to *C*

## Simplification

+ Simplify track with constant velocity
+ Simplify track with variable velocity

## Track cleaning

+ Starting point is a noise point
+ Destiny point is a noise point
+ Track has 1 noise point in between origin and destiny
+ Track has 5 consecutive noise points in between origin and destiny
+ Track has 10 consecutive noise points in between origin and destiny
+ Track has a noise spikes 10 around one place and in between origin and destiny

## Track completion

+ Correct origin of a trip
+ Correct destination of a trip
+ Interpolate missing data

## Trip representation

+ Two identical trips should have the same representation

## Transportation mode inferring

+ Go from *A* to *B* and don't change transportation mode
  Label the segment *A* to *B* with *walk*, *bike*, *run*, *in-vehicle*
+ Go from *A* to *B* and change transportation mode once
  Label segments *A* to *A'* and *A'* to *B* with *stationary*, *walk*, *bike*, *run*, *in-vehicle*, there cannot be two segments with the same transportation mode
+ Go from *A* to *B* and change transportation mode twice
  Label segments *A* to *A'*, *A'* to *A''* and *A''* to *B* with *stationary*, *walk*, *bike*, *run*, *in-vehicle*, there cannot be two consecutive segments with the same transportation mode
+ Go from *A* to *B* and change transportation mode three times
  Label segments *A* to *A'*, *A'* to *A''*, *A''* to *A'''* and *A'''* to *B* with *stationary*, *walk*, *bike*, *run*, *in-vehicle*, there cannot be two consecutive segments with the same transportation mode

## Personal location identification

+ In a trip, from *A* to *B*, *A* and *B* are identified as personally relevant locations, if already visited
+ In a trip, from *A* to *B*, *A* and *B* are identified as personally relevant locations if either one is within 10 meters of an already visited place

