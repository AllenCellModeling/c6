# c6 (Circular Center-based Cell Colony Creation and Clustering) <img src="docs/imgs/logo.png" width="250" title="c6" alt="c6" align="right" vspace = "50">

[![Build Status](https://github.com/AllenCellModeling/c6/workflows/Build%20Master/badge.svg)](https://github.com/AllenCellModeling/c6/actions)
[![Documentation](https://github.com/AllenCellModeling/c6/workflows/Documentation/badge.svg)](https://AllenCellModeling.github.io/c6)
[![Code Coverage](https://codecov.io/gh/AllenCellModeling/c6/branch/master/graph/badge.svg)](https://codecov.io/gh/AllenCellModeling/c6)

C6 is a toy center-based model of the initial clustering that occurs as a cells aggregate after replating. 


---

## Features
- [x] Represents cells as non-overlapping circles
- [x] Cells exclude each other
- [x] Cells sense each other with tunable strength and distances
- [x] Cells grow at tunable rates
- [x] Cells divide at tunable sizes
- [x] Cells' growth is contact inhibited
- [x] Runs are launched from stored initial conditions
- [x] Runs are selectable as deterministic or stochastic 
- [x] Runs are logged to tidy data file
- [x] Run state is visualized
- [x] You can save run states out to pretty MP4s
- [ ] Summary statistics are available for probing run logs
- [ ] Easy run profiling

## Quick Start
```python
import c6
import numpy as np
import matplotlib.pyplot as plt


space = c6.Space()
cell_locs = 20*np.random.random((10,2))
cells = [c6.Cell(space, loc) for loc in cell_locs]

fig, ax = plt.subplots(1,1, figsize=(10,10))
ax.set(xlim=(-10, 20), ylim=(-10, 20))
animation = c6.plot.animate(fig, ax, space, 500)
animation.save('example.mp4', fps=20)
```

## Installation

Clone and install or `pip install git+https://github.com/AllenCellModeling/c6.git`

## Creating initial conditions and logging runs

Both initial conditions and run logs are stored as JSON in this form:

```json
{
    "seed": 123,
    "universal": {"sensing": 12.3,
                  "influence_max": 12,
                  "influence_decay": 0.3,
                  "adhesion": 0.5
                 },
    "cells": [{"time": 0,
               "id": [0, 1, ..., 100],
               "loc": [[1, 2], [3, 4], ..., [0.5, 2]],
               "radius": [0.3, 0.5, ..., 2.0]
             }]
}
```

Any property that can be passed to `c6.Cell` as a parameter can be serialized either as a key/value pair in `'universal'`, in which case it applies to all cells at all time points, or to `"cells"`, in which case it is parsed on a per cell per time point basis. Starting conditions are this file, but with only the first entry in `"cells"` specified. The first entry in `"cells"` is always applied before later entries and so per-cell values that do not change (e.g. ids) can be set there. 


## Documentation
For full package documentation please visit [AllenCellModeling.github.io/c6](https://AllenCellModeling.github.io/c6).

Available under the Allen Institute Software License
