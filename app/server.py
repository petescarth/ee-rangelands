#!/usr/bin/env python
"""Web server for the Trendy Lights application.

The overall architecture looks like:

               server.py         script.js
 ______       ____________       _________
|      |     |            |     |         |
|  EE  | <-> | App Engine | <-> | Browser |
|______|     |____________|     |_________|
     \                               /
      '- - - - - - - - - - - - - - -'

The code in this file runs on App Engine. It's called when the user loads the
web page and when details about a polygon are requested.

Our App Engine code does most of the communication with EE. It uses the
EE Python library and the service account specified in config.py. The
exception is that when the browser loads map tiles it talks directly with EE.

The basic flows are:

1. Initial page load

When the user first loads the application in their browser, their request is
routed to the get() function in the MainHandler class by the framework we're
using, webapp2.

The get() function sends back the main web page (from index.html) along
with information the browser needs to render an Earth Engine map and
the IDs of the polygons to show on the map. This information is injected
into the index.html template through a templating engine called Jinja2,
which puts information from the Python context into the HTML for the user's
browser to receive.

Note: The polygon IDs are determined by looking at the static/polygons
folder. To add support for another polygon, just add another GeoJSON file to
that folder.

2. Getting details about a polygon

When the user clicks on a polygon, our JavaScript code (in static/script.js)
running in their browser sends a request to our backend. webapp2 routes this
request to the get() method in the DetailsHandler.

This method checks to see if the details for this polygon are cached. If
yes, it returns them right away. If no, we generate a Wikipedia URL and use
Earth Engine to compute the brightness trend for the region. We then store
these results in a cache and return the result.

Note: The brightness trend is a list of points for the chart drawn by the
Google Visualization API in a time series e.g. [[x1, y1], [x2, y2], ...].

Note: memcache, the cache we are using, is a service provided by App Engine
that temporarily stores small values in memory. Using it allows us to avoid
needlessly requesting the same data from Earth Engine over and over again,
which in turn helps us avoid exceeding our quota and respond to user
requests more quickly.

"""

import json
import os

import config
import ee
import jinja2
import webapp2

from google.appengine.api import memcache


###############################################################################
#                             Web request handlers.                           #
###############################################################################


class MainHandler(webapp2.RequestHandler):
  """A servlet to handle requests to load the main Trendy Lights web page."""

  def get(self, path=''):
    """Returns the main web page, populated with EE map and polygon info."""
    mapid = GetTrendyMapId()
    template_values = {
        'eeMapId': mapid['mapid'],
        'eeToken': mapid['token'],
        'serializedPolygonIds': json.dumps(POLYGON_IDS)
    }
    template = JINJA2_ENVIRONMENT.get_template('index.html')
    self.response.out.write(template.render(template_values))


class DetailsHandler(webapp2.RequestHandler):
  """A servlet to handle requests for details about a Polygon."""

  def get(self):
    """Returns details about a polygon."""
    polygon_id = self.request.get('polygon_id')
    if polygon_id in POLYGON_IDS:
      content = GetPolygonTimeSeries(polygon_id)
    else:
      content = json.dumps({'error': 'Unrecognized polygon ID: ' + polygon_id})
    self.response.headers['Content-Type'] = 'application/json'
    self.response.out.write(content)


# Define webapp2 routing from URL paths to web request handlers. See:
# http://webapp-improved.appspot.com/tutorials/quickstart.html
app = webapp2.WSGIApplication([
    ('/details', DetailsHandler),
    ('/', MainHandler),
])


###############################################################################
#                                   Helpers.                                  #
###############################################################################

# Endmembers derived from the Auscover Field Sites Database using attached ipythron notebook
# Overall global RMSE unmixing error is 13.1%
# RMSE of the derived fractions against 675 field sites is:
# Bare:  0.11959856
# Dead:  0.14945009
# Green: 0.12286588




