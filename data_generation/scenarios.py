"""
This file holds all the manually crafted scenarios, which for the time being
is one where all targets intersect at a given point, and the other being CV
objects being birthed and killed stochastically, the former with a possion-
gaussian birth model, and the other a bernoulli.

To make a scenario follow the basic single-target assumptions, set the probability
of survival to 1 and the birth intensity to 0

TODO: YAML configuration for scenario
TODO: Own class for plotting
TODO: Animate plots
TODO: Step forward backward with buttons
"""

import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass


from constant_velocity_object import CVObject, Measurement

from utility import step_from_time, time_from_step




@dataclass
class ScenarioConfig:
    dt: float

    n_starting_targets: int
    birth_intensity: int
    mean_birth_pos: np.ndarray
    var_birth_pos: np.ndarray
    mean_birth_vel: np.ndarray
    var_birth_vel: np.ndarray

    probability_survival: float
    probability_detection: float

    process_noise: float # For the CV model
    measurement_noise: float # variance for position

    clutter_intensity: float

    sensor_range_max: float # Square with sidelength 2*sensor_range_max
    sensor_range_min: float
    sensor_position: np.ndarray = np.array((0, 0))




class BaseScenario:
    """
    A scenario takes some config for its input, and returns a set of measurements
    for the current timestep, or of multiple timesteps. 


    """

    def __init__(self, config: ScenarioConfig) -> None:
        self.config = config
        self.alive_targets = []
        self.k = 0 # current timestep. Maintain inside base?
        self.id = 0 # maintain an ID counter that is increased for every new target

        for _ in range(config.n_starting_targets):
            self.alive_targets.append(self._new_cv_object())


    def _new_cv_object(self):
        object = CVObject(
            np.random.multivariate_normal(self.config.mean_birth_pos, self.config.var_birth_pos),
            np.random.multivariate_normal(self.config.mean_birth_vel, self.config.var_birth_vel),
            self.id,
            self.config.process_noise,
            self.config.dt,
            time_from_step(self.k, self.config.dt)
        )
        self.id += 1

        return object

    def _is_target_in_range(self, target):
        target_in_sensor_range = True

        lmax = self.config.sensor_range_max
        lmin = self.config.sensor_range_min

        if not lmax > np.abs(target.track[-1, 1]) > lmin:
            target_in_sensor_range = False
        if not lmax > np.abs(target.track[-1, 2]) > lmin:
            target_in_sensor_range = False

        return target_in_sensor_range
        

    def generate_clutter(self):
        n_clutter = np.random.poisson(self.config.clutter_intensity)

        clutter = []
        for n in range(n_clutter):
            # TODO: Account for sensor position
            pos = np.random.uniform(-self.config.sensor_range_max, self.config.sensor_range_max, (2,))
            measurement = Measurement(pos, time_from_step(self.k, self.config.dt), is_clutter=True)
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
            if p_drop > self.config.probability_detection:
                continue
            
            if not self._is_target_in_range(target):
                continue

            position = np.array(target.track[-1, 1:3]) + np.random.normal((0, 0), self.config.measurement_noise*np.ones(2))

            measurement = Measurement(position, time_from_step(self.k, self.config.dt), is_clutter=False)
            measurements.append(measurement)

        return measurements



    def step(self):
    
        # Kill existing targets
        n_alive_targets = len(self.alive_targets)
        for i in range(n_alive_targets):
            p_kill = np.random.uniform()
            if p_kill > self.config.probability_survival:
                self.alive_targets.pop(i)

        for target in self.alive_targets:
            target.step()

        # Spawn new targets according to a PPP birth model
        n_new_targets = np.random.poisson(self.config.birth_intensity)
        for _ in range(n_new_targets):
            self.alive_targets.append(self._new_cv_object())
            

    def run(self, n_timesteps):

        hist_measurements = []

        for _ in range(n_timesteps):
            self.step() # Step ground truth targets
            

            # Generate true and false measurements and append to final list
            true_measurements = self.measurement_from_tracks()
            false_measurements = self.generate_clutter()

            measurements = true_measurements + false_measurements
            hist_measurements.append(measurements)

            self.k += 1


        return hist_measurements
    
    def ground_truths(self):
        raise NotImplementedError


    def plot(self, measurements):
        """
        TODO: Move to own class
        """

        # Ground truths
        for target in self.alive_targets:
            track = target.track
            x = track[:, 1]
            y = track[:, 2]
            plt.scatter(x, y)

        # Measurements
        for measurement in measurements:
            # measurements at time t
            for point in measurement:
                color = "r" if point.is_clutter else "k"                
                plt.scatter(point.pos[0], point.pos[1], marker="x", color=color)


        plt.show()


class ScenarioPlotter:

    def __init__(self):
        pass

    def plot(self):
        pass

if __name__ == "__main__":
    # Plot a single scenario

    config = ScenarioConfig(
        n_starting_targets=1,
        birth_intensity=0,
        mean_birth_pos=np.array((0, 0)),
        var_birth_pos=np.eye(2),
        mean_birth_vel=np.array((1, 1)),
        var_birth_vel=np.eye(2),
        probability_survival=1,
        probability_detection=0.9,
        process_noise=1,
        measurement_noise=0.1,
        clutter_intensity=1,
        sensor_range_max=10,
        sensor_range_min=0.1,
        dt = 0.1,
    )


    scenario = BaseScenario(config)

    measurements = scenario.run(100)
    scenario.plot(measurements)