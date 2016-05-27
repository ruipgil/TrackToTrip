from pykalman import KalmanFilter

def kalman_filter(measurements, dt, n_iter=2):
    transition = [
            [1, dt, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, dt],
            [0, 0, 0, 1]]
    observation = [
            [1, 0, 0, 0],
            [0, 0, 1, 0]]
    initial = [measurements[0][0], measurements[0][1], 0, 0]
    kf = KalmanFilter(transition_matrices = transition, observation_matrices = observation, initial_state_mean=initial)
    kf = kf.em(measurements, n_iter=n_iter)
    (smoothed_state_means, smoothed_state_covariances) = kf.smooth(measurements)

    return map(lambda s: [s[0], s[2]], smoothed_state_means)
