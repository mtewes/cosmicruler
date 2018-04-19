import cosmicruler
import galcounts
import svgwrite

import astropy.units as u
from astropy.cosmology import Planck15 as cosmo
from astropy.cosmology import z_at_value

import astropy.table

import numpy as np
import scipy.optimize


"""
A script for the glass
"""



zptrans = cosmicruler.ZPTrans(0.0, 2.0, "sqrt")


scales = []


name = "redshift"
title = "Redshift"
labels = [(value, "{}".format(value)) for value in [0.0, 0.01, 0.02, 0.04, 0.06, 0.08, 0.1, 0.2, 0.4, 0.6, 0.8, 1.0, 2.0]]
majticks = [value for (value, text) in labels]
medticks = cosmicruler.subticks(majticks, 2)
minticks = cosmicruler.subticks(majticks, 10)
scales.append(cosmicruler.Scale.fromz(zptrans, name, majticks, medticks, minticks, labels, title))


name = "lbt"
title = "Time to launch [Gyr]"

sourceticks = np.arange(1, 10.1, 1)
labels = [(z_at_value(cosmo.lookback_time, value * u.Gyr), "{:.0f}".format(value)) for value in sourceticks]
majticks = [value for (value, text) in labels]
majticks.append(0.0)
labels.append((0.0, "0"))
medticks = [z_at_value(cosmo.lookback_time, value * u.Gyr) for value in cosmicruler.subticks(sourceticks, 2)]
minticks = [z_at_value(cosmo.lookback_time, value * u.Gyr) for value in cosmicruler.subticks(sourceticks, 10)]

presourceticks = [0.01, 0.1]
prelabels = [(z_at_value(cosmo.lookback_time, value * u.Gyr), "{}".format(value)) for value in presourceticks]
premajticks = [value for (value, text) in prelabels]
premedticks = []
preminticks = [z_at_value(cosmo.lookback_time, value * u.Gyr) for value in cosmicruler.subticks(presourceticks, 9)] + \
	[z_at_value(cosmo.lookback_time, value * u.Gyr) for value in [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]]
labels = prelabels + labels
majticks = premajticks + majticks
medticks = premedticks + medticks
minticks = preminticks + minticks
scales.append(cosmicruler.Scale.fromz(zptrans, name, majticks, medticks, minticks, labels, title))


name = "distmod"
title = "Distance modulus"
labels = [(z_at_value(cosmo.distmod, value * u.mag), "{:.0f}".format(value)) for value in np.arange(37.0, 46.1, 1)]
majticks = [value for (value, text) in labels]
medticks = [z_at_value(cosmo.distmod, value * u.mag) for value in np.arange(37, 46, 0.5)]
minticks = [z_at_value(cosmo.distmod, value * u.mag) for value in np.arange(37, 46, 0.1)]

prelabels = [(z_at_value(cosmo.distmod, value * u.mag), "{:.0f}".format(value)) for value in [30, 32, 34, 36]]

premajticks = [value for (value, text) in prelabels]
premedticks = list(cosmicruler.subticks(premajticks, 2))
preminticks = []
labels = prelabels + labels
majticks = premajticks + majticks
medticks = premedticks + medticks
minticks = preminticks + minticks

scales.append(cosmicruler.Scale.fromz(zptrans, name, majticks, medticks, minticks, labels, title))



name = "angdiam"
title = "Angular diameter distance [Gpc]"
zpeak = scipy.optimize.fmin(lambda z: -cosmo.angular_diameter_distance(z).value, 1.5)[0]
valpeak = cosmo.angular_diameter_distance(zpeak)
labelpeak = ""

extras={"peak":(zpeak, labelpeak)}

sourceticks1 = [0.1, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6]
labelticks1 = sourceticks1 + [1.7, 1.75, 1.78, 1.79]
labels1 = [(z_at_value(cosmo.angular_diameter_distance, value * u.Gpc, zmax=zpeak), "{}".format(value)) for value in labelticks1]
majticks1 = [value for (value, text) in labels1]
majticks1.append(0.0)
labels1.append((0.0, "0"))
medticks1 = [z_at_value(cosmo.angular_diameter_distance, value * u.Gpc, zmax=zpeak) for value in cosmicruler.subticks(sourceticks1, 2)]
minticks1 = [z_at_value(cosmo.angular_diameter_distance, value * u.Gpc, zmax=zpeak) for value in cosmicruler.subticks(sourceticks1, 10)]

sourceticks2 = [1.79, 1.78]
labels2 = [(z_at_value(cosmo.angular_diameter_distance, value * u.Gpc, zmin=zpeak), "{}".format(value)) for value in sourceticks2]
majticks2 = [value for (value, text) in labels2]
medticks2 = []
minticks2 = []

labels = labels1 + labels2
majticks = majticks1 + majticks2
medticks = medticks1 + medticks2
minticks = minticks1 + minticks2

scales.append(cosmicruler.Scale.fromz(zptrans, name, majticks, medticks, minticks, labels, title, extras))








