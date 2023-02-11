import os
from mixpanel import Mixpanel

class MixpanelTestClient:
    def __init__(self, token) -> None:
        return

    def track(self, user_id, event, *args, **kwargs) -> None:
        return None

# initial match distance
environment = os.getenv('ENVIRONMENT')

if environment == 'production':
    MixpanelClient = Mixpanel(os.environ["MIXPANEL_TOKEN"])
else:
    MixpanelClient = MixpanelTestClient(os.environ["MIXPANEL_TOKEN"])
    