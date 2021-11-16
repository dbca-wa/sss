import bottle
from email import encoders
import email.utils
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import io
import json
import os
import png
import pyqrcode
import requests
import settings
import smtplib
import ssl
import traceback


"""app_id = "480daeea-6cb0-4b79-8b31-2f2c210f5b33"
client_secret = "9f3F1RukXiTuv3F.7Li1Tt1oWBJ2NaTdaF"
token_url = 'https://login.microsoftonline.com/7b934664-cdcf-4e28-a3ee-1a5bcca0a1b6/oauth2/token'
token_data = {
    'grant_type': 'client_credentials',
    'client_id': app_id,
    'client_secret': client_secret,
    'resource': 'https://graph.microsoft.com',
    'scope': 'https://graph.microsoft.com/People.Read, https://graph.microsoft.com/People.Read.All'
    #'scope': 'https://graph.microsoft.com/.default'
}
"""

def test():
    bottle.response.set_header("Content-Type", "text/plain")
    return "test succeeded"

def get_email_addresses():
   # Old code to get MS Graph token (works but then get permissions errors on next step)
   #token_r = requests.post(token_url, data=token_data)
    #token = token_r.json().get('access_token')
    #me_url = "https://graph.microsoft.com/v1.0/me"
    #headers = {
    #    'Authorization': 'Bearer {}'.format(token),
    #    'Content-Type': 'application/json'
    #}
    
    headers = {
    'Access-Control-Allow-Credentials': 'true',
    'Access-Control-Allow-Origin': '*',
    'Content-Type': 'application/json'
    }
    
    #url = "https://itassets.dbca.wa.gov.au/api/options/?list=dept_user"
    #url = "https://itassets.dbca.wa.gov.au/api/v3/departmentuser/?selectlist="
    url = "https://itassets.dbca.wa.gov.au/api/v3/departmentuser/"
    response_data = requests.get(url, headers=headers, auth=(settings.EMAIL_USER, settings.EMAIL_PWD))
    
    return response_data

#def add_qr_and_link(index, url, qr_filename, text):
def add_qr_and_link(index, url, text):
    #Create QR code and store as png alongside this script
    qr = pyqrcode.create(url)
    buffer = io.BytesIO()
    qr.png(buffer, scale=4)
    
    #Create text and link component of msg
    text_content = '<p>' + text + '<a href="' + url + '">' + url + '</a></p><p><img src="cid:' + index + '"></p>'
    #Create QR image component
    #img_content = MIMEBase('image', 'png', filename=qr_filename)
    img_content = MIMEImage(buffer.getvalue())
    # add required header data:
    #img_content.add_header('Content-Disposition', 'attachment', filename=qr_filename)
    img_content.add_header('X-Attachment-Id', index)
    img_content.add_header('Content-ID', '<' + index + '>')
    # read attachment file content into the MIMEBase object
    img_content.set_payload(buffer.getvalue())
    buffer.close()
    # encode with base64
    encoders.encode_base64(img_content)
    return [text_content, img_content]

def send_email(recipient, msg_text, flights=None, cql_filter=None):
    bottle.response.set_header("Content-Type", "text/plain")
    try:
        smtp_server = 'mail-relay.lan.fyi'
        port = 587
        server = smtplib.SMTP(smtp_server, port)
        sender_email = "no-reply@dbca.wa.gov.au"
        mosaic_layer = ""
        mosaic_qr_filename = ""
        sss_url = 'https://sss.dpaw.wa.gov.au/sss'
        #geoserver_kml_reflector_url = "https://hotspots.dbca.wa.gov.au/geoserver/wms/kml?mode=download&layers="
        geoserver_mosaic_url = "https://hotspots.dbca.wa.gov.au/geoserver/wcs?service=WCS&version=2.0.1&request=GetCoverage&format=image/tiff&CoverageId="
        geoserver_wfs_url = "https://hotspots.dbca.wa.gov.au/geoserver/wfs?format_options=charset%3AUTF-8&outputFormat=SHAPE-ZIP&version=1.0.0&service=WFS&request=GetFeature&typename="
        flight_footprints_layer = "hotspots:hotspot_flight_footprints"
        hotspot_centroids_layer = "hotspots:hotspot_centroids"
        mosaic_layers = []
        if not flights is None:
            flights_list = flights.split(',')
            for flight in flights_list:
                mosaic_layers.append("hotspots:FireFlight_" + flight)
        elif cql_filter is None:
            mosaic_layers = ["hotspots:vrt-test"]
        
        msg = MIMEMultipart()
        msg['To'] = email.utils.formataddr(('Recipient', recipient))
        msg['From'] = email.utils.formataddr(('', 'no-reply@dbca.wa.gov.au'))
        msg['Subject'] = 'Potential hotspots'
        html_text = '<html><body><p>' + msg_text + '</p>'
        hotspots_content = add_qr_and_link('0', geoserver_wfs_url + hotspot_centroids_layer + "&cql_filter=" + cql_filter, 'Download hotspots shp: ')
        footprints_content = add_qr_and_link('1', geoserver_wfs_url + flight_footprints_layer + "&cql_filter=" + cql_filter, 'Download flight footprint(s): ')
        sss_content = add_qr_and_link('2', sss_url, 'Details from SSS: ')
        #mosaic_content = add_qr_and_link('3', geoserver_mosaic_url + mosaic_layer, 'Download mosaic of raw image: ')
        mosaic_content = []
        #html_text += hotspots_content[0] + footprints_content[0] + sss_content[0] + mosaic_content[0] + '</body></html>'
        html_text += hotspots_content[0] + footprints_content[0] + sss_content[0]
        i = 3   # Continues indexing after sss_content
        for mosaic_layer in mosaic_layers:
            mosaic_content.append(add_qr_and_link(str(i), geoserver_mosaic_url + mosaic_layer, 'Download mosaic of raw image for ' + mosaic_layer + ': '))
            i += 1
        for item in mosaic_content:
            html_text += item[0]
        html_text += '</body></html>'
        msg_content = MIMEText(html_text, 'html', 'utf-8')
        msg.attach(msg_content)
        msg.attach(hotspots_content[1])
        msg.attach(footprints_content[1])
        msg.attach(sss_content[1])
        for item in mosaic_content:
            #msg.attach(mosaic_content[1])
            msg.attach(item[1])
        server.sendmail('no-reply@dbca.wa.gov.au', [recipient], msg.as_string())
        server.quit()
        return "email sent"
    except Exception as e:
        return "email failed " + str(e.args) + "\n  " + traceback.format_exc()