import cosmicruler
import astropy.table
#import matplotlib.pyplot as plt



def scale_counts_to_z(cat, catfactor=1.0, zptrans=None, 
	majticks=[0.1, 1.0, 10.0], medticks=[], minticks=[], labels=[(1.0, "1.0")],
	name="counts", title="Cumulated counts to redshift", z_name="true_redshift_gal"):
	"""
	
	Function that builds a scale with "counts" of sources in a catalog up to the redshift.
	
	cat: an astropy table
	
	ticks : values of counts that you want to show, in your prefered unit (e.g., gals per arcmin2)
	labels: count, and label for this count to show (in the same unit)

	catfactor: how many gals are in your cat for a unit "count" ?
		This is a function of area, subsampling, ...
	
	
	"""

	if zptrans is None:
		zptrans = cosmicruler.ZPTrans()

	cat.sort(z_name)

	def find_redshifts(ticks):
		"""
		returns a list of redshifts corresponding to the given "count" ticks
		"""
		zs = []
		for count in ticks:
			count_in_cat = int(count * catfactor)
			print("count:", count, " -> count in cat:", count_in_cat)

			if count_in_cat < 10 or count_in_cat > len(cat):
				raise RuntimeError("Out of range")

			z1 = cat[count_in_cat-1][z_name]
			z2 = cat[count_in_cat+1][z_name]
			print(z1, z2)
		
			z = 0.5 * (z1 + z2)
			zs.append(z)
		
		assert len(zs) == len(ticks)
		return zs
		
	
	majticks = find_redshifts(majticks) # Those are now in redshift
	medticks = find_redshifts(medticks)
	minticks = find_redshifts(minticks)
	
	# Find label positions in redshifts
	labelcounts = [value for (value, text) in labels]
	labelzs = find_redshifts(labelcounts)
	labels = [(z, text) for (z, (value, text)) in zip(labelzs, labels)]

	outscale = cosmicruler.Scale.fromz(zptrans, name=name, majticks=majticks, medticks=medticks, minticks=minticks, labels=labels, title=title)
	
	return outscale




if __name__ == '__main__':
	
    
	catpath = "2562.fits"
	cat = astropy.table.Table.read(catpath)
	cat = cat[cat["euclid_vis"] < 24.5]

	
	subsamplefactor = (1./256.) * 0.1
	overal_square_degrees = 5000.0
	catfactor = (overal_square_degrees * 3600) * subsamplefactor


	make_count_scale(cat, catfactor, counts=[0.1, 1.0, 10.0])



#cat = cat[0::100]

#plt.hist(cat["true_redshift_gal"])

#plt.scatter(cat["true_redshift_gal"], cat["euclid_vis"], marker=".")

#plt.show()