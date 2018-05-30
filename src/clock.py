from PIL import Image, ImageDraw
import io
import xml.etree.ElementTree as ET


def application(environ, start_response):
    tree = ET.parse('/usr/local/pnp4nagios/var/perfdata/SMYPXENXAP009V/Maintenance.xml')
    root = tree.getroot()
    perfdata = root.findall('NAGIOS_PERFDATA')[0].text.split('=')[1].split(';')
    current = int(perfdata[0])
    warn = int(perfdata[1])
    crit = int(perfdata[2])
    start = 90
    size = 22
    if current > crit:
        current = crit
    end = int((float(current) / float(crit)) * 360) + 90
    img = Image.new('RGB', (size, size), color='white')
    draw = ImageDraw.Draw(img)
    if current < warn:
        color = 'green'
    elif current < crit:
        color = 'orange'
    else:
        color = 'red'
    draw.ellipse([ 0, 0, img.size[0], img.size[1]], 'white', color)
    draw.pieslice([ 0, 0, img.size[0], img.size[1]], start, end, color, 64)
    del draw

    img_data = io.BytesIO()
    img.save(img_data, 'PNG')
    status = '200 OK'
    d = img_data.getvalue()
    response_headers = [('Content-type', 'image/png'),
                        ('Content-Length', str(len(d)))]
    start_response(status, response_headers)

    return [ d ]
