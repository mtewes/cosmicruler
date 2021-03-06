"""
Writes a cosmic ruler in SVG
github.com/mtewes/cosmicruler
"""

import svgwrite
import astropy.units as u
from astropy.cosmology import Planck15 as cosmo
from astropy.cosmology import z_at_value
import numpy as np

import logging


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
	"""Returns a list with the positions of subticks placed between the items of a so to divide these intervals into n parts
	
	Example: a = [1, 2, 3], n=2 returns [1.5, 2.5]
	"""
	output = []
	asorted = sorted(a)
	for i in range(len(a)-1):
		output.extend(np.linspace(asorted[i], asorted[i+1], n+1)[1:-1])
	#return np.array(output)	
	return output
	

def autosubtickmaker(a, majticks, medticks, minticks, type="lin2", transf=None):
	"""For each interval between the major ticks in array a, I append medticks and minticks to the given lists, according to type.
	
	I also add elements of a to the majticks
	
	The function pays attention not to place subticks on top of each other or on positions of a.
	"""
	
	
	if transf is None: # We set it to identity
		transf = lambda x: x
	
	asorted = sorted(a)
	
	for aitem in asorted:
		try:
			majticks.append(transf(aitem))
		except:
			logging.warning("transf failed on a majtick, but no prob")
			pass
	
	for i in range(len(asorted)-1):
		
		if type is "lin2" or type is "lin210": # medtick at half step
			medticks.append(transf(0.5 * (asorted[i] +  asorted[i+1])))
			
		if type is "lin210": # minticks at tenth of step
			for s in [0.1, 0.2, 0.3, 0.4, 0.6, 0.7, 0.8, 0.9]:
				minticks.append(transf(asorted[i] + s * (asorted[i+1] - asorted[i])))

		if type is "lin5" or type is "lin210": # minticks at fifths of step
			for s in [0.2, 0.4, 0.6, 0.8]:
				medticks.append(transf(asorted[i] + s * (asorted[i+1] - asorted[i])))

		if type is "log10": # minticks at 8 positions equispaced between the two (not the extrema, so 2, 3, 4, 5, 6, 7, 8, 9)
			if not np.isclose(asorted[i+1], 10*asorted[i]):
				raise RuntimeError("Fishy log auto subticks")
			for s in np.linspace(2.0, 9.0, 8):		
				minticks.append(transf(s * asorted[i]))
		

def remove_duplicates(l):
	"""
	
	"""
	if len(l) < 2:
		return l
	s = sorted(l)
	out = []
	out.append(s[0])
	for item in s[1:]:
		if not np.isclose(item, out[-1]):
			out.append(item)
	return out

def remove_duplicate_labels(labels):
	"""
	Similar, but for (pos, label) tuples
	We can't use the label text for identifactino, as they might appear several times on non-monotonous scales...
	"""
	out = []
	out.append(labels[0])
	for item in labels[1:]:
		isnew = True
		for outitem in out:
			if np.isclose(item[0], outitem[0]):
				isnew = False
		if isnew:
			out.append(item)
	return out



