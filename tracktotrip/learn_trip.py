"""
Learns trips
"""
from .similarity import segment_similarity

def learn_trip(current, current_id, canonical_trips, insert_canonical, update_canonical):
    """Learns a trip against of other canonical trips

    Args:
        current (:obj:`Track`): current trip
        current_id (int): current trip (db) id
        canonical_trips (:obj:`list` of :obj:`Track`): list of canonical trips
        insert_canonical: Function to insert a new canonical trip, with the
            signature: (:obj:`Track`, int) -> void
        update_canonical: Function to update an existing canonical trip, with
            the signature: (int, :obj:`Track`, int) -> void
    """

    if len(canonical_trips) == 0:
        # print("Insert new canonical trip, unmatched bounding box")

        # TODO simplify
        # currentTrip.simplify(topology_only=True)
        # print(currentTrip, currentTripId)
        insert_canonical(current, current_id)
    else:
        # print(canonicalTrips)
        canonical_trips = [
            (trip_id, trip, segment_similarity(trip, current))
            for trip_id, trip in canonical_trips
            ]
        canonical_trips = sorted(canonical_trips, key=lambda t: t[2][0])

        trip_id, trip, (similarity, _) = canonical_trips[0]
        # print(similarity, diffs)

        if similarity >= 0.8:
            # print("Same as canonical trip, fitting trip")
            # Same trip, fit all segments
            trip.merge_and_fit(current)#, diffs)
            trip.simplify(topology_only=True)
            update_canonical(trip_id, trip, current_id)

        elif similarity >= 0.3:
            # print("Similar as canonical trip, fitting similar segments. Adding new trip")
            # Fit similar segments
            orig = trip.copy()
            trip.merge_and_fit(current)#, diffs, threshold=0.2)
            trip.simplify(topology_only=True)

            current.merge_and_fit(orig)#, diffs, threshold=0.8)
            current.simplify(topology_only=True)

            # updateCanonicalTrip(tripId, trip, currentTripId)
            # updateCanonicalTrip(tripId, trip, currentTripId)

        else:
            # print("New canonical trip, with similar boundingbox to others")
            # Insert new canonical representation
            current.simplify(topology_only=True)
            insert_canonical(current, current_id)
