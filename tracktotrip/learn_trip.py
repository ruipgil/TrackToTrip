from similarity import segment_similarity

def learn_trip(currentTrip, currentTripId, canonicalTrips, insertCanonicalTrip, updateCanonicalTrip):
    """Learns a trip against of other canonical trips

    Args:
        currentTrip: tracktotrip.Segment that is the current trip
            to learn
        canonicalTrips: Array of tracktotrip.Segment, to whom the
            trip will be compared
        insertCanonicalTrip: Function that receives a tracktotrip.Track
            as argument. It is called when the trip is a new one.
        updateCanonicalTrip: Function that receives a tracktotrip.Track
            as argument. It is called when the trip to be learned exists
            or needs to be updated.
    """

    if len(canonicalTrips) == 0:
        print("Insert new canonical trip, unmatched bounding box")

        # TODO simplify
        # currentTrip.simplify(topology_only=True)
        print(currentTrip, currentTripId)
        insertCanonicalTrip(currentTrip, currentTripId)
    else:
        print(canonicalTrips)
        canonicalTrips = map(lambda (tripId, trip): (tripId, trip, segment_similarity
            (trip, currentTrip)), canonicalTrips)
        canonicalTrips = sorted(canonicalTrips, key=lambda t: t[2][0])

        tripId, trip, (similarity, diffs) = canonicalTrips[0]
        # print(similarity, diffs)

        if similarity >= 0.8:
            print("Same as canonical trip, fitting trip")
            # Same trip, fit all segments
            trip.merge_and_fit(currentTrip)#, diffs)
            trip.simplify(topology_only=True)
            updateCanonicalTrip(tripId, trip, currentTripId)

        elif similarity >= 0.3:
            print("Similar as canonical trip, fitting similar segments. Adding new trip")
            # Fit similar segments
            orig = trip.copy()
            trip.merge_and_fit(currentTrip)#, diffs, threshold=0.2)
            trip.simplify(topology_only=True)

            currentTrip.merge_and_fit(orig)#, diffs, threshold=0.8)
            currentTrip.simplify(topology_only=True)

            # updateCanonicalTrip(tripId, trip, currentTripId)
            # updateCanonicalTrip(tripId, trip, currentTripId)

        else:
            print("New canonical trip, with similar boundingbox to others")
            # Insert new canonical representation
            currentTrip.simplify(topology_only=True)
            insertCanonicalTrip(currentTrip, currentTripId)

