# from .smooth import smoothSegments
# from .noiseDetection import noiseDetection
# from .segment import segment
# from .simplify import simplify

# def tracktotrip(track):
    # noise = noiseDetection(track, var=2)

    # finalSet = set(range(len(track))).difference(set(noise))
    # noiselessTrack = []
    # for i in finalSet:
        # noiselessTrack.append(track[i])

    # track = smoothSegments([noiselessTrack])
    # segments = segment(track[0])
    # segments = map(lambda s: simplify(s, 0.01, 5), segments)

    # return segments