# Builds Interactive Terms
def applytransforms(mcd43Image):
    # Select the algorithm bands and rescale to Qld RSC values
    useBands = mcd43Image.select("Nadir_Reflectance_Band4", "Nadir_Reflectance_Band1", "Nadir_Reflectance_Band2", "Nadir_Reflectance_Band5","Nadir_Reflectance_Band6","Nadir_Reflectance_Band7")
    logBands = useBands.log();
    # Combine the bands into a new image
    # Note that this line is missing logBands.expression("b('Nadir_Reflectance_Band2') * b('Nadir_Reflectance_Band7')"),
    return ee.Image.cat(
      useBands.expression("b('Nadir_Reflectance_Band4') * b('Nadir_Reflectance_Band1')"),
      useBands.expression("b('Nadir_Reflectance_Band4') * b('Nadir_Reflectance_Band2')"),
      useBands.expression("b('Nadir_Reflectance_Band4') * b('Nadir_Reflectance_Band5')"),
      useBands.expression("b('Nadir_Reflectance_Band4') * b('Nadir_Reflectance_Band6')"),
      useBands.expression("b('Nadir_Reflectance_Band4') * b('Nadir_Reflectance_Band7')"),
      useBands.expression("b('Nadir_Reflectance_Band4') * logs", {'logs': logBands}),
      useBands.expression("b('Nadir_Reflectance_Band1') * b('Nadir_Reflectance_Band2')"),
      useBands.expression("b('Nadir_Reflectance_Band1') * b('Nadir_Reflectance_Band5')"),
      useBands.expression("b('Nadir_Reflectance_Band1') * b('Nadir_Reflectance_Band6')"),
      useBands.expression("b('Nadir_Reflectance_Band1') * b('Nadir_Reflectance_Band7')"),
      useBands.expression("b('Nadir_Reflectance_Band1') * logs", {'logs': logBands}),
      useBands.expression("b('Nadir_Reflectance_Band2') * b('Nadir_Reflectance_Band5')"),
      useBands.expression("b('Nadir_Reflectance_Band2') * b('Nadir_Reflectance_Band6')"),
      useBands.expression("b('Nadir_Reflectance_Band2') * b('Nadir_Reflectance_Band7')"),
      useBands.expression("b('Nadir_Reflectance_Band2') * logs", {'logs': logBands}),
      useBands.expression("b('Nadir_Reflectance_Band5') * b('Nadir_Reflectance_Band6')"),
      useBands.expression("b('Nadir_Reflectance_Band5') * b('Nadir_Reflectance_Band7')"),
      useBands.expression("b('Nadir_Reflectance_Band5') * logs", {'logs': logBands}),
      useBands.expression("b('Nadir_Reflectance_Band6') * b('Nadir_Reflectance_Band7')"),
      useBands.expression("b('Nadir_Reflectance_Band6') * logs", {'logs': logBands}),
      useBands.expression("b('Nadir_Reflectance_Band7') * logs", {'logs': logBands}),
      logBands.expression("b('Nadir_Reflectance_Band4') * b('Nadir_Reflectance_Band1')"),
      logBands.expression("b('Nadir_Reflectance_Band4') * b('Nadir_Reflectance_Band2')"),
      logBands.expression("b('Nadir_Reflectance_Band4') * b('Nadir_Reflectance_Band5')"),
      logBands.expression("b('Nadir_Reflectance_Band4') * b('Nadir_Reflectance_Band6')"),
      logBands.expression("b('Nadir_Reflectance_Band4') * b('Nadir_Reflectance_Band7')"),
      logBands.expression("b('Nadir_Reflectance_Band1') * b('Nadir_Reflectance_Band2')"),
      logBands.expression("b('Nadir_Reflectance_Band1') * b('Nadir_Reflectance_Band5')"),
      logBands.expression("b('Nadir_Reflectance_Band1') * b('Nadir_Reflectance_Band6')"),
      logBands.expression("b('Nadir_Reflectance_Band1') * b('Nadir_Reflectance_Band7')"),
      logBands.expression("b('Nadir_Reflectance_Band2') * b('Nadir_Reflectance_Band5')"),
      logBands.expression("b('Nadir_Reflectance_Band2') * b('Nadir_Reflectance_Band6')"),
      logBands.expression("b('Nadir_Reflectance_Band5') * b('Nadir_Reflectance_Band6')"),
      logBands.expression("b('Nadir_Reflectance_Band5') * b('Nadir_Reflectance_Band7')"),
      logBands.expression("b('Nadir_Reflectance_Band6') * b('Nadir_Reflectance_Band7')"),
      useBands,
      logBands,
      ee.Image(0.25))
      
  
 
