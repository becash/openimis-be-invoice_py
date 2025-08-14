from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from core.models import HistoryBusinessModel, HistoryModel, UUIDModel, ObjectMutation, MutationLog
from core.fields import DateField
from datetime import date
from invoice.apps import InvoiceConfig
from django.utils.translation import gettext as _
# Create your models here.
from invoice.mixins import GenericInvoiceQuerysetMixin, GenericInvoiceManager


def get_default_currency():
    return InvoiceConfig.default_currency_code


class GenericInvoice(GenericInvoiceQuerysetMixin, HistoryBusinessModel):
    class Status(models.IntegerChoices):
        DRAFT = 0, _('draft')
        VALIDATED = 1, _('validated')
        PAID = 2, _('paid')
        CANCELLED = 3, _('cancelled')
        DELETED = 4, _('deleted')
        SUSPENDED = 5, _('suspended')
        UNPAID = 6, _('unpaid')
        RECONCILIATED = 7, _('reconciliated')

    thirdparty_type = models.ForeignKey(ContentType, models.DO_NOTHING,
                                          db_column='ThirdpartyType', blank=True, null=True, unique=False)
    thirdparty_id = models.CharField(db_column='ThirdpartyId', max_length=255, blank=True, null=True)  # object is referenced by uuid
    thirdparty = GenericForeignKey('thirdparty_type', 'thirdparty_id')

    code_tp = models.CharField(db_column='CodeTp', max_length=255, blank=True, null=True)
    code = models.CharField(db_column='Code', max_length=255, null=False)
    code_ext = models.CharField(db_column='CodeExt', max_length=255, blank=True, null=True)

    date_due = DateField(db_column='DateDue', blank=True, null=True)

    date_payed = DateField(db_column='DatePayed', blank=True, null=True)

    amount_discount = models.DecimalField(
        db_column='AmountDiscount', max_digits=18, decimal_places=2,  null=True, default=0.0)
    amount_net = models.DecimalField(
        db_column='AmountNet', max_digits=18, decimal_places=2, default=0.0)
    amount_total = models.DecimalField(
        db_column='AmountTotal', max_digits=18, decimal_places=2, default=0.0)

    tax_analysis = models.JSONField(db_column='TaxAnalysis', blank=True, null=True)

    status = models.SmallIntegerField(
        db_column='Status', null=False, choices=Status.choices, default=Status.DRAFT)

    currency_tp_code = models.CharField(
        db_column='CurrencyTpCode', null=False, max_length=255, default=get_default_currency)
    currency_code = models.CharField(
        db_column='CurrencyCode', null=False, max_length=255, default=get_default_currency)

    note = models.TextField(db_column='Note', blank=True, null=True)
    terms = models.TextField(db_column='Terms', blank=True, null=True)

    payment_reference = models.CharField(db_column='PaymentReference', max_length=255, blank=True, null=True)

    objects = GenericInvoiceManager()

    class Meta:
        abstract = True


class GenericInvoiceLineItem(GenericInvoiceQuerysetMixin, HistoryBusinessModel):
    code = models.CharField(db_column='Code', max_length=255, null=False)

    description = models.TextField(db_column='Description', blank=True, null=True)
    details = models.JSONField(db_column='Details', blank=True, null=True)

    ledger_account = models.CharField(db_column='LedgerAccount', max_length=255, blank=True, null=True)

    quantity = models.IntegerField(db_column='Quantity', default=0.0)
    unit_price = models.DecimalField(db_column='UnitPrice', max_digits=18, decimal_places=2, default=0.0)

    discount = models.DecimalField(db_column='Discount', max_digits=18, decimal_places=2, default=0.0)

    deduction = models.DecimalField(db_column='Deduction', max_digits=18, decimal_places=2, default=0.0)

    tax_rate = models.UUIDField(db_column="CalculationUUID", blank=True, null=True)
    tax_analysis = models.JSONField(db_column='TaxAnalysis',  blank=True, null=True)

    amount_total = models.DecimalField(db_column='AmountTotal', max_digits=18, decimal_places=2, default=0.0)
    amount_net = models.DecimalField(db_column='AmountNet', max_digits=18, decimal_places=2, default=0.0)

    objects = GenericInvoiceManager()

    class Meta:
        abstract = True