class Scale(object):
	"""Object to group all the information needed to draw a scale"""
	
	def __init__(self, name="scale", majticks=None, medticks=None, minticks=None, labels=None, title="Scale", extras=None):
		"""
		Object to store what is needed to draw a scale.
		Before drawing, all positions should be given in terms of relative positions "p", from 0 to 1.
		But you can first create the object using redshift z positions, and then call the method zptransform.
		
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
		
		if self.majticks is None:
			self.majticks = []
		if self.medticks is None:
			self.medticks = []
		if self.minticks is None:
			self.minticks = []
		if self.labels is None:
			self.labels = []
	
	
	def __str__(self):
		return """
		Scale '{self.title}'
		majticks: {self.majticks}
		medticks: {self.medticks}
		minticks: {self.minticks}
		labels: {self.labels}
		""".format(self=self)
	
	
	def apply_zptrans(self, zptrans):
		"""
		Transforms all "positions" from z to p
		"""
		self.majticks = [zptrans.p(value) for value in self.majticks]
		self.medticks = [zptrans.p(value) for value in self.medticks]
		self.minticks = [zptrans.p(value) for value in self.minticks]
		self.labels = [(zptrans.p(value), text) for (value, text) in self.labels]
		
		if self.extras is not None:
			if "peak" in self.extras:
				self.extras["peak"] = (zptrans.p(self.extras["peak"][0]), self.extras["peak"][1])
			
	
	def addautosubticks(self, a, type, transf=None):
		autosubtickmaker(a, self.majticks, self.medticks, self.minticks, type=type, transf=transf)
		
	
	
	@classmethod
	def fromz(cls, zptrans, *args, **kwargs):
		"""
		Factory function to construct a Scale from information given in redshift
		"""
		
		scale = cls(*args, **kwargs)
		scale.apply_zptrans(zptrans)
		return scale
		
	
	def clean(self):
		"""
		Removes duplicates
		"""
		self.majticks = remove_duplicates(self.majticks)
		
		self.labels = remove_duplicate_labels(self.labels)
		
		
		
	
		
	def simpledraw(self, dwg, x0, y0, l, 
		lw=0.5, tickl=8.0, 
		labelspace=3.0, titlespace=5.0, labelstyle=None, titlestyle=None,
		rotatelabels=False, switchside=False, ticktype=1,
		textshiftx=0.0, textshifty=0.0):
		"""Draws the scale onto a svgwrite.Drawing dwg
		
		x0 : svg x position of p=0
		y0 : svg y position of p=0
		l : svg lenght in x direction
		
		textxshift and textyshift are there to "hack" the text positions in case the
		"text alignment" is not understood by your SVG reader (e.g., Inkscape)
		
		
		"""
		
		self.clean()
		
		
		if labelstyle is None:
			labelstyle = "font-size:10;font-family:Helvetica Neue"
			
		if titlestyle is None:
			titlestyle = "font-size:12;font-family:CMU Serif"
		
		
		def xtrans(p):
			"""Transforms p into the svg position x
			"""
			#assert np.alltrue(p >= 0)
			#assert np.alltrue(p <= 1)
			return x0 + np.asarray(p) * l

			
		# A group for the scale
		scaleg = dwg.add(dwg.g(id=self.name+'-scale'))
	
	
		# Drawing the main line
		scaleg.add(dwg.line(start=(x0-lw/2.0, y0), end=(x0+l+lw/2.0, y0), style="stroke:black;stroke-width:{}".format(lw)))
	
		# Groups for ticks
		majticksg = scaleg.add(dwg.g(id=self.name+'-majticks'))
		majticksg.stroke('black', width=lw)
		medticksg = scaleg.add(dwg.g(id=self.name+'-medticks'))
		medticksg.stroke('black', width=lw)
		minticksg = scaleg.add(dwg.g(id=self.name+'-minticks'))
		minticksg.stroke('black', width=lw)
	
	
		# Drawing the ticks
		if switchside:
			signedtickl = - tickl
		else:
			signedtickl = tickl
		
		if ticktype is 1:
			majtickya = y0-lw/2.0
			majtickyb = y0+signedtickl
			medtickya = y0-lw/2.0
			medtickyb = y0+0.75*signedtickl
			mintickya = y0-lw/2.0
			mintickyb = y0+0.5*signedtickl
		elif ticktype is 2:
			majtickya = y0-lw/2.0
			majtickyb = y0+signedtickl
			medtickya = y0-lw/2.0
			medtickyb = y0+0.666*signedtickl
			mintickya = y0-lw/2.0
			mintickyb = y0+0.333*signedtickl
			
		else:
			raise RuntimeError("Unknown ticktype")
	
	
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
				style=labelstyle
				)
			)
			
		# Drawing the labels
		for (p, text) in self.labels:
			x = xtrans(p) + textshiftx
			if switchside:
				y = y0-tickl-labelspace
			else:
				y = y0+tickl+labelspace
				
			if rotatelabels:
				if switchside:
					text_anchor="start"
				else:
					text_anchor="end"
			
				labelsg.add(
					dwg.text(text, insert=(x, y),
						text_anchor=text_anchor, alignment_baseline="central",
						transform="rotate(-90, {}, {})".format(x, y)
						)
					)
			else:
				labelsg.add(
					dwg.text(text, insert=(x, y), 
						text_anchor="middle", alignment_baseline="hanging")
					)

	
		# Drawing the extras, if present
		if self.extras is not None:
			if "peak" in self.extras:
				(peakp, peaklabel) = self.extras["peak"]
				
				x = xtrans(peakp)
				
				majticksg.add(dwg.line(start=(x, majtickya), end=(x-0.66*tickl, majtickyb)))
				majticksg.add(dwg.line(start=(x, majtickya), end=(x+0.66*tickl, majtickyb)))
				
				xtxt = x + textshiftx
				
				if switchside:
					y = y0-tickl-labelspace
				else:
					y = y0+tickl+labelspace
				
				if rotatelabels:
					if switchside:
						text_anchor="start"
					else:
						text_anchor="end"
			
					labelsg.add(
						dwg.text(peaklabel, insert=(xtxt, y),
							text_anchor=text_anchor, alignment_baseline="central",
							transform="rotate(-90, {}, {})".format(xtxt, y)
							)
						)
				else:
					labelsg.add(
						dwg.text(peaklabel, insert=(xtxt, y), 
							text_anchor="middle", alignment_baseline="hanging")
						)

				
				
	
		#And we add a title
		if switchside:
			y = y0+titlespace + textshifty
			alignment_baseline="hanging"
		else:
			y = y0-titlespace + textshifty
			alignment_baseline="auto"
		titleg = scaleg.add(dwg.g(id=self.name+'-title', text_anchor="start",
			style=titlestyle))
		titleg.add(dwg.text(self.title, insert=(x0, y), alignment_baseline=alignment_baseline))
	
		return scaleg
	






def demoruler(filepath="demo.svg"):

		zptrans = ZPTrans(0.0, 2.0, "sqrt")
	

		# Draw the ruler
		dwg = svgwrite.Drawing(filepath, profile='full', debug=True)
		dwg.add(dwg.rect(insert=(10, 10), size=(1000, 160), rx=10, ry=10, fill="none", stroke="black"))
	
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
		title = "Lookback Time [Gyr]"
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
	
	
	majticks = []
	medticks = []
	minticks = []
	
	autosubtickmaker([1, 2, 3], majticks, medticks, minticks, type="lin")
	autosubtickmaker([3, 4], majticks, medticks, minticks, type="linmin")
	autosubtickmaker([10, 100], majticks, medticks, minticks, type="log")
	
	print majticks
	print medticks
	print minticks
	
	
	demoruler()
    
    