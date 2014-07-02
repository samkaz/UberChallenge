I run my application with Python 2.7.3.  It has the following dependencies:

Flask
enum34
requests
html2text

To run the application, execute "python service.py".  An email service provider can be chosen with the "-s" or "--service" flag.  Currently, only "mandrill" and "mailgun" are valid options to use with the flag.  If an email service provider is not explicitly specified, it will default to Mailgun (set in Configuration.defaultService). To run tests, simply execute "sh test_suite.sh" with all files from the GitHub repo in the same directory.  The service must already be running for the tests to work. All tests passing corresponds to no output from the script.

I chose Python over Javascript as I have used it more recently than Javascript.  I chose the Flask micro-framework simply because it was the only Python framework mentioned in the instructions.

The validation of fields is minimal for several reasons.  I assumed that if automatic requests are being made to this service with a user's information, this information must live in a database so presumably the fields have already been thoroughly validated.  Without knowing more about Uber's practices, I had to keep validation of the body and subject fields lax.  I decided it is also better to be lax with names because it is better to have paying customers with fake names than not.  Finally, after researching it online, I came to the conclusion that truly correct validation of emails is not worthwhile.  Rather, a confirmation email should simply be sent to the customer in order to validate their email.

At the expense of readability, I used meta-programming in two places to allow for extensibility.

First, each valid email service provider is listed in the Services enum and has a corresponding function which prepares and sends a request to that service.  The name of this function must be the value of the service in the enum concatenated with the string "Sender".  For example, Mailgun is listed in the enum as

MAILGUN = "mailgun"

and its corresponding function is mailgunSender.  This leads to extensibility because to support a new email service provider, one need to only add the service to the Services enum and to construct a function with the correct name that performs the actions specific to that service.  Excluding adding it to the Services enum, this is the minimum modification necessary to support a new email service.

Second, each (accepted) field in the request sent to my email service is listed in Validator.fields. Corresponding to each field is a type (represented by the inner-class FieldTypes) and a static method (belonging to Validator) that performs validation on the field.  The name of this method must be the concatenation of the string "isValid" and the value of the type in the FieldTypes enum.  For example, the list Validator.fields contains the pair ("from_name", FieldTypes.FROM_NAME).  "from_name" is simply used to extract the payload from the request.  This payload is then validated with the function whose name is "isValid" + "FromName" = "isValidFromName".  Observe that FieldTypes contains the member

FROM_NAME = "FromName"

Similar to the mechanism for email service providers, this leads to extensibility because to add a new field, one need to only add the field to Validator.fields.  By assigning the new field the right type, validation code will be reused.  If the field requires new validation, one needs to also add a new type to FieldTypes and to compose a function with the correct name that performs the validation specific to that field.  This is almost the bare minimum necessary to support new validation.

If I had more time, I would have liked to extend the modularity afforded by Validator.fields and the inner-class FieldTypes to the functions mailgunSender and mandrillSender.  Currently, both of these functions have nested functions (ie. toMailgunFormat and toMandrillFormat) with hard coded field names and straight line code.

Most importantly, with extra time I would drastically improve my testing.  At present, my test suite is brittle (in that it is tightly coupled with my code) and not very thorough.  Moreover, the test suite itself is written in a very primitive style.  In addition, I would write unit tests with more time.

It may be of note that this is the first time I have written an HTTP service.