class GenericInvoicePayment(GenericInvoiceQuerysetMixin, HistoryModel):
    class PaymentStatus(models.IntegerChoices):
        REJECTED = 0, _('rejected')
        ACCEPTED = 1, _('accepted')
        REFUNDED = 2, _('refunded')
        CANCELLED = 3, _('cancelled')

    code_tp = models.CharField(db_column='CodeTp', max_length=255, blank=True, null=True)
    code_ext = models.CharField(db_column='CodeExt', max_length=255, blank=True, null=True)
    code_receipt = models.CharField(db_column='CodeReceipt', max_length=255, blank=True, null=True)

    label = models.CharField(db_column='Label', max_length=255,  blank=True, null=True)

    status = models.SmallIntegerField(db_column='Status', null=False, choices=PaymentStatus.choices)

    amount_payed = models.DecimalField(db_column='AmountPayed', max_digits=18, decimal_places=2,  blank=True, null=True)
    fees = models.DecimalField(db_column='Fees', max_digits=18, decimal_places=2,  blank=True, null=True)
    amount_received = models.DecimalField(db_column='AmountReceived', max_digits=18, decimal_places=2,  blank=True, null=True)

    date_payment = DateField(db_column='DatePayment',  blank=True, null=True)

    payment_origin = models.CharField(db_column='PaymentOrigin', max_length=255,  blank=True, null=True)

    objects = GenericInvoiceManager()

    class Meta:
        abstract = True


class GenericInvoiceEvent(GenericInvoiceQuerysetMixin, HistoryModel):
    class EventType(models.IntegerChoices):
        MESSAGE = 0, _('message')
        STATUS = 1, _('status')
        WARNING = 2, _('warning')
        PAYMENT = 3, _('payment')
        PAYMENT_ERROR = 4, _('payment_error')

    message = models.CharField(db_column='Message', max_length=500,  blank=True, null=True)
    event_type = models.SmallIntegerField(
        db_column='Status', null=False, choices=EventType.choices, default=EventType.MESSAGE)

    objects = GenericInvoiceManager()

    class Meta:
        abstract = True


