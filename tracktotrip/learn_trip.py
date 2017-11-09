"""
Learns trips
"""
import numpy as np
from .similarity import segment_similarity

def complete_trip(canonical_trips, from_point, to_point, distance_thr):
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
        current_result = []
        from_index, from_closest = trip.closest_point_to(from_point, thr=distance_thr)
        to_index, to_closest = trip.closest_point_to(to_point, thr=distance_thr)

        if from_index != -1 and to_index != -1:
            trip_slice = trip.slice(from_index, to_index+1)
            if trip.points[from_index] != from_closest and from_point.distance(from_closest) < from_point.distance(trip_slice.points[0]):
                trip_slice.points[0] = from_closest
            if trip.points[to_index] != to_closest and to_point.distance(to_closest) < to_point.distance(trip_slice.points[-1]):
                trip_slice.points[-1] = to_closest

            result.append([[p.lat, p.lon] for p in trip_slice.points])
            weights.append(count)
            total_weights = total_weights + count


    aa = {
        'possibilities': result,
        'weights': list(np.array(weights) / total_weights)
    }
    print([len(r) for r in result])
    print(weights)
    return aa


def learn_trip(current, current_id, canonical_trips, insert_canonical, update_canonical, eps, distance_thr):
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
        print("inserting trip %d" % len(current.points))
        insert_canonical(current, current_id)
    else:
        canonical_trips_a = [
            (trip_id, trip, segment_similarity(trip, current,  T=distance_thr))
            for trip_id, trip in canonical_trips
            ]
        canonical_trips_b = [
            (trip_id, trip, segment_similarity(current, trip, T=distance_thr))
            for trip_id, trip in canonical_trips
            ]

        canonical_trips = []
        for i in range(len(canonical_trips_a)):
            ct_a = canonical_trips_a[i]
            ct_b = canonical_trips_b[i]
            canonical_trips.append(ct_a if ct_a[2][0] > ct_b[2][0] else ct_b)

        canonical_trips = list(reversed(sorted(canonical_trips, key=lambda t: t[2][0])))

        trip_id, trip, (similarity, _) = canonical_trips[0]

        print("similarity = %f" % similarity)

        if similarity >= 0.7:
            # Same trip, fit all segments
            trip.merge_and_fit(current)#, diffs)
            trip.simplify(eps, 0, 0, topology_only=True)
            update_canonical(trip_id, trip, current_id)
            print("updating trip %d" % len(current.points))

        # elif similarity >= 0.3:
        #     # Fit similar segments
        #     orig = trip.copy()
        #     trip.merge_and_fit(current)#, diffs, threshold=0.2)
        #     trip.simplify(eps, 0, 0, topology_only=True)
        #
        #     current.merge_and_fit(orig)#, diffs, threshold=0.8)
        #     current.simplify(eps, 0, 0, topology_only=True)
        #
        #     # updateCanonicalTrip(tripId, trip, currentTripId)
        #     # updateCanonicalTrip(tripId, trip, currentTripId)

        else:
            # Insert new canonical representation
            current.simplify(eps, 0, 0, topology_only=True)
            print("inserting trip %d" % len(current.points))
            insert_canonical(current, current_id)
