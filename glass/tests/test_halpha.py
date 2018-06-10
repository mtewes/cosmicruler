import cosmicruler
import astropy.table

import matplotlib.pyplot as plt
import numpy as np



cat = astropy.table.Table.read("2614.fits")
subsamplefactor = (1./256.) # For 2614
overal_square_degrees = 5000.0
catfactor = (overal_square_degrees) * subsamplefactor

print cat.colnames

"""
"logf_halpha_model1"
"logf_halpha_model1_ext"
"logf_halpha_model3_ext"
"logf_halpha_model3"

"euclid_vis", "random_index", "true_redshift_gal"
"""

cat["f_halpha_model1_ext"] = 10.0**(cat["logf_halpha_model1_ext"])
cat["f_halpha_model3_ext"] = 10.0**(cat["logf_halpha_model3_ext"])


cat["f_halpha_avg_ext"] = 0.5 * (cat["f_halpha_model1_ext"] + cat["f_halpha_model3_ext"])
cat["logf_halpha_avg_ext"] = np.log10(cat["f_halpha_avg_ext"])


#cat = cat[cat["true_redshift_gal"] < 2.3]
cat = cat[np.logical_and(cat["true_redshift_gal"] > 0.9, cat["true_redshift_gal"] < 1.82)]

print "VIS < 24.5, per arcmin2 : ", np.sum(cat["euclid_vis"] < 24.5)/(catfactor*3600)
print "NISP H < 24.0, per arcmin2 : ", np.sum(cat["euclid_nisp_h"] < 24.5)/(catfactor*3600)


print "Ha (model1) > 2.e-16, per deg2 : ", np.sum(cat["f_halpha_model1_ext"] > 2.e-16)/(catfactor)
print "Ha (model3) > 2.e-16, per deg2 : ", np.sum(cat["f_halpha_model3_ext"] > 2.e-16)/(catfactor)
print "Ha (avg_model) > 2.e-16, per deg2 : ", np.sum(cat["f_halpha_avg_ext"] > 2.e-16)/(catfactor)

print "NISP H < 24.0 and Ha (model1) > 2.e-16, per deg2 : ", np.sum(np.logical_and(cat["euclid_nisp_h"] < 24.0, cat["f_halpha_model1_ext"] > 2.e-16))/(catfactor)
print "NISP H < 24.0 and Ha (model3) > 2.e-16, per deg2 : ", np.sum(np.logical_and(cat["euclid_nisp_h"] < 24.0, cat["f_halpha_model3_ext"] > 2.e-16))/(catfactor)
print "NISP H < 24.0 and Ha (avg_model) > 2.e-16, per deg2 : ", np.sum(np.logical_and(cat["euclid_nisp_h"] < 24.0, cat["f_halpha_avg_ext"] > 2.e-16))/(catfactor)


"http://euclid2017.london/slides/Wednesday/Session1/NISPStatus-Ealet.pdf"


"""
plt.scatter(cat["logf_halpha_ext"], cat["euclid_nisp_h"], marker=".")
plt.xlabel("logf_halpha_ext (computed from average flux of model 1 and 3)")
plt.ylabel("euclid_nisp_h")

#plt.hist(cat["avg_halpha_ext"], bins=100)
plt.show()
"""

"""
plt.scatter(cat["logf_halpha_model1_ext"], cat["logf_halpha_model3_ext"], marker=".")
plt.xlabel("logf_halpha_model3_ext")
plt.ylabel("logf_halpha_model3_ext")

#plt.hist(cat["avg_halpha_ext"], bins=100)
plt.show()
"""



