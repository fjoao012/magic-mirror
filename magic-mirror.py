# magic-mirror.py
# Modified by Ferreira Joao Alexandre (TT-CH/ERS)

from tkinter import * # to show a native graphical interface (GUI)
import locale
import threading
import time
import requests # to perform HTTP requests
import json # to parse JSON responses from HTTP requests
import traceback
import feedparser # to parse RSS feeds

from PIL import Image, ImageTk # to display images
from contextlib import contextmanager

LOCALE_LOCK = threading.Lock()

# TODO feel free to change here some of the parameters to understand how this app works
ui_locale = 'pt_PT' # e.g. 'fr_FR' fro French, '' as default
time_format = 24 # 12 or 24
date_format = "%b %d, %Y" # check python doc for strftime() for options
news_country_code = 'pt-PT' # look at the google news URL some lines below to understand what should you put here
weather_api_token = '2c212b3a5c7bfed52b91b0f5f1d4c8cb' # create account at https://darksky.net/dev/
weather_lang = 'pt' # see https://darksky.net/dev/docs/forecast for full list of language parameters values
weather_unit = 'si' # see https://darksky.net/dev/docs/forecast for full list of unit parameters values
latitude = '40.6421543' # Set this if IP location lookup does not work for you (must be a string)
longitude = '-8.6495847' # Set this if IP location lookup does not work for you (must be a string)
xlarge_text_size = 94
large_text_size = 48
medium_text_size = 28
small_text_size = 18

@contextmanager
def setlocale(name): #thread proof function to work with locale
    with LOCALE_LOCK:
        saved = locale.setlocale(locale.LC_ALL)
        try:
            yield locale.setlocale(locale.LC_ALL, name)
        finally:
            locale.setlocale(locale.LC_ALL, saved)

# maps open weather icons to
# icon reading is not impacted by the 'lang' parameter
icon_lookup = {
    'clear-day': "assets/Sun.png",  # clear sky day
    'wind': "assets/Wind.png",   #wind
    'cloudy': "assets/Cloud.png",  # cloudy day
    'partly-cloudy-day': "assets/PartlySunny.png",  # partly cloudy day
    'rain': "assets/Rain.png",  # rain day
    'snow': "assets/Snow.png",  # snow day
    'snow-thin': "assets/Snow.png",  # sleet day
    'fog': "assets/Haze.png",  # fog day
    'clear-night': "assets/Moon.png",  # clear sky night
    'partly-cloudy-night': "assets/PartlyMoon.png",  # scattered clouds night
    'thunderstorm': "assets/Storm.png",  # thunderstorm
    'tornado': "assests/Tornado.png",    # tornado
    'hail': "assests/Hail.png"  # hail
}

"""
  * This class defines the information that the weather widget will show 
"""
class Weather(Frame):
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, bg='black')
        self.temperature = ''
        self.forecast = ''
        self.location = ''
        self.currently = ''
        self.icon = ''
        self.degreeFrm = Frame(self, bg="black")
        self.degreeFrm.pack(side=TOP, anchor=W)
        self.temperatureLbl = Label(self.degreeFrm, font=('Helvetica', xlarge_text_size), fg="white", bg="black")
        self.temperatureLbl.pack(side=LEFT, anchor=N)
        self.iconLbl = Label(self.degreeFrm, bg="black")
        self.iconLbl.pack(side=LEFT, anchor=N, padx=20)
        self.currentlyLbl = Label(self, font=('Helvetica', medium_text_size), fg="white", bg="black")
        self.currentlyLbl.pack(side=TOP, anchor=W)
        self.forecastLbl = Label(self, font=('Helvetica', small_text_size), fg="white", bg="black")
        self.forecastLbl.pack(side=TOP, anchor=W)
        self.locationLbl = Label(self, font=('Helvetica', small_text_size), fg="white", bg="black")
        self.locationLbl.pack(side=TOP, anchor=W)
        self.get_weather()

    # get the machine's IP address (where this script is running)
    def get_ip(self):
        try:
            ip_url = "http://jsonip.com/"
            req = requests.get(ip_url)
            ip_json = json.loads(req.text)
            return ip_json['ip']
        except Exception as e:
            traceback.print_exc()
            return "Error: %s. Cannot get ip." % e

    # get the weather from DarkSky (you can change this to another provider like IPMA or AccuWeather if you prefer)
    def get_weather(self):
        try:
            # in case you didn't define any coordinates above, this will try to get your approximate
            # coordinates, based on your IP address
            if latitude is None and longitude is None:
                # get location
                location_req_url = "http://freegeoip.net/json/%s" % self.get_ip()
                r = requests.get(location_req_url)
                location_obj = json.loads(r.text)

                lat = location_obj['latitude']
                lon = location_obj['longitude']

                location2 = "%s, %s" % (location_obj['city'], location_obj['region_code'])

                # the effective call to the weather provider
                weather_req_url = "https://api.darksky.net/forecast/%s/%s,%s?lang=%s&units=%s" % (weather_api_token, lat,lon,weather_lang,weather_unit)
            else:
                location2 = ""
                # get weather
                weather_req_url = "https://api.darksky.net/forecast/%s/%s,%s?lang=%s&units=%s" % (weather_api_token, latitude, longitude, weather_lang, weather_unit)

            r = requests.get(weather_req_url)
            weather_obj = json.loads(r.text)

            degree_sign= u'\N{DEGREE SIGN}'
            temperature2 = "%s%s" % (str(int(weather_obj['currently']['temperature'])), degree_sign)
            currently2 = weather_obj['currently']['summary']
            forecast2 = weather_obj["hourly"]["summary"]

            icon_id = weather_obj['currently']['icon']
            icon2 = None

            # get the icon to display
            if icon_id in icon_lookup:
                icon2 = icon_lookup[icon_id]

            # adjust the icon to show it in the screen
            if icon2 is not None:
                if self.icon != icon2:
                    self.icon = icon2
                    image = Image.open(icon2)
                    image = image.resize((100, 100), Image.ANTIALIAS)
                    image = image.convert('RGB')
                    photo = ImageTk.PhotoImage(image)

                    self.iconLbl.config(image=photo)
                    self.iconLbl.image = photo
            else:
                # remove image
                self.iconLbl.config(image='')

            # store the weather information in the internal structure
            if self.currently != currently2:
                self.currently = currently2
                self.currentlyLbl.config(text=currently2)
            if self.forecast != forecast2:
                self.forecast = forecast2
                self.forecastLbl.config(text=forecast2)
            if self.temperature != temperature2:
                self.temperature = temperature2
                self.temperatureLbl.config(text=temperature2)
            if self.location != location2:
                if location2 == ", ":
                    self.location = "Cannot Pinpoint Location"
                    self.locationLbl.config(text="Cannot Pinpoint Location")
                else:
                    self.location = location2
                    self.locationLbl.config(text=location2)
        except Exception as e:
            traceback.print_exc()
            print("Error: %s. Cannot get weather." % e)

        self.after(600000, self.get_weather)

    @staticmethod
    def convert_kelvin_to_fahrenheit(kelvin_temp):
        return 1.8 * (kelvin_temp - 273) + 32

