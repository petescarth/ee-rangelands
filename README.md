Global Rangeland App
====================

This repository consists of two applications:

 - The calibration ipython notebook, that:
	 - Takes a database of fractional cover field sites and extracts the reflectance data for the closest image acquisition in space and time
	 - Follows the endmember extration method outlined in Scarth 2010 to build an optimal set of endmembers for image unmixing
 - The Earth Engine based appspot app found at https://global-rangelands.appspot.com/ which **is planned** to include:
	 - Time series fractional cover estimates
	 - Time series decile maps for anomoly detection
	 - Summary tools for significant grasslands based on a [simplfied WWF grasslands map](https://www.google.com/fusiontables/data?docid=1ZEU45Vfzu9VTQMhwTeAoVY5eY2yIDqFz4JhUm5Fy#map:id=3)
	 - push alert tools for significat events

References
----------

Scarth, P., Röder, A., Schmidt, M., 2010b. Tracking grazing pressure and climate interaction - the role of Landsat fractional cover in time series analysis. In: Proceedings of the 15th Australasian Remote Sensing and Photogrammetry Conference (ARSPC), 13-17 September, Alice Springs, Australia. Alice Springs, NT.

