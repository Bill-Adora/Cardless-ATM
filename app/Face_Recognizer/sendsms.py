import random
import os
# Import the helper gateway class
from AfricasTalkingGateway import AfricasTalkingGateway, AfricasTalkingGatewayException

def generatePass(phoneNo):
#def generatePass(phoneNo):
    genCode = random.randint(100000, 999999)
    # Specify your login credentials
    username = os.environ['AT_USERNAME']
    apikey   = os.environ['AT_APIKEY']
    # Specify the receiving number
    to = phoneNo
    # Message to be sent
    message = "Your verification code is {}, valid for 30 minutes.".format(genCode)
    # Create a new instance of our awesome gateway class
    gateway = AfricasTalkingGateway(username, apikey)

    try:
        results = gateway.sendMessage(to, message)

        for recipient in results:
            # status is either "Success" or "error message"
            print('number = {}; status = {}; messageId = {}; cost = {}'.format(recipient['number'],
                                                                    recipient['status'],
                                                                    recipient['messageId'],
                                                                    recipient['cost']))
    except AfricasTalkingGatewayException as e:
        print ('Encountered an error while sending: {}').format(str(e))
    
    return genCode
