"""
This file holds all the manually crafted scenarios, which for the time being
is one where all targets intersect at a given point, and the other being CV
objects being birthed and killed stochastically, the former with a possion-
gaussian birth model, and the other a bernoulli
"""

import numpy as np

from constant_velocity_object import CVObject

from dataclasses import dataclass

@dataclass
class ScenarioConfig:
    initial_birth: int
    birth_intensity: int
    mean_birth_pos: float
    var_birth_pos: float
    mean_birth_vel: float
    var_birth_vel: float

    probability_survival: float
    probability_detection: float

    process_noise: float # For the CV model
    measurement_noise: float

    clutter_intensity: float

    sensor_range_max: float
    sensor_range_min: float





class BaseScenario:
    """
    A scenario takes some config for its input, and returns a set of measurements
    for the current timestep, or of multiple timesteps. 

    The measurement model assumed here is range bearing!
    """

    def __init__(self, config: ScenarioConfig) -> None:
        self.config = config
        self.alive_targets: CVObject = []
        self.k: int = 0 # current timestep. Maintain inside base?
        self.id: int = 0 # maintain an ID counter that is increased for every new target

        # Initialize with Pois() number of targets

        n_starting_targets = np.random.poisson(config.initial_birth)

        for n in range(n_starting_targets):
            # sample position and velocity
            pos = np.random.normal(config.mean_birth_pos, config.var_birth_pos)
            vel = np.random.normal(config.mean_birth_vel, config.var_birth_vel)
            self.alive_targets.append(CVObject(pos, vel, self.id,
                config.process_noise, config.dt, np.round(self.k * config.dt, 3)
                )
            ) 
            self.id += 1

    def generate_clutter(self):
        n_clutter = np.random.poisson(self.config.clutter_intensity)

        clutter = []
        for n in range(n_clutter):
            pos = np.random.uniform()
            vel = np.random.normal(self.config.mean_birth_vel, self.config.var_birth_vel)
            clutter.append()
        return clutter

    def measurement_from_track(self):
        """
        Drop measurements with probability 1 - p_d
        Add noise
        """
        pass

    def step(self):

        # Kill existing targets

        for target in self.alive_targets:
            target.step()

        # Spawn new targets


class RandomScenario(BaseScenario):

    def __init__(self) -> None:
        super().__init__()




if __name__ == "__main__":
    # Plot a single scenario
