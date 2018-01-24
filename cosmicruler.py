"""
Writes a cosmic ruler in SVG
github.com/mtewes/cosmicruler
"""

import svgwrite
import astropy.units as u
from astropy.cosmology import Planck15 as cosmo
from astropy.cosmology import z_at_value
import numpy as np


class ZPTrans(object):
	"""Class defining the transformation between redshift z and the relative position p.
	"""
	def __init__(self, zmax=2.0):
		"""
		zmax : redshift is linear from 0 (p=0) to zmax (p=1)
		"""
		self.zmax = zmax
		

	def z(self, p):
		"""redshift z correcponding to p"""
		return np.asarray(p) * self.zmax
	
	def p(self, z):
		"""relative position p corresponding to redshift z"""
		return np.asarray(z) / self.zmax



class Scale(object):
	"""Object to group all the information needed to draw a scale"""
	
	def __init__(self, name="demo", majticks=[0, 1], medticks=[0.5], minticks=[0.25, 0.75], labels=[(0.5, "Test")], title="Demo scale"):
		"""
		The tick and label position are given in relative positions "p", from 0 to 1.
		If you have positions in redshift, use the fromz() factory function below instead of this init!
	
		name : is used internally for ids
		majticks : array of p values for major ticks
		medticks: idem for intermediate ticks (larger than minor, but usually no labels...)
		minticks : idem for minor ticks
		labels : array of tuples (p value, "text")
		title : to be written as description on the scale
	
	
		"""
		
		self.name = name
		self.majticks = majticks
		self.medticks = medticks
		self.minticks = minticks
		self.labels = labels
		self.title = title
		
	
	@classmethod
	def fromz(cls, zptrans, name="demo", majticks=[0, 1], medticks=[0.5], minticks=[0.25, 0.75], labels=[(0.5, "Test")], title="Demo scale"):
		"""
		Factory function to construct a Scale from information given in redshift
		"""
		
		p_majticks = [zptrans.p(value) for value in majticks]
		p_medticks = [zptrans.p(value) for value in medticks]
		p_minticks = [zptrans.p(value) for value in minticks]
		p_labels = [(zptrans.p(value), text) for (value, text) in labels]
		
		return cls(name, p_majticks, p_medticks, p_minticks, p_labels, title)
		
	
		
	def simpledraw(self, dwg, x0, y0, l):
		"""Draws the scale onto a svgwrite.Drawing dwg
		
		x0 : svg x position of p=0
		y0 : svg y position of p=0
		l : svg lenght in x direction
		
		"""
		
		def xtrans(p):
			"""Transforms p into the svg position x
			"""
			#assert np.alltrue(p >= 0)
			#assert np.alltrue(p <= 1)
			return x0 + np.asarray(p) * l

			
		# A group for the scale
		scaleg = dwg.add(dwg.g(id=self.name+'-scale'))
	
	
		# Drawing the main line
		lw = 0.5
		scaleg.add(dwg.line(start=(x0, y0), end=(x0+l, y0), style="stroke:black;stroke-width:{}".format(lw)))
	
		# Groups for ticks
		majticksg = scaleg.add(dwg.g(id=self.name+'-majticks'))
		majticksg.stroke('black', width=lw)
		medticksg = scaleg.add(dwg.g(id=self.name+'-medticks'))
		medticksg.stroke('black', width=lw)
		minticksg = scaleg.add(dwg.g(id=self.name+'-minticks'))
		minticksg.stroke('black', width=lw)
	
		# Drawing the ticks
		majtickya = y0-lw/2.0
		majtickyb = y0+8
		medtickya = y0-lw/2.0
		medtickyb = y0+6
		mintickya = y0-lw/2.0
		mintickyb = y0+4
	
		for x in xtrans(self.majticks):
			majticksg.add(dwg.line(start=(x, majtickya), end=(x, majtickyb)))
		for x in xtrans(self.medticks):
			medticksg.add(dwg.line(start=(x, medtickya), end=(x, medtickyb)))
		for x in xtrans(self.minticks):
			minticksg.add(dwg.line(start=(x, mintickya), end=(x, mintickyb)))
	
		# Group for the labels
		# style="font-size:30;font-family:Helvetica, Arial;font-weight:bold;font-style:oblique;stroke:black;stroke-width:1;fill:none"
		# CMU Serif, Arial
		labelsg = scaleg.add(
			dwg.g(id=self.name+'-labels',
				text_anchor="middle",
				style="font-size:10;font-family:Helvetica Neue"
				)
			)
	
		# Drawing the labels
		for (p, text) in self.labels:
			x = xtrans(p)
			labelsg.add(dwg.text(text, insert=(x, y0+18)))
	
		#And we add a title
		titleg = scaleg.add(dwg.g(id=self.name+'-title', text_anchor="start",
			style="font-size:12;font-family:CMU Serif"))
		titleg.add(dwg.text(self.title, insert=(x0, y0-5)))
	
		return scaleg
	






