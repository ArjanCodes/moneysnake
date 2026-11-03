# moneysnake
![Authors](https://kajabi-storefronts-production.kajabi-cdn.com/kajabi-storefronts-production/file-uploads/themes/2149113237/settings_images/4adb13d-824c-454-a5c-72b2c6f06e1_Arjan_Codes_-_FInal_Files.png)

Python SDK around the Moneybird accounting platform.

## Description

SDK for the Moneybird accounting platform to connect applications to Moneybird's API. With this SDK, you can easily create invoices, manage contacts, and retrieve financial data. It takes care of authentication and API requests, making it simple to automate tasks and handle accounting workflows in Moneybird from within a Python application.

## Installation

This library is uploaded to PyPi, to install simply run the following commands:

```bash
pip install moneysnake
```

## Errors

Every error the library raises is a `MoneybirdError`. Each error is also either transient or permanent. A transient error can succeed when you repeat the request later. A permanent error fails again until you change the request.

- `MoneybirdError`
  - `MoneybirdTransientError`
    - `MoneybirdRateLimitError` (429)
    - `MoneybirdServerError` (5xx)
    - `MoneybirdConnectionError` (timeout or no connection, no response)
  - `MoneybirdPermanentError`
    - `MoneybirdBadRequestError` (400)
    - `MoneybirdAuthenticationError` (401)
    - `MoneybirdPaymentRequiredError` (402)
    - `MoneybirdForbiddenError` (403)
    - `MoneybirdNotFoundError` (404)
    - `MoneybirdValidationError` (422)
    - `MoneybirdClientError` (other 4xx)
  - `MoneybirdAPIError`, the base of every error that has an HTTP response. All classes above except `MoneybirdConnectionError` are also a `MoneybirdAPIError`.

The library retries rate limits, and it retries server errors and connection errors only for requests that are safe to repeat, such as GET and DELETE. It raises the error when the retries are used up.

A `MoneybirdAPIError` keeps the raw body in `response_body` and the parsed JSON object in `body`. `message` gives the error message, `field_errors` gives the messages per field, `field_error_codes` gives the error codes per field, and `symbolic` gives the symbolic error codes when Moneybird sends them. `retry_after` holds the raw Retry-After header, or `None` when there is none.

```python
from moneysnake import Contact, MoneybirdValidationError

try:
    Contact(company_name="Acme", tax_number="NL123").save()
except MoneybirdValidationError as error:
    for field, messages in error.field_errors.items():
        print(field, messages)
```

# Contributing
If you want to contribute to this project, please use the following steps:

1. Fork the project.
2. Create a new branch (git checkout -b feature/awesome-feature).
3. Commit your changes (git commit -m 'Add some feature').
4. Push to the branch (git push origin feature/awesome-feature).
5. Open a pull request.

# License
This project is licensed under the MIT License.
