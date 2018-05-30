from PIL import Image, ImageDraw
import io
import xml.etree.ElementTree as ET
from urlparse import parse_qs
import shlex

def error(size):
    img = Image.new('RGB', (size, size), color='white')
    draw = ImageDraw.Draw(img)
    draw.text((1,1), "NA", fill='red')
    del draw

    img_data = io.BytesIO()
    img.save(img_data, 'PNG')
    return ['200 OK', img_data.getvalue()]

def clock(data, size, 
        clock_color='white', 
        ok_color='green', ok_bgcolor='lightgreen', 
        warn_color='goldenrod', warn_bgcolor='gold',
        crit_color='red'):
    if data is None:
        return error(size)
    (current, warn, crit) = data
    if current is None or warn is None or crit is None:
        return error(size)
    start = 90
    if current > crit:
        current = crit
    if current <= warn:
        color = ok_color
        clock_color=ok_bgcolor
    elif current <= crit:
        color = warn_color
        clock_color = warn_bgcolor
    else:
        color = crit_color
        clock_color = crit_color
    end = int((float(current) / float(crit)) * 360) + 90
    img = Image.new('RGB', (size, size), color='white')
    draw = ImageDraw.Draw(img)
    draw.ellipse([ 1, 1, img.size[0] - 1, img.size[1] - 1], clock_color, color)
    draw.pieslice([ 1, 1, img.size[0] - 1, img.size[1] - 1], start, end, color, 64)
    del draw

    img_data = io.BytesIO()
    img.save(img_data, 'PNG')
    return ['200 OK', img_data.getvalue()]

def semaphore(data, size):
    if data is None:
        return error(size)
    (current, warn, crit) = data
    if current is None or warn is None or crit is None:
        return error(size)
    if current <= warn:
        color = 'green'
    elif current <= crit:
        color = 'yellow'
    else:
        color = 'red'
    img = Image.new('RGB', (size, size), color='white')
    draw = ImageDraw.Draw(img)
    draw.ellipse([ 1, 1, img.size[0] - 1, img.size[1] - 1], color, color)
    del draw

    img_data = io.BytesIO()
    img.save(img_data, 'PNG')
    return ['200 OK', img_data.getvalue()]

def get_data(host_name, perfdata, ds=0):
    output = ()
    try:
        filename = "/usr/local/pnp4nagios/var/perfdata/{0}/{1}.xml".format(host_name, perfdata)
        tree = ET.parse(filename)
        root = tree.getroot()
        perfdata = shlex.split(root.findall('NAGIOS_PERFDATA')[0].text)[ds].split('=')[1].split(';')
        current = (int(float(perfdata[0].replace('%', ''))) if '%' in perfdata[0] else int(perfdata[0]))
        output = (current, int(perfdata[1]), int(perfdata[2]))
    except:
        output = None
    return output

def application(environ, start_response):
    query = parse_qs(environ['QUERY_STRING'])
    perfdata = query.get('perfname', [None])[0]
    host_name = query.get('server', [None])[0]
    clock_size = 22

    if perfdata is None or host_name is None:
        [ status, output ] = error(clock_size)
    elif perfdata == 'Maintenance' or perfdata == 'Uptime' or perfdata == 'Unregistered':
        size = clock_size
        [ status, output ] = clock(get_data(host_name, perfdata), size)

    elif perfdata == 'Disk_space_on_C_' or perfdata == 'Disk_space_on_D_':
        size = clock_size
        [ status, output ] = clock(get_data(host_name, perfdata, ds=1), size)

    elif perfdata == 'Application_Errors' or perfdata == 'System_Errors':
        size = clock_size
        [ status, output ] = semaphore(get_data(host_name, perfdata), size)

    elif perfdata == 'Citrix_Services' or perfdata == 'Windows_Services_Spooler':
        size = clock_size
        [ status, output ] = semaphore(get_data(host_name, perfdata, ds=1), size)

    else:
        [ status, output ] = error(clock_size)

    response_headers = [('Content-type', 'image/png'),
                        ('Content-Length', str(len(output)))]
    start_response(status, response_headers)

    return [ output ]