def GetTrendyMapId():
  # Import MODIS Imagery
  mcd43a4 = ee.ImageCollection('MODIS/MCD43A4')

  # Get the latest image
  latestImage = mcd43a4.sort('system:time_start', False ).limit(1).median()
  transformedImage = applytransforms(latestImage)

  # Cmpute the cover Fractions
  coverFractions = transformedImage.unmix([end_bare,end_gren,end_dead]).select(["band_0","band_1","band_2"])

  return ee.Image(latestImage).select('Nadir_Reflectance_Band6', 'Nadir_Reflectance_Band2', 'Nadir_Reflectance_Band1').getMapId({'min': '100,100,100', 'max': '4000,4000,4000'})

#   """Returns the MapID for the night-time lights trend map."""
#   collection = ee.ImageCollection(IMAGE_COLLECTION_ID)

#   # Add a band containing image date as years since 1991.
#   def CreateTimeBand(img):
#     year = ee.Date(img.get('system:time_start')).get('year').subtract(1991)
#     return ee.Image(year).byte().addBands(img)
#   collection = collection.select('stable_lights').map(CreateTimeBand)

#   # Fit a linear trend to the nighttime lights collection.
#   fit = collection.reduce(ee.Reducer.linearFit())
#   return fit.getMapId({
#       'min': '0',
#       'max': '0.18,20,-0.18',
#       'bands': 'scale,offset,scale',
#   })


def GetPolygonTimeSeries(polygon_id):
  """Returns details about the polygon with the passed-in ID."""
  details = memcache.get(polygon_id)

  # If we've cached details for this polygon, return them.
  if details is not None:
    return details

  details = {'wikiUrl': WIKI_URL + polygon_id.replace('-', '%20')}

  try:
    details['timeSeries'] = ComputePolygonTimeSeries(polygon_id)
    # Store the results in memcache.
    memcache.add(polygon_id, json.dumps(details), MEMCACHE_EXPIRATION)
  except ee.EEException as e:
    # Handle exceptions from the EE client library.
    details['error'] = str(e)

  # Send the results to the browser.
  return json.dumps(details)


def ComputePolygonTimeSeries(polygon_id):
  """Returns a series of brightness over time for the polygon."""
  collection = ee.ImageCollection(IMAGE_COLLECTION_ID)
  collection = collection.select('stable_lights').sort('system:time_start')
  feature = GetFeature(polygon_id)

  # Compute the mean brightness in the region in each image.
  def ComputeMean(img):
    reduction = img.reduceRegion(
        ee.Reducer.mean(), feature.geometry(), REDUCTION_SCALE_METERS)
    return ee.Feature(None, {
        'stable_lights': reduction.get('stable_lights'),
        'system:time_start': img.get('system:time_start')
    })
  chart_data = collection.map(ComputeMean).getInfo()

  # Extract the results as a list of lists.
  def ExtractMean(feature):
    return [
        feature['properties']['system:time_start'],
        feature['properties']['stable_lights']
    ]
  return map(ExtractMean, chart_data['features'])


def GetFeature(polygon_id):
  """Returns an ee.Feature for the polygon with the given ID."""
  # Note: The polygon IDs are read from the filesystem in the initialization
  # section below. "sample-id" corresponds to "static/polygons/sample-id.json".
  path = POLYGON_PATH + polygon_id + '.json'
  path = os.path.join(os.path.split(__file__)[0], path)
  with open(path) as f:
    return ee.Feature(json.load(f))


###############################################################################
#                                   Constants.                                #
###############################################################################


# Memcache is used to avoid exceeding our EE quota. Entries in the cache expire
# 24 hours after they are added. See:
# https://cloud.google.com/appengine/docs/python/memcache/
MEMCACHE_EXPIRATION = 60 * 60 * 24

# The ImageCollection of the night-time lights dataset. See:
# https://earthengine.google.org/#detail/NOAA%2FDMSP-OLS%2FNIGHTTIME_LIGHTS
IMAGE_COLLECTION_ID = 'NOAA/DMSP-OLS/NIGHTTIME_LIGHTS'

