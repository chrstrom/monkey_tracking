import argparse

import numpy as np
import matplotlib.pyplot as plt

from constant_velocity_object import CVObject, Measurement

from utility import time_from_step
from load_config import load_yaml_into_dotdict


class BaseScenario:
    """
    A scenario takes some config for its input, and returns a set of measurements
    for the current timestep, or of multiple timesteps.


    """

    def __init__(self, config) -> None:
        self.config = config
        self.alive_targets = []
        self.dead_targets = []
        self.k = 0  # current timestep. Maintain inside base?
        self.id = 0  # maintain an ID counter that is increased for every new target

        for _ in range(config.n_starting_targets):
            self.alive_targets.append(self._new_cv_object())

    def _new_cv_object(self):
        object = CVObject(
            np.random.multivariate_normal(
                self.config.birth.position.mean, self.config.birth.position.var
            ),
            np.random.multivariate_normal(
                self.config.birth.velocity.mean, self.config.birth.velocity.var
            ),
            self.id,
            self.config.noise.process,
            self.config.dt,
            time_from_step(self.k, self.config.dt),
        )
        self.id += 1

        return object

    def _is_target_in_range(self, target):
        target_in_sensor_range = True

        lmax = self.config.sensor.range.max
        lmin = self.config.sensor.range.min

        if not lmax > np.abs(target.track[-1, 1]) > lmin:
            target_in_sensor_range = False
        if not lmax > np.abs(target.track[-1, 2]) > lmin:
            target_in_sensor_range = False

        return target_in_sensor_range

    def generate_clutter(self):
        n_clutter = np.random.poisson(self.config.noise.clutter_intensity)

        clutter = []
        for n in range(n_clutter):
            # TODO: Account for sensor position
            pos = np.random.uniform(
                -self.config.sensor.range.max, self.config.sensor.range.max, (2,)
            )
            measurement = Measurement(
                pos, time_from_step(self.k, self.config.dt), is_clutter=True
            )
            clutter.append(measurement)
        return clutter

    def measurement_from_tracks(self):
        """
        Drop measurements with probability 1 - p_d or if target is out of sensor
        area.
        """
        measurements = []

        for target in self.alive_targets:
            p_drop = np.random.uniform()
            if p_drop > self.config.probability.detection:
                continue

            if not self._is_target_in_range(target):
                continue

            position = np.array(target.track[-1, 1:3]) + np.random.normal(
                (0, 0), self.config.noise.measurement * np.ones(2)
            )

            measurement = Measurement(
                position, time_from_step(self.k, self.config.dt), is_clutter=False
            )
            measurements.append(measurement)

        return measurements

    def step(self):

        # Kill existing targets
        n_alive_targets = len(self.alive_targets)
        for i in range(n_alive_targets):
            p_kill = np.random.uniform()
            if p_kill > self.config.probability.survival:
                dead_target = self.alive_targets.pop(
                    np.random.randint(len(self.alive_targets))
                )
                self.dead_targets.append(dead_target)

        for target in self.alive_targets:
            target.step()

        # Spawn new targets according to a PPP birth model
        n_new_targets = np.random.poisson(self.config.birth.intensity)
        for _ in range(n_new_targets):
            self.alive_targets.append(self._new_cv_object())

    def run(self, n_timesteps):

        hist_measurements = []

        for _ in range(n_timesteps):
            self.step()  # Step ground truth targets

            # Generate true and false measurements and append to final list
            true_measurements = self.measurement_from_tracks()
            false_measurements = self.generate_clutter()

            measurements = true_measurements + false_measurements
            hist_measurements.append(measurements)

            self.k += 1

        ground_truths = self.dead_targets + self.alive_targets

        return hist_measurements, ground_truths

    def ground_truths(self):
        raise NotImplementedError


def plot(scenario, measurements, ground_truths):

    end_time = time_from_step(scenario.k, scenario.config.dt)
    min_alpha = 0.5

    # Ground truths
    for target in ground_truths:
        track = target.track
        x = track[:, 1]
        y = track[:, 2]
        alpha = 1 - np.vectorize(max)(min_alpha, 1 - track[:, 5] / end_time)
        plt.scatter(x, y, alpha=alpha)

    # Measurements
    for measurements_at_t in measurements:

        # opacity based on time
        for measurement in measurements_at_t:
            alpha = 1 - max(min_alpha, 1 - measurement.t / end_time)
            color = "r" if measurement.is_clutter else "k"
            plt.scatter(
                measurement.pos[0],
                measurement.pos[1],
                marker="x",
                color=color,
                alpha=alpha,
            )

    plt.xlabel("x [m]")
    plt.ylabel("y [m]")

    plt.gca().set_aspect("equal")
    plt.grid()
    plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config")
    args = parser.parse_args()

    print(f"Using config from: {args.config}")
    config = load_yaml_into_dotdict(args.config)

    scenario = BaseScenario(config)

    measurements, ground_truths = scenario.run(50)

    for measurements_at_t in measurements:
        for measurement in measurements_at_t:
            print(measurement)
        print()

    plot(scenario, measurements, ground_truths)
