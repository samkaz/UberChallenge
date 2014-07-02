from flask import Flask, request
from werkzeug.exceptions import BadRequest
from enum import Enum, unique
import argparse
import requests
import json
import html2text

app = Flask(__name__)

@unique
class Services(Enum):
    """ This enum contains the supported email service providers.
    The function which performs the actions specific to a provider, including
    sending the actual request to the provider, must have a name that is the
    concatenation of the value of the service's enum variable and the string
    "Sender".  For example, the function which sends a POST request to Mailgun
    is called mailgunSender.  In this way, the values of the enum are not
    arbitrary.
    """
    MAILGUN = "mailgun"
    MANDRILL = "mandrill"
    
class Configuration:
    """ This class contains configuration parameters for the whole program, such
    as the name of flags and the default email service provider, in addition to
    fixed parameters required by the email service providers, such as the URL
    where the service exists and authentication parameters.
    """
    shortServiceFlag = "-s"
    longServiceFlag = "--service"
    defaultService = "mailgun"
    serviceSpecificConfig = { Services.MAILGUN :
                              {"username":"api",
                               "password":"key",
                               "url":
                               "https://api.mailgun.net/v2/sandboxcb081ce4ab0a4647b7e00a55a2240301.mailgun.org/messages"},
                              Services.MANDRILL :
                              {"url":"https://mandrillapp.com/api/1.0/messages/send.json",
                               "key":"password",
                               "headers":{'Content-type':'application/json',
                                          'User-Agent':'Mandrill-Curl/1.0'}}}

    def __init__(self):
        self.parser = argparse.ArgumentParser()
        
        self.parser.add_argument(Configuration.shortServiceFlag,
                                 Configuration.longServiceFlag,
                                 default = Configuration.defaultService)
        service = self.parser.parse_args().service
        
        serviceExists = False
        for s in Services:
            if s.value == service:
                self.service = s
                serviceExists = True

        if not serviceExists:
            msg = "Service not supported. The following services are supported:"
            for s in Services:
                msg =  msg + "\n" + s.value
            self.parser.error(msg)

class Validator:
    """ This class validates the fields in a request.  The fields member
    variable has a list of pairs wherein the first element of each pair
    is a name of an accepted field. The second element of each pair is
    the type of the first element.  These types can be found in the FieldTypes
    nested class.  A field type is used to determine which validation function
    to call on a field.  In this way, the values assigned to each type in the
    enum are not arbitrary.
    """
    @unique
    class FieldTypes(Enum):
        TO_EMAIL = "ToEmail"
        FROM_EMAIL = "FromEmail"
        TO_NAME = "ToName"
        FROM_NAME = "FromName"
        SUBJECT = "Subject"
        BODY = "Body"

    fields = [("to", FieldTypes.TO_EMAIL),
              ("to_name", FieldTypes.TO_NAME),
              ("from", FieldTypes.FROM_EMAIL),
              ("from_name", FieldTypes.FROM_NAME),
              ("subject", FieldTypes.SUBJECT),
              ("body", FieldTypes.BODY)]

    minBodyLength = 1
    minSubjectLength = 1
    minNameLength = 2
    minEmailLength = 3

    @staticmethod
    def isValidToEmail(email):
        if email is None:
            return False, "To Email is a required field."
        return Validator.isValidEmail(email)

    @staticmethod
    def isValidFromEmail(email):
        if email is None:
            return False, "From Email is a required field."
        return Validator.isValidEmail(email)

    @staticmethod
    def isValidEmail(email):
        if len(email) < Validator.minEmailLength:
            return False, "Email length is too short."
        if not "@" in email:
            return False, "Email does not contain @ symbol."
        return True, "Valid Email."
        
    @staticmethod
    def isValidToName(name):
        if name is None:
            return False, "To Name is a required field."
        return Validator.isValidName(name)

    @staticmethod
    def isValidFromName(name):
        if name is None:
            return False, "From Name is a required field."
        return Validator.isValidName(name)

    @staticmethod
    def isValidName(name):
        if len(name) < Validator.minNameLength:
            return False, "Name length is too short."
        return True, "Valid name."

    @staticmethod
    def isValidSubject(subject):
        if subject is None:
            return False, "Subject is a required field."
        if len(subject) < Validator.minSubjectLength:
            return False, "Subject length is too short."
        return True, "Valid subject."

    @staticmethod
    def isValidBody(body):
        if body is None:
            return False, "Body is a required field."
        if len(body) < Validator.minBodyLength:
            return False, "Body length is too short."
        return True, "Valid body."

    @staticmethod
    def isValid(request):
        for field, fieldType in Validator.fields:
            typeVal = fieldType.value
            validator = getattr(Validator, "isValid" + typeVal,
                                lambda _: (False,
                                           typeVal + " validator not found."))
            valid, err = validator(request.get(field))
            if not valid:
                return False, err
        return True, "Valid request."

