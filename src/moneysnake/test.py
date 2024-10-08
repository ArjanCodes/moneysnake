from client import init_mb_client
from contact import Contact
from httpx import HTTPStatusError

# initialize client
init_mb_client(
    admin_id=375843955958351376, token="-cnqGW5QndzNDbl0uU2ORS6Iy7cDZ_nU4B6MaTZ5350"
)
id = 434317738549184093

# # create a contact
# contact = Contact(company_name="Test Company", firstname="John", lastname="Doedoedoe")
# contact.save()

# print(contact)

# delete a contact
try:
    result = Contact.delete_by_id(id)
    print(f"Contact with id {id} deleted.")
    print(result)
except HTTPStatusError as e:
    print(e)