name = "size"
title = "VIS pixel scale [kpc] (transverse proper size subtending 0.1 arcsec)"
f = 600.0 * u.kpc / u.arcmin
zpeak = scipy.optimize.fmin(lambda z: -cosmo.kpc_proper_per_arcmin(z).value, 1.5)[0]
valpeak = cosmo.kpc_proper_per_arcmin(zpeak) / f
labelpeak = "{:.3f}".format(valpeak.value)

extras={"peak":(zpeak, labelpeak)}


sourceticks1 = list(np.arange(0.1, 0.85, 0.1))
labelticks1 = sourceticks1 + [0.85, 0.86]
labels1 = [(z_at_value(cosmo.kpc_proper_per_arcmin, value * f, zmax=zpeak), "{}".format(value)) for value in labelticks1]	
majticks1 = [value for (value, text) in labels1]
medticks1 = [z_at_value(cosmo.kpc_proper_per_arcmin, value * f, zmax=zpeak) for value in cosmicruler.subticks(sourceticks1, 2)]
minticks1 = [z_at_value(cosmo.kpc_proper_per_arcmin, value * f, zmax=zpeak) for value in cosmicruler.subticks(sourceticks1, 10)]


labelticks2 = [0.001, 0.01, 0.1]
labels2 = [(z_at_value(cosmo.kpc_proper_per_arcmin, value * f, zmax=zpeak), "{}".format(value)) for value in labelticks2]	
majticks2 = [value for (value, text) in labels2]
medticks2 = []
minticks2 = [z_at_value(cosmo.kpc_proper_per_arcmin, value * f, zmax=zpeak) for value in cosmicruler.subticks(labelticks2, 9)]
majticks2 = majticks2[:-1]
labels2 = labels2[:-1]


labels3 = [(z_at_value(cosmo.kpc_proper_per_arcmin, value * f, zmin=zpeak), "{}".format(value)) for value in [0.865, 0.86]]
majticks3 = [value for (value, text) in labels3]
medticks3 = []
minticks3 = []

labels = labels1 + labels2 + labels3
majticks = majticks1 + majticks2 + majticks3
medticks = medticks1 + medticks2 + medticks3
minticks = minticks1 + minticks2 + minticks3

scales.append(cosmicruler.Scale.fromz(zptrans, name, majticks, medticks, minticks, labels, title, extras))




name = "visgals"
title = "Cumulated number of galaxies per square arcmin with VIS < 24.5 (based on the Euclid Flagship mock galaxy catalogue)"
cat = astropy.table.Table.read("2562.fits")
cat = cat[cat["euclid_vis"] < 24.5]
subsamplefactor = (1./256.) * 0.1
overal_square_degrees = 5000.0
catfactor = (overal_square_degrees * 3600) * subsamplefactor
labels = [(value, "{}".format(value)) for value in [0.01, 0.1, 1.0, 10.0, 15.0, 20.0, 25.0, 30.0]]
majticks = [value for (value, text) in labels]
medticks = []
minticks = cosmicruler.subticks([0.01, 0.1, 1.0, 10.0], 9)
scale = galcounts.scale_counts_to_z(cat, catfactor, zptrans, name=name, majticks=majticks, medticks=medticks, minticks=minticks, labels=labels, title=title)
scales.append(scale)



name = "nispsgals"
title = "Cumulated number of galaxies per square arcmin with an H-alpha flux above NISP spectroscopic sensitivity (based on the Euclid Flagship mock galaxy catalogue)"
cat = astropy.table.Table.read("2580.fits")
cat["avg_halpha_ext"] = 0.5 * ( 10.0**(cat["logf_halpha_model1_ext"]) +  10.0**(cat["logf_halpha_model3_ext"]))
cat = cat[cat["avg_halpha_ext"] > 2.e-16]
subsamplefactor = (1./256.) * 0.1
overal_square_degrees = 5000.0
catfactor = (overal_square_degrees * 3600) * subsamplefactor
labels = [(value, "{}".format(value)) for value in [0.01, 0.1, 1.0, 2]]
majticks = [value for (value, text) in labels]
medticks = []
minticks = []#cosmicruler.subticks([0.01, 0.1, 1.0, 10.0], 9)
scale = galcounts.scale_counts_to_z(cat, catfactor, zptrans, name=name, majticks=majticks, medticks=medticks, minticks=minticks, labels=labels, title=title)
scales.append(scale)




"""
name = "w"
title = "Current best estimate of the dark energy equation of state parameter"
labels = [(value, "1.0") for value in np.linspace(0.0, 1.0, 10)]
majticks = [value for (value, text) in labels]
medticks = []
minticks = []
scales.append(cosmicruler.Scale(name, majticks, medticks, minticks, labels, title))
"""




filepath = "all.svg"

dwg = svgwrite.Drawing(filepath, profile='full', debug=True)
dwg.add(dwg.rect(insert=(0, 0), size=(1000, 1000), rx=5, ry=5, fill="none", stroke="black"))

for (i, scale) in enumerate(scales):
	scale.simpledraw(dwg, 20, 50 + i*50 , 960)
	
dwg.save(pretty=True)

