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


scale = cosmicruler.Scale(name="redshift", title="Redshift")
labelpos = [0.0, 0.01, 0.1, 0.2, 0.4, 0.6, 0.8, 1.0, 1.5, 2.0]
scale.labels.extend([(value, "{}".format(value)) for value in labelpos])
scale.addautosubticks([0.0, 0.01], "lin2")
scale.addautosubticks([0.01, 0.1], "log10")
scale.addautosubticks([0.1, 0.2, 0.4, 0.6, 0.8, 1.0], "lin2")
scale.addautosubticks([1.0, 1.5, 2.0], "lin5")
scales.append(scale)


scale = cosmicruler.Scale(name="lbt", title="Time to launch [Gyr]")
transf = lambda x: z_at_value(cosmo.lookback_time, x * u.Gyr)
sourceticks = [0.5, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
scale.labels.extend([(transf(value), "{}".format(value)) for value in sourceticks])
scale.labels.append((0.0, "0"))
scale.addautosubticks([0.0, 0.5], "lin5", transf)
scale.addautosubticks(sourceticks, "lin2", transf)
scale.majticks.append(0.0)
scales.append(scale)


scale = cosmicruler.Scale(name="distmod", title="Distance modulus")
transf = lambda x: z_at_value(cosmo.distmod, x * u.mag)
sourceticks = [40, 41, 42, 43, 44, 45, 46]
scale.labels.extend([(transf(value), "{}".format(value)) for value in sourceticks])
scale.addautosubticks(sourceticks, "lin2", transf)
sourceticks = [35, 37, 39]
scale.labels.extend([(transf(value), "{}".format(value)) for value in sourceticks])
scale.addautosubticks(sourceticks, "lin2", transf)
sourceticks = [30, 35]
scale.labels.extend([(transf(value), "{}".format(value)) for value in sourceticks])
scale.addautosubticks(sourceticks, "lin5", transf)
scales.append(scale)



scale = cosmicruler.Scale(name="angdiam", title="Angular diameter distance [Gpc]")
zpeak = scipy.optimize.fmin(lambda z: -cosmo.angular_diameter_distance(z).value, 1.5)[0]
valpeak = cosmo.angular_diameter_distance(zpeak)
labelpeak = "{:.3f}".format(valpeak.value/1000.0)
scale.extras = {"peak":(zpeak, labelpeak)}
scale.labels.append((0.0, "0.0"))
scale.majticks.append(0.0)
transf1 = lambda x: z_at_value(cosmo.angular_diameter_distance, x * u.Gpc, zmax=zpeak) # left of peak
transf2 = lambda x: z_at_value(cosmo.angular_diameter_distance, x * u.Gpc, zmin=zpeak) # right of peak
#sourceticks = [0.01, 0.1]
#scale.labels.extend([(transf1(value), "{}".format(value)) for value in sourceticks])
#scale.addautosubticks(sourceticks, None, transf1)
scale.addautosubticks([0.0, 0.1], "lin5", transf1)
scale.labels.extend([(transf1(value), "{}".format(value)) for value in [0.1]])
sourceticks = [0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6]
scale.labels.extend([(transf1(value), "{}".format(value)) for value in sourceticks])
scale.addautosubticks(sourceticks, "lin2", transf1)
sourceticks = [1.7, 1.75, 1.78]
scale.labels.extend([(transf1(value), "{}".format(value)) for value in sourceticks])
scale.addautosubticks(sourceticks, None, transf1)
sourceticks = [1.78]
scale.labels.extend([(transf2(value), "{}".format(value)) for value in sourceticks])
scale.addautosubticks(sourceticks, None, transf2)
scales.append(scale)





scale = cosmicruler.Scale(name="size", title="VIS pixel scale [kpc] (transverse proper size subtending 0.1 arcsec)")
f = 600.0 * u.kpc / u.arcmin
zpeak = scipy.optimize.fmin(lambda z: -cosmo.kpc_proper_per_arcmin(z).value, 1.5)[0]
valpeak = cosmo.kpc_proper_per_arcmin(zpeak) / f
labelpeak = "{:.2f}".format(valpeak.value)
scale.extras={"peak":(zpeak, labelpeak)}
transf1 = lambda x: z_at_value(cosmo.kpc_proper_per_arcmin, x * f, zmax=zpeak) # left of peak
transf2 = lambda x: z_at_value(cosmo.kpc_proper_per_arcmin, x * f, zmin=zpeak) # right of peak
sourceticks = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
scale.labels.extend([(transf1(value), "{}".format(value)) for value in sourceticks])
scale.addautosubticks(sourceticks, "lin2", transf1)
sourceticks = [0.01, 0.1]
scale.labels.extend([(transf1(value), "{}".format(value)) for value in sourceticks])
scale.addautosubticks(sourceticks, "log10", transf1)
sourceticks = [0.85, 0.86]
scale.labels.extend([(transf1(value), "{}".format(value)) for value in sourceticks])
scale.addautosubticks(sourceticks, None, transf1)
sourceticks = [0.86]
scale.labels.extend([(transf2(value), "{}".format(value)) for value in sourceticks])
scale.addautosubticks(sourceticks, None, transf2)
scales.append(scale)






filepath = "glass.svg"

dwg = svgwrite.Drawing(filepath, profile='full', debug=True)
dwg.add(dwg.rect(insert=(0, 0), size=(1100, 1570), rx=5, ry=5, fill="none", stroke="red")) # height is 110 mm, perimeter is 157

labelstyle = "font-size:24;font-family:Helvetica Neue"
titlestyle = "font-size:32;font-family:Helvetica Neue"

for (i, scale) in enumerate(scales[::-1]):
	#print scale
	
	
	scale.apply_zptrans(zptrans)
	
	scale.simpledraw(dwg, 10, 90 + i*160 , 1060,
		lw=2.0, tickl=25.0, titlespace=15.0, labelspace=10.0,
		labelstyle=labelstyle, titlestyle=titlestyle,
		rotatelabels=True, switchside=True, ticktype=2,
		textshiftx = 8.0, textshifty = 20.0 # Set to 0 for a clean rendering in Safari
		)
	
dwg.save(pretty=True)

