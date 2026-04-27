from .document import Document, DocumentDetailsAttribute


class ReceiptDetailsAttribute(DocumentDetailsAttribute):
    """Details attribute (line item) for a receipt."""


class Receipt(Document):
    """Represents a receipt in Moneybird."""

    _resource = "receipt"