def htmlToPlainText(html):
    """This function converts HTML to plain text"""
    try:
        txt = html2text.HTML2Text().handle(html)
        return True, txt
    except:
        return False, "Failed to convert HTML body to plain text."

def mailgunSender(req):
    """This function transforms a request to the format dictated by the
    Mailgun API and places a call (via POST) to Mailgun.
    """
    def toMailgunFormat():
        rtn = {}
        rtn["to"] = req["to_name"] + " <" + req["to"] + ">"
        rtn["from"] = req["from_name"] + " <" + req["from"] + ">"
        rtn["text"] = req["body"]
        rtn["subject"] = req["subject"]
    
        return rtn

    settings = Configuration.serviceSpecificConfig[Services.MAILGUN]
    return requests.post(settings["url"],
                         auth = (settings["username"], settings["password"]),
                         data = toMailgunFormat())

def mandrillSender(req):
    """This function transforms a request to the format dictated by the
    Mandrill API and places a call (via POST) to Mandrill.
    """
    def toMandrillFormat():
        rtn = {}
        rtn["from_email"] = req["from"]
        rtn["from_name"] = req["from_name"]
        rtn["to"] = [{"email":req["to"], "name":req["to_name"]}]
        rtn["text"] = req["body"]
        rtn["subject"] = req["subject"]

        return rtn
    
    settings = Configuration.serviceSpecificConfig[Services.MANDRILL]
    return requests.post(settings["url"],
                         data = json.dumps({"key":settings["key"],
                                            "message":toMandrillFormat()}),
                         headers = settings["headers"])

@app.route('/email', methods=['POST'])
def emailService():
    """ This function handles POST requests to this service's /email endpoint.
    First, the JSON data in the request is validated.  Second, the HTML body
    in the request is transformed to plain text.  Lastly, a request is made to
    an email service provider.
    """
    try:
        req = request.get_json()
    except BadRequest:
        return "Malformed JSON."

    if req is None:
        return "Failed to load JSON.  Check that Content-Type is set correctly."

    valid, err = Validator.isValid(req)
    if not valid:
        return err

    # req is guaranteed to have the key "body" as this was checked in the
    # validation (ie. Validator.isValid(req)).  We check to be sure.
    if req.get("body") is None:
        return "Panic: Body field went missing!"
    success, payload = htmlToPlainText(req["body"])
    if success:
        req["body"] = payload        
    else:
        return "Failed to convert HTML body to plain text:\n" + payload

    sender = globals().get(config.service.value + "Sender")
    if sender is None:
        return "Panic: Couldn't find email service!"

    excp = requests.exceptions
    try:
        r = sender(req)
    except KeyError:
        return "Panic: Required field does not exist after successful validation."
    except excp.ConnectionError:
        return "Could not connect to " + config.service.value + "."
    except excp.HTTPError:
        return "An HTTPError occured using " + config.service.value + "."
    except excp.Timeout:
        return "Connection timed out using " + config.service.value + "."
    except excp.TooManyRedirects:
        return "Too many redirects occured using " + config.service.value + "."
    except excp.URLRequired:
        return "Invalid URL using " + config.service.value + "."
    except excp.RequestException:
        return "RequestException occured using " + config.service.value + "."

    return "Request successfully serviced."

if __name__ == '__main__':
    global config
    config = Configuration()
    #todo remove debug
    app.run(debug=True)
