#!/usr/bin/python
import sys, subprocess, os, ogr

def main(argv):
	inputfile = argv[0]

	totalpolygons = 0

	# 2 get the shapefile driver
	driver = ogr.GetDriverByName('ESRI Shapefile')

	# 4 create a new data source and layer
	fn = inputfile + '/' + inputfile + '.shp'
	if os.path.exists(fn):driver.DeleteDataSource(fn)
	outDS = driver.CreateDataSource(fn)
	if outDS is None:
		print 'Could not create consolidated shapefile'
		sys.exit(1)
	outLayer = outDS.CreateLayer(inputfile, geom_type=ogr.wkbPolygon)

	# new field definitions for this shapefile
	# color definition
	colorDefn = ogr.FieldDefn("Color", ogr.OFTInteger)
	colorDefn.SetWidth(2)
	colorDefn.SetPrecision(0)
	outLayer.CreateField( colorDefn )

	# dot count definition
	dotCountDefn = ogr.FieldDefn("Dot Count", ogr.OFTInteger)
	dotCountDefn.SetWidth(2)
	dotCountDefn.SetPrecision(0)
	outLayer.CreateField( dotCountDefn )

	# dot type definition
	dotTypeDefn = ogr.FieldDefn("Dot Type", ogr.OFTInteger)
	dotTypeDefn.SetWidth(1)
	dotTypeDefn.SetPrecision(0)
	outLayer.CreateField( dotTypeDefn )

	for ff in os.listdir(inputfile):
		if ff.endswith(".tif"):
			base_name = ff[:ff.find(".tif")]
			shapefile = inputfile + "/" + base_name + "/" + base_name + "-traced.shp"

			if totalpolygons == 0:
				os.system("cp " + inputfile + "/" + base_name + "/" + base_name + "-traced.prj " + inputfile + "/" + inputfile + ".prj")
			
			# 3 open the input data source and get the layer
			inDS = driver.Open(shapefile, 0) #shows cover at given points
			if inDS is None:
				print 'Could not open shapefile: ' + shapefile
				sys.exit(1)
			inLayer = inDS.GetLayer()

			# 5 get the FieldDefn's for the id and cover fields in the input shapefile
			# feature = inLayer.GetFeature(0)
			# idFieldDefn = feature.GetFieldDefnRef('DN')
			# colorFieldDefn = feature.GetFieldDefnRef('Color')
			# dotCountFieldDefn = feature.GetFieldDefnRef('Dot Count')
			# dotTypeFieldDefn = feature.GetFieldDefnRef('Dot Type')

			# 6 get the FeatureDefn for the output layer
			featureDefn = inLayer.GetLayerDefn()

			# 7 loop through the input features
			inFeature = inLayer.GetNextFeature()
			while inFeature:
				totalpolygons = totalpolygons + 1
				# create a new feature
				outFeature = ogr.Feature(featureDefn)#using featureDefn created in step 6

				# set the geometry
				geom = inFeature.GetGeometryRef()
				outFeature.SetGeometry(geom) #move it to the new feature

				# set the attributes
				outFeature.SetField('DN', totalpolygons) #move it to the new feature

				color = inFeature.GetField('Color')
				outFeature.SetField('Color', color)

				dc = inFeature.GetField('Dot Count')
				outFeature.SetField('Dot Count', dc)

				dt = inFeature.GetField('Dot Type')
				outFeature.SetField('Dot Type', dt)

				# add the feature to the output layer
				outLayer.CreateFeature(outFeature)

				# destroy the output feature
				outFeature.Destroy()

				# destroy the input feature and get a new one
				inFeature.Destroy()
				inFeature = inLayer.GetNextFeature()

			# close the data sources
			inDS.Destroy()
	
	outDS.Destroy() #flush out the last changes here

if __name__ == "__main__":
	main(sys.argv[1:])

