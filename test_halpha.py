import cosmicruler
import astropy.table

import matplotlib.pyplot as plt
import numpy as np


catpath = "2580.fits"
cat = astropy.table.Table.read(catpath)


print cat.colnames

"""
"logf_halpha_model1"
"logf_halpha_model1_ext"
"logf_halpha_model3_ext"
"logf_halpha_model3"

"euclid_vis", "random_index", "true_redshift_gal"
"""

cat["avg_halpha_ext"] = 0.5 * ( 10.0**(cat["logf_halpha_model1_ext"]) +  10.0**(cat["logf_halpha_model3_ext"]))

cat = cat[cat["avg_halpha_ext"] > 2.e-16]

plt.scatter(cat["avg_halpha_ext"], cat["true_redshift_gal"], marker=".")

#plt.hist(cat["avg_halpha_ext"], bins=100)
plt.show()

