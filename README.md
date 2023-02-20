# Target tracking playground

Currently contains unpublished tracking code for project/msc thesis work and a data generator to test point-object trackers

# How to run scenario generator
Modify the scenario.yaml to your liking :^)
```
python .\data_generation\scenarios.py -c .\config\scenario.yaml
```

# Using data_generation in other projects

To install the data generator using the setup.py file, follow these steps:

1. Clone this project.

2. Open a terminal window and navigate to the directory containing the setup.py file.

3. Run the following command to install the package:

    python -m pip install .

This will install all the components of this library. An example usage can be found below:


```python

import data_generation.scenarios as scene


scenario = scene.BaseScenario(config)

```

where you will need to specify your own config