"""
  * This class defines the information that the news widget will show 
"""
class News(Frame):
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.config(bg='black')
        self.title = 'News' # 'News' is more internationally generic
        self.newsLbl = Label(self, text=self.title, font=('Helvetica', medium_text_size), fg="white", bg="black")
        self.newsLbl.pack(side=TOP, anchor=W)
        self.headlinesContainer = Frame(self, bg="black")
        self.headlinesContainer.pack(side=TOP)
        self.get_headlines()

    # get the news' headlines for the country you've defined at the top of this Python script
    def get_headlines(self):
        try:
            # remove all children
            for widget in self.headlinesContainer.winfo_children():
                widget.destroy()
            if news_country_code == None:
                headlines_url = "https://news.google.com/rss?hl=ko" # why not Korea's news? :)
            else:
                headlines_url = "https://news.google.com/rss?hl=%s" % news_country_code

            feed = feedparser.parse(headlines_url)

            for post in feed.entries[0:5]:
                headline = NewsHeadline(self.headlinesContainer, post.title)
                headline.pack(side=TOP, anchor=W)
        except Exception as e:
            traceback.print_exc()
            print("Error: %s. Cannot get news." % e)

        self.after(600000, self.get_headlines)

"""
  * This is a class that defines objects that will hold the headlines of the 
  * news that were retrieved.
"""
class NewsHeadline(Frame):
    def __init__(self, parent, event_name=""):
        Frame.__init__(self, parent, bg='black')

        image = Image.open("assets/Newspaper.png")
        image = image.resize((25, 25), Image.ANTIALIAS)
        image = image.convert('RGB')
        photo = ImageTk.PhotoImage(image)

        self.iconLbl = Label(self, bg='black', image=photo)
        self.iconLbl.image = photo
        self.iconLbl.pack(side=LEFT, anchor=N)

        # the headlines are limited in size to 92 chars, but you can remove that limitation
        MAX_SIZE = 92
        if len(event_name) > MAX_SIZE:
            self.eventName = event_name[:MAX_SIZE] + '(...)' 
        else:
            self.eventName = event_name
        self.eventNameLbl = Label(self, text=self.eventName, font=('Helvetica', small_text_size), fg="white", bg="black")
        self.eventNameLbl.pack(side=LEFT, anchor=N)

"""
  * TODO This is the perfect spot to create your widget!
  * One possible way to do that is to create a class, define everything you want there 
  * and then evoke one object at FullScreenWindow.init()
"""




"""
  * The class that defines the GUI (i.e., graphical user interface)
  * Try to tinker with this to change the appearance of the window
"""
class FullscreenWindow:

    def __init__(self):
        self.tk = Tk()
        self.tk.configure(background='black')
        self.topFrame = Frame(self.tk, background = 'black')
        self.bottomFrame = Frame(self.tk, background = 'black')
        self.topFrame.pack(side = TOP, fill=BOTH, expand = YES)
        self.bottomFrame.pack(side = BOTTOM, fill=BOTH, expand = YES)
        self.state = False
        # While this app is running, press <Enter> to put the app in full screen
        self.tk.bind("<Return>", self.toggle_fullscreen)
        # While this app is running, press <Esc> to remove the app from full screen
        self.tk.bind("<Escape>", self.end_fullscreen)
        
        # create an object 'weather' inside the GUI, and set its position
        self.weather = Weather(self.topFrame)
        self.weather.pack(side=LEFT, anchor=N, padx=100, pady=60)
        
        # create an object 'news' inside the GUI and set its position
        self.news = News(self.bottomFrame)
        self.news.pack(side=LEFT, anchor=S, padx=100, pady=60)

        # TODO create more objects here and assign your widget
        #  Examples of widgets you can create:
        # self.calendar = Calendar ...
        # self.clock = Clock ...
        # self.radio = LastMusicThatPlayedOnRadioComercial
        # self.word = WordOfTheDay
        # self.yourWidget = MagicChimpDoingStuff

    def toggle_fullscreen(self, event=None):
        self.state = not self.state  # Just toggling the boolean
        self.tk.attributes("-fullscreen", self.state)
        return "break"

    def end_fullscreen(self, event=None):
        self.state = False
        self.tk.attributes("-fullscreen", False)
        return "break"

if __name__ == '__main__':
    w = FullscreenWindow()
    w.tk.mainloop()
