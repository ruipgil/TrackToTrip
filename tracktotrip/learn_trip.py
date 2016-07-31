"""
Learns trips
"""
import numpy as np
from .similarity import segment_similarity

def complete_trip(canonical_trips, from_point, to_point):
    """ Completes a trip based on set of canonical trips

    Args:
        canonical_trips (:obj:`list` of :obj:`Segment`)
        from_point (:obj:`Point`)
        to_point (:obj:`Point`)
    """
    result = []
    weights = []
    total_weights = 0.0
    # match points in lines
    for (_, trip, count) in canonical_trips:
        from_index = trip.closest_point_to(from_point)
        to_index = trip.closest_point_to(to_point)
        if from_index != to_index and from_index != -1 and to_index != -1:
            trip_slice = trip.slice(from_index, to_index)
            result.append([[p.lat, p.lon] for p in trip_slice.points])
            weights.append(count)
            total_weights = total_weights + count

    return {
        'possibilities': result,
        'weights': list(np.array(weights) / total_weights)
    }


def learn_trip(current, current_id, canonical_trips, insert_canonical, update_canonical, eps):
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
        current.simplify(eps, 0, 0, topology_only=True)
        insert_canonical(current, current_id)
    else:
        canonical_trips = [
            (trip_id, trip, segment_similarity(trip, current))
            for trip_id, trip in canonical_trips
            ]
        canonical_trips = sorted(canonical_trips, key=lambda t: t[2][0])

        trip_id, trip, (similarity, _) = canonical_trips[0]

        if similarity >= 0.8:
            # Same trip, fit all segments
            trip.merge_and_fit(current)#, diffs)
            trip.simplify(eps, 0, 0, topology_only=True)
            update_canonical(trip_id, trip, current_id)

        elif similarity >= 0.3:
            # Fit similar segments
            orig = trip.copy()
            trip.merge_and_fit(current)#, diffs, threshold=0.2)
            trip.simplify(eps, 0, 0, topology_only=True)

            current.merge_and_fit(orig)#, diffs, threshold=0.8)
            current.simplify(eps, 0, 0, topology_only=True)

            # updateCanonicalTrip(tripId, trip, currentTripId)
            # updateCanonicalTrip(tripId, trip, currentTripId)

        else:
            # Insert new canonical representation
            current.simplify(eps, 0, 0, topology_only=True)
            insert_canonical(current, current_id)
