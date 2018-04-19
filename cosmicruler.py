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
	def __init__(self, zmin=0.0, zmax=2.0, type="lin"):
		"""
		zmax : redshift is linear from 0 (p=0) to zmax (p=1)
		"""
		self.zmin = zmin
		self.zmax = zmax
		self.type = type
		
	
		self.fct = np.sqrt
		self.invfct = np.square

	def z(self, p):
		"""redshift z corresponding to p"""
		if self.type == "lin":
			return np.asarray(p) * (self.zmax - self.zmin) + self.zmin
		if self.type == "log":
			return np.exp( np.asarray(p) * (np.log(self.zmax / self.zmin)) + np.log(self.zmin) )
		if self.type == "sqrt":
			return self.invfct(np.asarray(p) * (self.fct(self.zmax) - self.fct(self.zmin)) + self.fct(self.zmin))
	
	def p(self, z):
		"""relative position p corresponding to redshift z"""
		if self.type == "lin":
			return (np.asarray(z) - self.zmin) / (self.zmax - self.zmin)
		if self.type == "log":
			return np.log(np.asarray(z) / self.zmin) / np.log(self.zmax / self.zmin)
		if self.type == "sqrt":
			return (self.fct(np.asarray(z)) - self.fct(self.zmin)) / (self.fct(self.zmax) - self.fct(self.zmin))


def subticks(a, n=2):
	"""Returns an array with the positions of subticks placed between the items of a so to divide these intervals into n parts
	
	Example: a = [1, 2, 3], n=2 returns [1.5, 2.5]
	"""
	output = []
	asorted = sorted(a)
	for i in range(len(a)-1):
		output.extend(np.linspace(asorted[i], asorted[i+1], n+1)[1:-1])
	return np.array(output)	
	


class Scale(object):
	"""Object to group all the information needed to draw a scale"""
	
	def __init__(self, name="demo", majticks=[0, 1], medticks=[0.5], minticks=[0.25, 0.75], labels=[(0.5, "Test")], title="Demo scale", extras=None):
		"""
		The tick and label position are given in relative positions "p", from 0 to 1.
		If you have positions in redshift, use the fromz() factory function below instead of this init!
	
		name : is used internally for ids
		majticks : array of p values for major ticks
		medticks: idem for intermediate ticks (larger than minor, but usually no labels...)
		minticks : idem for minor ticks
		labels : array of tuples (p value, "text")
		title : to be written as description on the scale
	
		extras is a dict that can hold specific items that need to be drawn, such as "peaks" etc.
	
		"""
		
		self.name = name
		self.majticks = majticks
		self.medticks = medticks
		self.minticks = minticks
		self.labels = labels
		self.title = title
		self.extras = extras
		
	
	@classmethod
	def fromz(cls, zptrans, name="demo", majticks=[0, 1], medticks=[0.5], minticks=[0.25, 0.75], labels=[(0.5, "Test")], title="Demo scale", extras=None):
		"""
		Factory function to construct a Scale from information given in redshift
		"""
		
		p_majticks = [zptrans.p(value) for value in majticks]
		p_medticks = [zptrans.p(value) for value in medticks]
		p_minticks = [zptrans.p(value) for value in minticks]
		p_labels = [(zptrans.p(value), text) for (value, text) in labels]
		
		if extras is not None:
			p_extras = extras.copy()
			if "peak" in extras:
				p_extras["peak"] = (zptrans.p(extras["peak"][0]), extras["peak"][1])
			
		else:
			p_extras = None
		
		return cls(name, p_majticks, p_medticks, p_minticks, p_labels, title, p_extras)
		
	
		
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
	
		majtickl = 8.0
	
		# Drawing the ticks
		majtickya = y0-lw/2.0
		majtickyb = y0+majtickl
		medtickya = y0-lw/2.0
		medtickyb = y0+0.75*majtickl
		mintickya = y0-lw/2.0
		mintickyb = y0+0.5*majtickl
	
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
	
		# Drawing the extras, if present
		if self.extras is not None:
			if "peak" in self.extras:
				(peakp, peaklabel) = self.extras["peak"]
				x = xtrans(peakp)
				labelsg.add(dwg.text(peaklabel, insert=(x, y0+18)))
				majticksg.add(dwg.line(start=(x, majtickya), end=(x-majtickl, majtickyb)))
				majticksg.add(dwg.line(start=(x, majtickya), end=(x+majtickl, majtickyb)))
				
	
		#And we add a title
		titleg = scaleg.add(dwg.g(id=self.name+'-title', text_anchor="start",
			style="font-size:12;font-family:CMU Serif"))
		titleg.add(dwg.text(self.title, insert=(x0, y0-5)))
	
		return scaleg
	






