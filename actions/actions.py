from typing import Dict, Text, Any, List, Union

from rasa_sdk import Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormValidationAction

import ssl
from urllib import request, parse
import json

class ValidateRestaurantForm(FormValidationAction):
    """Example of a form validation action."""

    def name(self) -> Text:
        return "validate_restaurant_form"

    @staticmethod
    def cuisine_db() -> List[Text]:
        """Database of supported cuisines."""

        return [
            "caribbean",
            "chinese",
            "french",
            "greek",
            "indian",
            "italian",
            "mexican",
        ]

    @staticmethod
    def is_int(string: Text) -> bool:
        """Check if a string is an integer."""

        try:
            int(string)
            return True
        except ValueError:
            return False

    def validate_cuisine(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate cuisine value."""
        print(value)

        if value.lower() in self.cuisine_db():
            # validation succeeded, set the value of the "cuisine" slot to value
            return {"cuisine": value}
        else:
            dispatcher.utter_message(response="utter_wrong_cuisine")
            # validation failed, set this slot to None, meaning the
            # user will be asked for the slot again
            return {"cuisine": None}

    def validate_num_people(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate num_people value."""

        if self.is_int(value) and int(value) > 0:
            return {"num_people": value}
        else:
            dispatcher.utter_message(response="utter_wrong_num_people")
            # validation failed, set slot to None
            return {"num_people": None}

    def validate_outdoor_seating(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate outdoor_seating value."""

        if isinstance(value, str):
            if "out" in value:
                # convert "out..." to True
                return {"outdoor_seating": True}
            elif "in" in value:
                # convert "in..." to False
                return {"outdoor_seating": False}
            else:
                dispatcher.utter_message(response="utter_wrong_outdoor_seating")
                # validation failed, set slot to None
                return {"outdoor_seating": None}

        else:
            # affirm/deny was picked up as True/False by the from_intent mapping
            return {"outdoor_seating": value}


class ValidateWeatherForm(FormValidationAction):
    """Example of a form validation action."""

    def name(self) -> Text:
        return "validate_weather_form"

    @staticmethod
    def getLocation(plocation):
        location = plocation if len(plocation)>0 else 'ip' # 默认根据当前IP查询，所查询的位置，可以使用城市拼音、v3 ID、经纬度等
        return location

    @staticmethod
    def fetchWeather(location):
        params = parse.urlencode({
            'key': 'SiJLwLBuHlDyGpYeA',  # API key
            'location': location,
            'language': 'zh-Hans', # 查询结果的返回语言
            'unit': 'c'  # 单位
        })
        ssl._create_default_https_context = ssl._create_unverified_context
        gcontext = ssl._create_unverified_context()
        req = request.Request('{api}?{params}'.format(api='https://api.seniverse.com/v3/weather/now.json', params=params))# API URL，可替换为其他 URL
        response = request.urlopen(req, context=gcontext).read().decode('UTF-8')
        print(response)
        data = json.loads(response)
        city = data["results"][0]["location"]["name"]
        weather = data["results"][0]["now"]["text"]
        temperature = data["results"][0]["now"]["temperature"]
        return city + "今天" + weather + " 温度 " + temperature + "摄氏度"
    def validate_city(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate cuisine value."""
        location = self.getLocation(value)
        try:
            print(location)
            weather = self.fetchWeather(location)
            dispatcher.utter_message(text=weather)
        except:
            dispatcher.utter_message(text="未查询到"+value+"天气")
        return {"city": None}
    
