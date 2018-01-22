"""
Writes a cosmic ruler in SVG
github.com/mtewes/cosmicruler
"""

import svgwrite
import numpy as np




def drawscale(dwg, x0, y0, l, majticks=None, minticks=None, labels=None, title=None):
	"""Draws a scale to the drawing dwg.
	
	The scale goes from 0 to 1 in terms of the relative parameter p.
	
	x0 : svg position of p=0
	y0 : 
	l : svg lenght in x direction
	
	majticks : array of p values for major ticks
	minticks : idem for minor ticks
	labels : array of tuples (p value, "text")
	
	"""
	
	
	def xtrans(p):
		"""Transforms p into the svg position x
		"""
		assert np.alltrue(p >= 0)
		assert np.alltrue(p <= 1)
		return x0 + p * l
		
	
	# A group for the scale
	scaleg = dwg.add(dwg.g(id='scale'))
	scaleg.stroke('black', width=1)
	
	# The main line
	scaleg.add(dwg.line(start=(x0, y0), end=(x0+l, y0)))
	
	# Groups for ticks
	majticksg = scaleg.add(dwg.g(id='majticks'))
	majticksg.stroke(width=1)
	minticksg = scaleg.add(dwg.g(id='minticks'))
	
	
	majtickya = y0-0.5
	majtickyb = y0+6
	mintickya = y0-0
	mintickyb = y0+3
	
	for x in xtrans(majticks):
		majticksg.add(dwg.line(start=(x, majtickya), end=(x, majtickyb)))
	for x in xtrans(minticks):
		minticksg.add(dwg.line(start=(x, mintickya), end=(x, mintickyb)))
	
	
	# Group of labels
	#labelsg = scaleg.add(dwg.g(id='labels', style="font-size:30;font-family:Helvetica, Arial;font-weight:bold;font-style:oblique;stroke:black;stroke-width:1;fill:none"))
	labelsg = scaleg.add(dwg.g(id='labels', text_anchor="middle", style="font-size:12;font-family:CMU Serif, Arial;stroke:none"))
	

	for (p, text) in labels:
		x = xtrans(p)
		labelsg.add(dwg.text(text, insert=(x, y0+20)))
	
	
	#And we add a title
	titleg = scaleg.add(dwg.g(id='title', text_anchor="start", style="font-size:12;font-family:CMU Serif, Arial;stroke:none"))
	titleg.add(dwg.text(title, insert=(x0, y0-10)))
	
	return scaleg
	
	
	
	
	


def makeruler(filepath="demo.svg"):

	dwg = svgwrite.Drawing(filepath, profile='full', debug=True)
	
	
	
	dwg.add(dwg.rect(insert=(10, 10), size=(1000, 200), rx=10, ry=10, fill="none", stroke="black"))
	
	
	#majticks = np.arange(0, 1, 0.2)
	#minticks = np.arange(0, 1, 0.05)
	majticks = np.linspace(0, 1, 10+1)
	minticks = np.linspace(0, 1, 50+1)
	#print majticks
	#print minticks
	
	labels = [(p, "{}".format(p)) for p in majticks]
	
	
	scaleg = drawscale(dwg, 50, 50, 900, majticks, minticks, labels, title="Zero to One")
	
	
	#scaleg = drawscale(dwg, 50, 60, 600)
	#scaleg.rotate(15, center=(500, 50))
	
	
	#dwg.add(dwg.text('Test', insert=(0, 0.2)))
	
	
	dwg.save(pretty=True)


if __name__ == '__main__':
	makeruler()
    
    