def demoruler(filepath="demo.svg", type="lin"):

	# Define a redshift transformation
	if type == "lin":
		
		zptrans = ZPTrans(0.0, 2.0, "lin")
	
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
		labels = [(value, "{}".format(value)) for value in np.linspace(0.0, 2.0, 20+1)]
		majticks = [value for (value, text) in labels]
		medticks = np.linspace(0.0, 2.0, 40+1)
		minticks = np.linspace(0.0, 2.0, 200+1)
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
	

	
	
	
	if type == "log":
		
	
		zptrans = ZPTrans(0.01, 2.0, "log")
	

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
		labels = [(value, "{}".format(value)) for value in [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 2.0]]
		majticks = [value for (value, text) in labels]
		medticks = subticks(majticks, 2)
		minticks = subticks(majticks, 10)
		scale = Scale.fromz(zptrans, name, majticks, medticks, minticks, labels, title)
		scale.simpledraw(dwg, 50, 40, 930)
	
		
		"""
		# Lookback time
		name = "lbt"
		title = "Time to launch [Gyr]"
		labels = [(z_at_value(cosmo.lookback_time, value * u.Gyr), "{:.0f}".format(value)) for value in np.arange(1, 10.1, 1)]
		majticks = [value for (value, text) in labels]
		medticks = [z_at_value(cosmo.lookback_time, value * u.Gyr) for value in np.arange(0.5, 10.6, 1)]
		minticks = [z_at_value(cosmo.lookback_time, value * u.Gyr) for value in np.arange(0.1, 10.51, 0.1)]
		#majticks.append(0.0)
		#labels.append((0.0, "0"))
		scale = Scale.fromz(zptrans, name, majticks, medticks, minticks, labels, title)
		scale.simpledraw(dwg, 50, 40+spacing, 930)
		"""

		"""
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
	
		"""
	
	
	if type == "sqrt":
		
	
		zptrans = ZPTrans(0.0, 2.0, "sqrt")
	

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
		labels = [(value, "{}".format(value)) for value in [0.0, 0.01, 0.02, 0.04, 0.06, 0.08, 0.1, 0.2, 0.4, 0.6, 0.8, 1.0, 2.0]]
		majticks = [value for (value, text) in labels]
		medticks = subticks(majticks, 2)
		minticks = subticks(majticks, 10)
		scale = Scale.fromz(zptrans, name, majticks, medticks, minticks, labels, title)
		scale.simpledraw(dwg, 50, 40, 930)
	
		# Lookback time
		name = "lbt"
		title = "Time to launch [Gyr]"
		sourceticks = np.arange(1, 10.1, 1)
		labels = [(z_at_value(cosmo.lookback_time, value * u.Gyr), "{:.0f}".format(value)) for value in sourceticks]
		majticks = [value for (value, text) in labels]
		majticks.append(0.0)
		labels.append((0.0, "0"))
		medticks = [z_at_value(cosmo.lookback_time, value * u.Gyr) for value in subticks(sourceticks, 2)]
		minticks = [z_at_value(cosmo.lookback_time, value * u.Gyr) for value in subticks(sourceticks, 10)]
		scale = Scale.fromz(zptrans, name, majticks, medticks, minticks, labels, title)
		scale.simpledraw(dwg, 50, 40+spacing, 930)
	
		# Angular Diam dist
		name = "angdiam"
		title = "Angular diameter distance [Gpc]"
		sourceticks = [0.1, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6]
		labels = [(z_at_value(cosmo.angular_diameter_distance, value * u.Gpc, zmax=1.6), "{}".format(value)) for value in sourceticks]
		majticks = [value for (value, text) in labels]
		majticks.append(0.0)
		labels.append((0.0, "0"))
		medticks = [z_at_value(cosmo.angular_diameter_distance, value * u.Gpc, zmax=1.6) for value in subticks(sourceticks, 2)]
		minticks = [z_at_value(cosmo.angular_diameter_distance, value * u.Gpc, zmax=1.6) for value in subticks(sourceticks, 10)]
		scale = Scale.fromz(zptrans, name, majticks, medticks, minticks, labels, title)
		scale.simpledraw(dwg, 50, 40+2*spacing, 930)
	

	
	
	
	#And we add a title
	#textg = dwg.add(dwg.g(id="text", text_anchor="end", style="font-size:12;font-family:CMU Serif"))
	#textg.add(dwg.text(r"\u039B CDM cosmology, Planck 2015", insert=(980, 180)))
	
	dwg.save(pretty=True)
	
	


if __name__ == '__main__':
	demoruler(type="sqrt")
    
    