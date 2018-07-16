import json
import os
from collections import namedtuple
from datetime import datetime
from typing import Union, Tuple

import requests


class Utils:
    statusMessageData = None
    statusMessageCustomData = {}

    @staticmethod
    def absolute_path(relative: str) -> str:
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative)

    @staticmethod
    def fetch_status_messages():
        # Try from the API to get latest (and save locally)
        try:
            Utils.log("Utils.fetch_status_messages", "Attempting to load from API...")
            resp = requests.get(url="https://cdn.unreal-designs.co.uk/cont/statusMsg/", timeout=5)
            data = resp.json()
            if data:
                Utils.statusMessageData = data
                with open('assets/statusMsg.json', 'w') as file:
                    json.dump(data, file, sort_keys=True, indent=4)
                Utils.log("Utils.fetch_status_messages", "Loaded from API")
        except:
            Utils.log("Utils.fetch_status_messages", "Failed to load from API...")
            pass

        # If API failed, use latest local copy
        if not Utils.statusMessageData:
            if os.path.isfile('assets/statusMsg.json'):
                with open('assets/statusMsg.json') as file:
                    Utils.statusMessageData = json.load(file)
                    Utils.log("Utils.fetch_status_messages", "Loaded from local file")

        # Inject our custom data
        for key, data in Utils.statusMessageCustomData.items():
            # Create blank data if it doesn't already exist
            if key not in Utils.statusMessageData:
                Utils.statusMessageData[key] = {'message': '', 'description': ''}
            # Loop over the properties provided
            for item, value in data.items():
                # If valid property, update
                if item in Utils.statusMessageData[key].keys():
                    Utils.statusMessageData[key][item] = value

    @staticmethod
    def status_message(code: int) -> Union[None, Tuple[int, str, str, str]]:
        # Check if we have data
        if not Utils.statusMessageData:
            # Attempt to load data
            Utils.fetch_status_messages()
            # If we still don't have data, return
            if not Utils.statusMessageData:
                return None

        # Check if the given code is in our data
        if str(code) not in Utils.statusMessageData.keys():
            return None

        # Return the data
        return code, Utils.statusMessageData[str(code)]['message'], Utils.statusMessageData[str(code)]['description'], \
               "{}: {}".format(code, Utils.statusMessageData[str(code)]['message'])

    @staticmethod
    def log(type: str, *args, **kwargs):
        now = "[{0.hour:02d}:{0.minute:02d}:{0.second:02d}]".format(datetime.now())
        print("{} [{}]".format(now, type), *args, **kwargs)
