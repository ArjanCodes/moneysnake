from client import init_mb_client
from contact import Contact
from httpx import HTTPStatusError

# initialize client
init_mb_client(
    admin_id=375843955958351376, token="-cnqGW5QndzNDbl0uU2ORS6Iy7cDZ_nU4B6MaTZ5350"
)

# read contact by id
contact = Contact.read(434289804752979530)
print(contact)

# update the city for testing
contact.city = "Lelystad"
try:
    contact.save()
    print(contact)
except HTTPStatusError as e:
    print(e.response.json())