def demoruler(filepath="demo.svg"):

	# Define a redshift transformation
	zptrans = ZPTrans()


	# Draw the ruler
	dwg = svgwrite.Drawing(filepath, profile='full', debug=True)
	dwg.add(dwg.rect(insert=(10, 10), size=(1000, 200), rx=10, ry=10, fill="none", stroke="black"))
	
	# Add a demo scale
	#scale = Scale()
	#scale.simpledraw(dwg, 30, 40, 960)
	
	spacing = 40
	
	
	# Redshift scale
	name = "redshift"
	title = "Redshift"
	labels = [(value, "{}".format(value)) for value in np.linspace(0, 2, 20+1)]
	majticks = [value for (value, text) in labels]
	medticks = np.linspace(0, 2, 40+1)
	minticks = np.linspace(0, 2, 200+1)
	scale = Scale.fromz(zptrans, name, majticks, medticks, minticks, labels, title)
	scale.simpledraw(dwg, 50, 40, 930)
	
	
	# Lookback time
	name = "lbt"
	title = "Time to launch [Gyr]"
	labels = [(z_at_value(cosmo.lookback_time, value * u.Gyr), "{:.0f}".format(value)) for value in np.arange(1, 10.1, 1)]
	majticks = [value for (value, text) in labels]
	medticks = [z_at_value(cosmo.lookback_time, value * u.Gyr) for value in np.arange(0.5, 10.6, 1)]
	minticks = [z_at_value(cosmo.lookback_time, value * u.Gyr) for value in np.arange(0.1, 10.51, 0.1)]
	majticks.append(0.0)
	labels.append((0.0, "0"))
	scale = Scale.fromz(zptrans, name, majticks, medticks, minticks, labels, title)
	scale.simpledraw(dwg, 50, 40+spacing, 930)


	# Distance modulus
	name = "distmod"
	title = "Distance modulus"
	labels = [(z_at_value(cosmo.distmod, value * u.mag), "{:.0f}".format(value)) for value in np.arange(37.0, 46.1, 1)]
	majticks = [value for (value, text) in labels]
	medticks = [z_at_value(cosmo.distmod, value * u.mag) for value in np.arange(37, 46, 0.5)]
	minticks = [z_at_value(cosmo.distmod, value * u.mag) for value in np.arange(37, 46, 0.1)]
	scale = Scale.fromz(zptrans, name, majticks, medticks, minticks, labels, title)
	scale.simpledraw(dwg, 50, 40+2*spacing, 930)
	
	
	# Pixel size in proper kpc
	name = "size"
	title = "VIS pixel scale [kpc] (transverse proper size subtending 0.1 arcsec)"
	f = 600.0 * u.kpc / u.arcmin
	labels = [(z_at_value(cosmo.kpc_proper_per_arcmin, value * f, zmax=1.6), "{}".format(value)) for value in list(np.arange(0.1, 0.85, 0.1)) + [0.85, 0.86, 0.865]]
	
	labels.extend([(z_at_value(cosmo.kpc_proper_per_arcmin, value * f, zmin=1.6), "{}".format(value)) for value in [0.865, 0.86]])
	
	majticks = [value for (value, text) in labels]
	medticks = [z_at_value(cosmo.kpc_proper_per_arcmin, value * f, zmax=1.6) for value in np.arange(0.1, 0.86, 0.05)]
	minticks = [z_at_value(cosmo.kpc_proper_per_arcmin, value * f, zmax=1.6) for value in np.arange(0.1, 0.86, 0.01)]
	scale = Scale.fromz(zptrans, name, majticks, medticks, minticks, labels, title)
	scale.simpledraw(dwg, 50, 40+3*spacing, 930)
	
	
	
	
	dwg.save(pretty=True)
	
	"""
	# The relative "p" scale goes from zero to one.
	# A Redshift scale
	# z = 2 * p
	
	zmajticks = np.linspace(0, zmax, 20+1)
	zmedticks = np.linspace(0, zmax, 40+1)
	zminticks = np.linspace(0, zmax, 200+1)
	
	majticks = np.linspace(0, 1, 20+1)
	medticks = np.linspace(0, 1, 40+1)
	minticks = np.linspace(0, 1, 200+1)
	labels = [(p, "{}".format(2.0*p)) for p in np.linspace(0, 1, 20+1)]
	zerooneg = drawscale(dwg, 50, 50, 900, majticks, medticks, minticks, labels,
		title="Redshift", name="redshift")
	
	"""
	
	# To test cosmology, Age in Gyr:
	"""
	agelabels = [(x * u.Gyr, "{}".format(x)) for x in [4, 6, 8, 10, 12]]
	agemajticks = np.array([4, 5, 6, 7, 8, 9, 10, 11, 12, 13]) * u.Gyr
	ageminticks = np.arange(3.5, 13.7, 0.5) * u.Gyr
	
	p_agemajticks = [z_at_value(cosmo.age, value)/2.0 for value in agemajticks]
	p_ageminticks = [z_at_value(cosmo.age, value)/2.0 for value in ageminticks]
	p_agelabels = [(z_at_value(cosmo.age, value)/2.0, text) for (value, text) in agelabels]
	
	ageg = drawscale(dwg, 50, 100, 900, p_agemajticks, p_ageminticks, p_agelabels,
		title="Age [Gyr]", name="age")
	"""
	
	"""
	# Lookback time in Gyr:
	lbtlabels = [(x * u.Gyr, "{}".format(x)) for x in np.arange(1, 10.1, 1)]
	lbtmajticks = np.array(np.arange(1, 10.1, 1)) * u.Gyr
	lbtminticks = np.array(np.arange(0.5, 10.1, 0.5)) * u.Gyr
	p_lbtmajticks = [z_at_value(cosmo.lookback_time, value)/2.0 for value in lbtmajticks]
	p_lbtminticks = [z_at_value(cosmo.lookback_time, value)/2.0 for value in lbtminticks]
	p_lbtlabels = [(z_at_value(cosmo.lookback_time, value)/2.0, text) for (value, text) in lbtlabels]
	
	p_lbtmedticks = []
	
	p_lbtmajticks.append(0.0)
	p_lbtlabels.append((0.0, "0"))
	
	lbtg = drawscale(dwg, 50, 100, 900, p_lbtmajticks, p_lbtmedticks, p_lbtminticks, p_lbtlabels,
		title="Time to launch [Gyr]", name="lbt")
	
	
	# Pixel size in proper kpc
	#zs = np.linspace(0, 2, 5)
	#print  cosmo.kpc_proper_per_arcmin(zs).value / 600.0
	
	sizelabels = [(x * 600.0 * u.kpc / u.arcmin, "{}".format(x)) for x in [0.2, 0.4, 0.6, 0.8, 0.85]]
	sizemajticks = np.array([0.2, 0.4, 0.6, 0.8]) * 600.0 * u.kpc / u.arcmin
	sizeminticks = np.array([0.1, 0.3, 0.5, 0.7, 0.81, 0.82, 0.83, 0.84, 0.85, 0.86]) * 600.0 * u.kpc / u.arcmin
	
	#print z_at_value(cosmo.kpc_proper_per_arcmin, 0.6 * 600.0 * u.kpc / u.arcmin, zmax=1.6)
	#exit()
	
	p_sizemajticks = [z_at_value(cosmo.kpc_proper_per_arcmin, value, zmax=1.6)/2.0 for value in sizemajticks]
	p_sizeminticks = [z_at_value(cosmo.kpc_proper_per_arcmin, value, zmax=1.6)/2.0 for value in sizeminticks]
	p_sizelabels = [(z_at_value(cosmo.kpc_proper_per_arcmin, value, zmax=1.6)/2.0, text) for (value, text) in sizelabels]
	
	p_sizemedticks = []
	
	sizeg = drawscale(dwg, 50, 150, 900, p_sizemajticks, p_sizemedticks, p_sizeminticks, p_sizelabels,
		title="VIS pixel scale [kpc] (transverse proper size subtending 0.1 arcsec)", name="size")
	
	
	#scaleg = drawscale(dwg, 50, 60, 600)
	#scaleg.rotate(15, center=(500, 50))
	"""
	
	#dwg.add(dwg.text('Test', insert=(0, 0.2)))
	
	
	


if __name__ == '__main__':
	demoruler()
    
    