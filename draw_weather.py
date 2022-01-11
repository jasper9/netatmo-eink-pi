import sys
import requests
import json
import logging
import time
from datetime import datetime
import digitalio
import busio
import board
from PIL import Image, ImageDraw, ImageFont
from adafruit_epd.epd import Adafruit_EPD

from adafruit_epd.ssd1675 import Adafruit_SSD1675
from adafruit_epd.ssd1680 import Adafruit_SSD1680

spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
ecs = digitalio.DigitalInOut(board.CE0)
dc = digitalio.DigitalInOut(board.D22)
rst = digitalio.DigitalInOut(board.D27)
busy = digitalio.DigitalInOut(board.D17)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

small_font = ImageFont.truetype(
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16
)
medium_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
large_font = ImageFont.truetype(
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24
)
#icon_font = ImageFont.truetype("./meteocons.ttf", 48)

# Initialize the Display
display = Adafruit_SSD1680( 122, 250, spi, cs_pin=ecs, dc_pin=dc, sramcs_pin=None, rst_pin=rst, busy_pin=busy)
display.rotation = 1
#display.fill(Adafruit_EPD.WHITE)
#image = Image.new("RGB", (250, 122), color=WHITE)
#draw = ImageDraw.Draw(image)

logging.captureWarnings(True)

test_api_url = "https://api.netatmo.com/api/getstationsdata?device_id=70%3Aee%3A50%3A84%3A88%3Ada&get_favorites=false"

##
##    function to obtain a new OAuth 2.0 token from the authentication server
##
def get_new_token():

    auth_server_url = "https://api.netatmo.com/oauth2/token"
    client_id = 'xxx'
    client_secret = 'xxx'
    username = 'xxx'
    password = 'xxx'

    token_req_payload = {
        'grant_type': 'password',
        'username': username,
        'password': password,
        'client_id': client_id,
        'client_secret': client_secret
    }

    token_response = requests.post(auth_server_url,
    data=token_req_payload, verify=False, allow_redirects=True)
    print("Status Code: "+str(token_response.status_code))
    if token_response.status_code !=200:
                print("Failed to obtain token from the OAuth 2.0 server", file=sys.stderr)
                sys.exit(1)

    print("Successfuly obtained a new token")
    tokens = json.loads(token_response.text)
    return tokens['access_token']

## 
## 	obtain a token before calling the API for the first time
## 	the token is valid for 15 minutes
##
token = get_new_token()

#while True:
if 1:
    now = datetime.now()
    time_text = now.strftime("%I:%M %p").lstrip("0").replace(" 0", " ")
    print("Time: "+str(time_text))
    ##
    ##   call the API with the token
    ##
    #print("Token: "+str(token))
    api_call_headers = {'Authorization': 'Bearer ' + token}
    api_call_response = requests.get(test_api_url, headers=api_call_headers, verify=False)

    ##
    ##
    print("Status Code: "+str(api_call_response.status_code))

    if	api_call_response.status_code == 401:
        token = get_new_token()
    else:
        
        display.fill(Adafruit_EPD.WHITE)
        image = Image.new("RGB", (250, 122), color=WHITE)
        draw = ImageDraw.Draw(image)

        #print(api_call_response.text)
        j = json.loads(api_call_response.text)
        inside_temp_c = j["body"]["devices"][0]["dashboard_data"]["Temperature"]
        inside_temp_f = (inside_temp_c * 9/5) + 32
        print("Inside: "+str(inside_temp_f))
        outside_temp_c = j["body"]["devices"][0]["modules"][0]["dashboard_data"]["Temperature"]
        outside_temp_f = (outside_temp_c * 9/5) + 32
        print("Outside: "+str(outside_temp_f))
        print("----------------------------------")
        draw.text((5, 5), "Weather Station", font=medium_font, fill=BLACK)
        
        # (font_width, font_height) = medium_font.getsize(time_text)
        # draw.text(
        #     (5, font_height * 2 - 5), time_text,
        #     font=medium_font,
        #     fill=BLACK,
        # )


        draw.text(
            (5, 55), "Inside: "+str(inside_temp_f)+" °F",
            font=large_font,
            fill=BLACK,
        )

        draw.text(
            (5, 95), "Outside: "+str(outside_temp_f)+" °F",
            font=large_font,
            fill=BLACK,
        )


        display.image(image)
        display.display()

    #time.sleep(60)
