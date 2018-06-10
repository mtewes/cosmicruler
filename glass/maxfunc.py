import astropy.units as u
from astropy.cosmology import Planck15 as cosmo
from astropy.cosmology import z_at_value

import matplotlib.pyplot as plt
import numpy as np


import scipy.optimize


z = np.linspace(1, 2, 1000)
d = cosmo.angular_diameter_distance(z)




plt.plot(z, d)
plt.show()