# The file system folder path to the folder with GeoJSON polygon files.
POLYGON_PATH = 'static/polygons/'

# The scale at which to reduce the polygons for the brightness time series.
REDUCTION_SCALE_METERS = 20000

# The Wikipedia URL prefix.
WIKI_URL = 'http://en.wikipedia.org/wiki/'



# The Computed Endmembers
end_gren = [1.005625793718393224e-01,1.551381619046308113e-01,1.792972445650116153e-01,1.756139193904675544e-01,1.409032551487235385e-01,-4.779793393912765698e-01,-3.863266414066787169e-01,-2.117543746254724746e-01,-1.678902136214300567e-01,-1.745431337396821381e-01,-2.403627985684871349e-01,1.985669393903456148e-01,1.986106673443171489e-01,1.798445329687358984e-01,1.347556128418881671e-01,-4.230897452709314055e-01,-4.306222970080941792e-01,-1.784168435713744949e-01,-2.087463228039195817e-01,-2.525836273873255378e-01,-3.519714061731354926e-01,2.493734504017069697e-01,2.756349644337070526e-01,2.214416586870512071e-01,-3.947699254951768655e-01,-2.140265169616704932e-01,-4.541274778620738029e-01,-3.787141551387274707e-01,-2.212936799517399578e-01,-1.761121705287621297e-01,2.131049159247370151e-01,1.555961382991326025e-01,-1.965963040151643970e-01,-2.830078567396365208e-01,-3.215068847604295454e-01,-4.270254941278601168e-01,-3.920532077778883795e-01,-4.393438610960144763e-01,1.139614936774503429e-01,-1.311489035400711933e-01,-3.933544485165051396e-01,-1.371423398967817342e-01,-3.626460253983346815e-01,-4.545950218460690917e-01,-5.836848311142593948e-01,-3.191089493163550700e-02,-3.224051458458987440e-01,-5.532773510021347929e-02,-2.759065442549579195e-01,-3.693207960693587477e-01,-4.824883750352684242e-01,-5.599811410645313403e-01,-4.618333710369355583e-01,2.638597724326164351e-01,3.657374965386450683e-01,3.747929451692371683e-01,6.583876748674915014e-01,5.451015751013433830e-01,1.083009465127019316e-01,-1.935712814253734149e-01,-6.658464327485663636e-01,7.608717656278304875e-02,-3.177089270701012325e-01,-5.280598956024164931e-02,-5.452106237221799878e-01,3.388294075045473752e-01,3.928265454868017370e-01,5.456166415438652439e-01,5.396204163342579463e-01,5.018642612505221923e-01,3.783475769849550807e-01,-5.231001864092722498e-01,-7.037557367909558215e-01,-2.423698219956213484e-01,-3.843516530893263949e-01,-4.458789415024453362e-01,-6.129339166090426172e-01,0.25];
end_dead = [1.403263555258253970e-01,1.740844187309274482e-01,2.143776613700686950e-01,2.255999818141902202e-01,1.798486122880957883e-01,-5.094852507233389449e-01,-3.943909593752877307e-01,-3.271005665360072756e-01,-2.398086866572867459e-01,-2.170372016296666096e-01,-2.928484835748055848e-01,2.223184524922829086e-01,2.575036368121275121e-01,2.602762597110128695e-01,1.931895170928574212e-01,-4.820346521695523245e-01,-4.530716612145118116e-01,-3.526026536396565381e-01,-2.871558826934162978e-01,-2.870497154688096408e-01,-4.239204810729221284e-01,2.484599564187424114e-01,2.861343176253623999e-01,2.281157131292944340e-01,-2.709993459043758546e-01,-1.894416977490074316e-01,-4.114788420817422909e-01,-3.305979743382004843e-01,-2.178179862993682714e-01,-1.965442916311349320e-01,3.017090569531513111e-01,2.272570720493811425e-01,-1.660063649921281748e-01,-2.078556996556621961e-01,-4.160412189662338611e-01,-3.834399519794880473e-01,-3.046072308937279871e-01,-3.455947654101590438e-01,2.145926981364830732e-01,-1.759330674468164712e-01,-3.226994801832344106e-01,-3.554447967112595030e-01,-3.608555462410469872e-01,-3.653556708703253886e-01,-5.288465893028195808e-01,4.871148572665796872e-02,-1.921852869110349249e-01,-1.538614444787815561e-01,-2.039512166097949830e-01,-2.536145208364682380e-01,-4.333713519267466396e-01,-3.290012282223230278e-01,-2.558320130370689283e-01,9.049690808748311888e-02,2.429555937637380980e-01,2.593593821267571875e-01,3.562463529501999071e-01,3.307446747853375335e-01,1.799196323512836926e-01,-2.219392694669459487e-01,-3.576993626520880709e-01,1.845227897749066731e-02,-1.685206360984441709e-01,5.580296776298742517e-02,-4.145629855116072515e-01,4.135862588851957344e-01,4.966752147834995745e-01,5.020998941719694297e-01,5.618702492116707248e-01,5.940529187364148589e-01,4.158125345134185968e-01,-3.348135919834706042e-01,-4.891960223481561787e-01,-4.775706041789192779e-01,-4.063217768189702483e-01,-3.902195969483839844e-01,-5.475248235551297693e-01,0.25];
end_bare = [1.557756133661153952e-01,1.802192110730069519e-01,2.214149969321710376e-01,2.378169515722290961e-01,2.167823936748812796e-01,-5.003139008582664360e-01,-3.858620353742320264e-01,-3.421557006601864126e-01,-2.561822930393134468e-01,-2.312584786760632782e-01,-2.534492576792338192e-01,2.320565217858724938e-01,2.736918995210841365e-01,2.878776178964150834e-01,2.581029762878466194e-01,-4.745006463997653023e-01,-4.212879123400909420e-01,-3.806564066788480361e-01,-3.037867195241924501e-01,-2.907748187098708748e-01,-3.319295543017048988e-01,2.418232712425302799e-01,2.813392488119939583e-01,2.763479007400641008e-01,-2.553586812522712912e-01,-2.148104467732427636e-01,-4.048503104537182762e-01,-3.368292685824204602e-01,-2.339882670913794593e-01,-1.459367612878482712e-01,2.994817350480266094e-01,2.997062696318842923e-01,-1.429721098700335868e-01,-2.050814814822079502e-01,-4.074130135695290811e-01,-3.783440378975941876e-01,-3.143608342429669023e-01,-2.387095954855755486e-01,3.026018626233351050e-01,-5.715470865161947911e-02,-1.997813302239145050e-01,-2.918934998203080999e-01,-3.067641746997048502e-01,-3.341194694934919718e-01,-3.347398350315027860e-01,-6.561644819416791174e-02,-2.114976663325430772e-01,-2.424937905246192793e-01,-2.467185800323841716e-01,-2.872824680797123054e-01,-3.344593134383595512e-01,-2.846135649729091277e-01,-2.302400388348356253e-01,6.664500979015522408e-02,2.303978017433380432e-01,2.281681038181598287e-01,2.555933168357400476e-01,2.387943621178491016e-01,7.191996580933962546e-02,-1.306805956480629749e-01,-3.364273224868226664e-01,1.181603266047939471e-01,-1.141124425180693319e-01,1.052852993043106866e-01,-4.738702699799992590e-01,4.284487379128869566e-01,5.211981857016393382e-01,4.921858390252278892e-01,5.432637332898500038e-01,5.550396166730965364e-01,5.269385781005170299e-01,-3.468334523171409667e-01,-5.224070998521183062e-01,-5.006934427040702351e-01,-4.453181641709889060e-01,-4.792341641719014556e-01,-4.946308016878979696e-01,0.25];

###############################################################################
#                               Initialization.                               #
###############################################################################


# Use our App Engine service account's credentials.
EE_CREDENTIALS = ee.ServiceAccountCredentials(config.EE_ACCOUNT, config.EE_PRIVATE_KEY_FILE)


# Read the polygon IDs from the file system.
POLYGON_IDS = [name.replace('.json', '') for name in os.listdir(POLYGON_PATH)]

# Create the Jinja templating system we use to dynamically generate HTML. See:
# http://jinja.pocoo.org/docs/dev/
JINJA2_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    autoescape=True,
    extensions=['jinja2.ext.autoescape'])

# Initialize the EE API.
ee.Initialize(EE_CREDENTIALS)



