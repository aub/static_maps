#!/opt/bcs/python2.6
#
from cgi import parse_qs, escape
import mapnik

mapsHash = {}
def application(environ, start_response):
    global mapsHash

    parameters = parse_qs(environ.get('QUERY_STRING', ''))

    width = int(escape(parameters['width'][0]))
    height = int(escape(parameters['height'][0]))

    key = str(width) + str(height)
    if not key in mapsHash:
        mapsHash[key] = mapnik.Map(width, height)
        mapnik.load_map(mapsHash[key], '/opt/bcs/packages/map_style-0.0.1/mapfile.xml')
    theMap = mapsHash[key]

    bbox = None
    buf = 0.001

    markers = parameters['markers']
    for marker in markers:
        split = escape(marker).split(',')
        lng_lat = ([float(split[0]), float(split[1])])
        if bbox == None:
            bbox = mapnik.Envelope(lng_lat[0] - buf, lng_lat[1] - buf, lng_lat[0] + buf, lng_lat[1] + buf)
        else:
            bbox.expand_to_include(mapnik.Envelope(lng_lat[0] - buf, lng_lat[1] - buf, lng_lat[0] + buf, lng_lat[1] + buf))

    bbox = bbox * 1.5
    bbox = bbox.forward(mapnik.Projection("+init=epsg:900913"))
    theMap.zoom_to_box(bbox)

    draw = mapnik.Image(width, height)
    mapnik.render(theMap, draw)
    img = draw.tostring('png')

    start_response('200 OK', [('Content-Type', 'image/png'), ('Content-Length', str(len(img)))])
    return [img]

