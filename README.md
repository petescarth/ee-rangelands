Global Rangelands - *Grassy Knowledge*
====================

This repository consists of two applications:

 - The calibration ipython notebook, that:
	 - Takes a database of fractional cover field sites and extracts the reflectance data for the closest image acquisition in space and time
	 - Follows the endmember extration method outlined in Scarth 2010 to build an optimal set of endmembers for image unmixing
 - The Earth Engine based appspot app
	 - Forked from [Trendy Lights](https://github.com/google/earthengine-api/tree/master/demos/trendy-lights)
	 - Currently running at https://global-rangelands.appspot.com/ 
	 -  **Is planned** to include:
		 - Time series fractional cover estimates
		 - Time series decile maps for anomoly detection
		 - Summary tools for significant grasslands based on a [simplfied WWF grasslands map](https://www.google.com/fusiontables/data?docid=1ZEU45Vfzu9VTQMhwTeAoVY5eY2yIDqFz4JhUm5Fy#map:id=3)
		 - Push alert tools for significant events

References
----------

Scarth, P., Röder, A., Schmidt, M., 2010b. Tracking grazing pressure and climate interaction - the role of Landsat fractional cover in time series analysis. In: Proceedings of the 15th Australasian Remote Sensing and Photogrammetry Conference (ARSPC), 13-17 September, Alice Springs, Australia. Alice Springs, NT.