class Invoice(GenericInvoice):
    subject_type = models.ForeignKey(ContentType, models.DO_NOTHING,
                                        db_column='SubjectType',  blank=True, null=True, related_name='subject_type', unique=False)
    subject_id = models.CharField(db_column='SubjectId', max_length=255,  blank=True, null=True)  # object is referenced by uuid
    subject = GenericForeignKey('subject_type', 'subject_id')

    date_invoice = DateField(db_column='DateInvoice', default=date.today,  blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'tblInvoice'


class InvoiceLineItem(GenericInvoiceLineItem):
    line_type = models.ForeignKey(
        ContentType, models.DO_NOTHING, db_column='LineType',  blank=True, null=True, related_name='line_type', unique=False)
    line_id = models.CharField(db_column='LineId', max_length=255,  blank=True, null=True)  # object is referenced by uuid
    line = GenericForeignKey('line_type', 'line_id')

    invoice = models.ForeignKey(Invoice, models.DO_NOTHING, db_column='InvoiceId', related_name="line_items")

    class Meta:
        managed = True
        db_table = 'tblInvoiceLineItem'


class InvoicePayment(GenericInvoicePayment):
    invoice = models.ForeignKey(Invoice, models.DO_NOTHING, db_column='InvoiceId', related_name="payments")

    class Meta:
        managed = True
        db_table = 'tblInvoicePayment'


class InvoiceEvent(GenericInvoiceEvent):
    invoice = models.ForeignKey(Invoice, models.DO_NOTHING, db_column='InvoiceId', related_name="events")

    class Meta:
        managed = True
        db_table = 'tblInvoiceEvent'


class Bill(GenericInvoice):
    subject_type = models.ForeignKey(ContentType, models.DO_NOTHING,
                                        db_column='SubjectType', null=True,blank=True, related_name='subject_type_bill',
                                     unique=False)
    subject_id = models.CharField(db_column='SubjectId', max_length=255, blank=True, null=True)  # object is referenced by uuid
    subject = GenericForeignKey('subject_type', 'subject_id')

    date_bill = DateField(db_column='DateBill', default=date.today, blank=True, null=True)
    month = models.SmallIntegerField(db_column='Month', null=True)
    year = models.SmallIntegerField(db_column='Year', null=True)

    class Meta:
        managed = True
        db_table = 'tblBill'


class BillItem(GenericInvoiceLineItem):
    line_type = models.ForeignKey(
        ContentType, models.DO_NOTHING, db_column='LineType',  blank=True, null=True, related_name='line_type_bill', unique=False)
    line_id = models.CharField(db_column='LineId', max_length=255,  blank=True, null=True)  # object is referenced by uuid
    line = GenericForeignKey('line_type', 'line_id')

    bill = models.ForeignKey(Bill, models.DO_NOTHING, db_column='BillId', related_name="line_items_bill")

    class Meta:
        managed = True
        db_table = 'tblBillLineItem'


class BillPayment(GenericInvoicePayment):
    bill = models.ForeignKey(Bill, models.DO_NOTHING, db_column='BillId', related_name="payments_bill")

    class Meta:
        managed = True
        db_table = 'tblBillPayment'


class BillEvent(GenericInvoiceEvent):
    bill = models.ForeignKey(Bill, models.DO_NOTHING, db_column='BillId', related_name="events_bill")

    class Meta:
        managed = True
        db_table = 'tblBillEvent'


class InvoiceMutation(UUIDModel, ObjectMutation):
    invoice = models.ForeignKey(Invoice, models.DO_NOTHING, related_name='mutations')
    mutation = models.ForeignKey(MutationLog, models.DO_NOTHING, related_name='invoices')

    class Meta:
        managed = True
        db_table = "invoice_invoiceMutation"


class InvoicePaymentMutation(UUIDModel, ObjectMutation):
    invoice_payment = models.ForeignKey(InvoicePayment, models.DO_NOTHING, related_name='mutations')
    mutation = models.ForeignKey(MutationLog, models.DO_NOTHING, related_name='invoice_payments')

    class Meta:
        managed = True
        db_table = "invoice_InvoicePaymentMutation"


class InvoiceLineItemMutation(UUIDModel, ObjectMutation):
    invoice_line_items = models.ForeignKey(InvoiceLineItem, models.DO_NOTHING, related_name='mutations')
    mutation = models.ForeignKey(MutationLog, models.DO_NOTHING, related_name='invoice_line_items')

    class Meta:
        managed = True
        db_table = "invoice_InvoiceLineItemsMutation"


class InvoiceEventMutation(UUIDModel, ObjectMutation):
    invoice_event = models.ForeignKey(InvoiceEvent, models.DO_NOTHING, related_name='mutations')
    mutation = models.ForeignKey(MutationLog, models.DO_NOTHING, related_name='event_messages')

    class Meta:
        managed = True
        db_table = "invoice_InvoiceEventMutation"


class BillMutation(UUIDModel, ObjectMutation):
    bill = models.ForeignKey(Bill, models.DO_NOTHING, related_name='mutations')
    mutation = models.ForeignKey(MutationLog, models.DO_NOTHING, related_name='bills')

    class Meta:
        managed = True
        db_table = "bill_BillMutation"


class BillPaymentMutation(UUIDModel, ObjectMutation):
    bill_payment = models.ForeignKey(BillPayment, models.DO_NOTHING, related_name='mutations')
    mutation = models.ForeignKey(MutationLog, models.DO_NOTHING, related_name='bill_payments')

    class Meta:
        managed = True
        db_table = "bill_BillPaymentMutation"


class BillItemMutation(UUIDModel, ObjectMutation):
    bile_items = models.ForeignKey(BillItem, models.DO_NOTHING, related_name='mutations')
    mutation = models.ForeignKey(MutationLog, models.DO_NOTHING, related_name='bill_line_items')

    class Meta:
        managed = True
        db_table = "bill_BillLineItemsMutation"


class BillEventMutation(UUIDModel, ObjectMutation):
    bill_event = models.ForeignKey(BillEvent, models.DO_NOTHING, related_name='mutations')
    mutation = models.ForeignKey(MutationLog, models.DO_NOTHING, related_name='bill_event_messages')

    class Meta:
        managed = True
        db_table = "bill_BillEventMutation"


# new approach for payment tables: 'PaymentInvoice' and 'DetailPaymentInvoice'
class PaymentInvoice(GenericInvoiceQuerysetMixin, HistoryModel):
    class ReconciliationStatus(models.IntegerChoices):
        NOT_RECONCILIATED = 0, _('not reconciliated')
        RECONCILIATED = 1, _('reconciliated')
        REFUNDED = 2, _('refunded')
        CANCELLED = 3, _('cancelled')

    code_tp = models.CharField(db_column='CodeTp', max_length=255,  blank=True, null=True)
    code_ext = models.CharField(db_column='CodeExt', max_length=255,  blank=True, null=True)
    code_receipt = models.CharField(db_column='CodeReceipt', max_length=255,  blank=True, null=True)

    label = models.CharField(db_column='Label', max_length=255,  blank=True, null=True)

    reconciliation_status = models.SmallIntegerField(db_column='ReconciliationStatus', null=False,
                                                     choices=ReconciliationStatus.choices)

    fees = models.DecimalField(db_column='Fees', max_digits=18, decimal_places=2,  blank=True, null=True)
    amount_received = models.DecimalField(db_column='AmountReceived', max_digits=18, decimal_places=2,  blank=True, null=True)

    date_payment = DateField(db_column='DatePayment',  blank=True, null=True)

    payment_origin = models.CharField(db_column='PaymentOrigin', max_length=255,  blank=True, null=True)

    payer_ref = models.CharField(db_column='PayerRef', max_length=255)
    payer_name = models.CharField(db_column='PayerName', max_length=255,  blank=True, null=True)

    objects = GenericInvoiceManager()

    class Meta:
        managed = True
        db_table = "tblPaymentInvoice"


class DetailPaymentInvoice(GenericInvoiceQuerysetMixin, HistoryModel):
    class DetailPaymentStatus(models.IntegerChoices):
        REJECTED = 0, _('rejected')
        ACCEPTED = 1, _('accepted')
        REFUNDED = 2, _('refunded')
        CANCELLED = 3, _('cancelled')

    payment = models.ForeignKey(PaymentInvoice, models.DO_NOTHING,
                                db_column='PaymentUUID', related_name="invoice_payments")

    subject_type = models.ForeignKey(ContentType, models.DO_NOTHING, db_column='SubjectType',
                                     related_name='subject_type_payment',  blank=True, null=True, unique=False)
    subject_id = models.CharField(db_column='SubjectId', max_length=255,  blank=True, null=True)
    subject = GenericForeignKey('subject_type', 'subject_id')

    status = models.SmallIntegerField(db_column='Status', null=False, choices=DetailPaymentStatus.choices)
    fees = models.DecimalField(db_column='Fees', max_digits=18, decimal_places=2,  blank=True, null=True)
    amount = models.DecimalField(db_column='Amount', max_digits=18, decimal_places=2,  blank=True, null=True)

    reconcilation_id = models.CharField(db_column='ReconcilationId', max_length=255,  blank=True, null=True)
    reconcilation_date = models.DateField(db_column='ReconcilationDate',  blank=True, null=True)

    objects = GenericInvoiceManager()

    class Meta:
        managed = True
        db_table = "tblDetailPaymentInvoice"


class PaymentInvoiceMutation(UUIDModel, ObjectMutation):
    payment_invoice = models.ForeignKey(PaymentInvoice, models.DO_NOTHING, related_name='mutations')
    mutation = models.ForeignKey(MutationLog, models.DO_NOTHING, related_name='payment_invoices')

    class Meta:
        managed = True
        db_table = "paymentinvoice_PaymentInvoiceMutation"


class DetailPaymentInvoiceMutation(UUIDModel, ObjectMutation):
    detail_payment_invoice = models.ForeignKey(DetailPaymentInvoice, models.DO_NOTHING, related_name='mutations')
    mutation = models.ForeignKey(MutationLog, models.DO_NOTHING, related_name='detail_payment_invoices')

    class Meta:
        managed = True
        db_table = "paymentinvoice_DetailPaymentInvoiceMutation"
