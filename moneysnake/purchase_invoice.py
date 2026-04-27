from .document import Document, DocumentDetailsAttribute


class PurchaseInvoiceDetailsAttribute(DocumentDetailsAttribute):
    """Details attribute (line item) for a purchase invoice."""


class PurchaseInvoice(Document):
    """Represents a purchase invoice in Moneybird."""

    _resource = "purchase_invoice"
