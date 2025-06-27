import graphene

from core.schema import signal_mutation_module_validate
from invoice.gql import query_mixins
from invoice.gql.invoice import DeleteInvoiceMutation, GenerateTimeframeInvoices
from invoice.gql.invoice_event.mutation import CreateInvoiceEventMutation
from invoice.gql.invoice_payment.mutation import (
    CreateInvoicePaymentMutation,
    UpdateInvoicePaymentMutation,
    DeleteInvoicePaymentMutation
)
from invoice.gql.bill.mutation import DeleteBillMutation, CreateMonthBillMutation
from invoice.gql.bill_event.mutation import CreateBillEventMutation
from invoice.gql.bill_payment.mutation import (
    CreateBillPaymentMutation,
    UpdateBillPaymentMutation,
    DeleteBillPaymentMutation
)
from invoice.gql.payment_invoice.mutation import (
    CreatePaymentInvoiceMutation,
    CreatePaymentInvoiceWithDetailMutation,
    UpdatePaymentInvoiceMutation,
    DeletePaymentInvoiceMutation
)
from invoice.gql.detail_payment_invoice.mutation import (
    CreateDetailPaymentInvoiceMutation,
    UpdateDetailPaymentInvoiceMutation,
    DeleteDetailPaymentInvoiceMutation
)
from invoice.models import (
    InvoicePayment,
    InvoicePaymentMutation,
    InvoiceEventMutation,
    InvoiceEvent,
    BillPayment,
    BillPaymentMutation,
    BillEventMutation,
    BillEvent,
    PaymentInvoice,
    DetailPaymentInvoice,
    PaymentInvoiceMutation,
    DetailPaymentInvoiceMutation,
)


class Query(
    query_mixins.InvoiceQueryMixin,
    query_mixins.InvoiceLineItemQueryMixin,
    query_mixins.InvoicePaymentQueryMixin,
    query_mixins.InvoiceEventQueryMixin,
    query_mixins.BillQueryMixin,
    query_mixins.BillItemQueryMixin,
    query_mixins.BillPaymentQueryMixin,
    query_mixins.BillEventQueryMixin,
    query_mixins.PaymentInvoiceQueryMixin,
    query_mixins.DetailPaymentInvoiceQueryMixin,
    graphene.ObjectType
):
    pass


class Mutation(graphene.ObjectType):
    # invoice mutations
    generate_invoices_for_time_period = GenerateTimeframeInvoices.Field()
    delete_invoice = DeleteInvoiceMutation.Field()
    create_invoice_payment = CreateInvoicePaymentMutation.Field()
    update_invoice_payment = UpdateInvoicePaymentMutation.Field()
    delete_invoice_payment = DeleteInvoicePaymentMutation.Field()

    create_invoice_event_message = CreateInvoiceEventMutation.Field()

    # bill mutations
    delete_bill = DeleteBillMutation.Field()
    create_month_bill = CreateMonthBillMutation.Field()
    create_bill_payment = CreateBillPaymentMutation.Field()
    update_bill_payment = UpdateBillPaymentMutation.Field()
    delete_bill_payment = DeleteBillPaymentMutation.Field()
    create_bill_event_type = CreateBillEventMutation.Field()

    # payment mutations
    create_payment_invoice = CreatePaymentInvoiceMutation.Field()
    create_payment_with_detail_invoice = CreatePaymentInvoiceWithDetailMutation.Field()
    update_payment_invoice = UpdatePaymentInvoiceMutation.Field()
    delete_payment_invoice = DeletePaymentInvoiceMutation.Field()
    create_detail_payment_invoice = CreateDetailPaymentInvoiceMutation.Field()
    update_detail_payment_invoice = UpdateDetailPaymentInvoiceMutation.Field()
    delete_detail_payment_invoice = DeleteDetailPaymentInvoiceMutation.Field()


def _on_mutation_log(mutation_model, model, obj_type, sender, **kwargs):
    uuids = kwargs['data'].get('ids', []) or kwargs['data'].get('uuids', [])
    if not uuids:
        uuid = kwargs['data'].get('id', None) or kwargs['data'].get('uuid', [])
        uuids = [uuid] if uuid else []
    if not uuids:
        return []
    impacted = model.objects.filter(uuid__in=uuids).all()
    for item in impacted:
        mutation_model.objects.create(
            **{obj_type: item, 'mutation_id':kwargs['mutation_log_id']}
        )
    return []


def on_invoice_payment_mutation(sender, **kwargs):
    if kwargs.get('mutation_class', None) \
            in ('CreateInvoicePaymentMutation', 'UpdateInvoicePaymentMutation', 'DeleteInvoicePaymentMutation'):
        return _on_mutation_log(InvoicePaymentMutation, InvoicePayment, 'invoice_payment', sender, **kwargs)

    if kwargs.get('mutation_class', None) in ('CreateInvoiceEventMutation'):
        return _on_mutation_log(InvoiceEventMutation, InvoiceEvent, 'invoice_event', sender, **kwargs)

    return []


def on_bill_payment_mutation(sender, **kwargs):
    if kwargs.get('mutation_class', None) \
            in ('CreateBillPaymentMutation', 'UpdateBillPaymentMutation', 'DeleteBillPaymentMutation'):
        return _on_mutation_log(BillPaymentMutation, BillPayment, 'bill_payment', sender, **kwargs)

    if kwargs.get('mutation_class', None) in ('CreateBillEventMutation'):
        return _on_mutation_log(BillEventMutation, BillEvent, 'bill_event', sender, **kwargs)

    return []


def on_payment_invoice_mutation(sender, **kwargs):
    if kwargs.get('mutation_class', None) \
            in ('CreatePaymentInvoiceMutation', 'UpdatePaymentInvoiceMutation', 'DeletePaymentInvoiceMutation',
                'CreatePaymentInvoiceWithDetailMutation'):
        return _on_mutation_log(PaymentInvoiceMutation, PaymentInvoice, 'payment_invoice', sender, **kwargs)

    if kwargs.get('mutation_class', None) \
            in ('CreateDetailPaymentInvoiceMutation', 'UpdateDetailPaymentInvoiceMutation',
                'DeleteDetailPaymentInvoiceMutation'):
        return _on_mutation_log(DetailPaymentInvoiceMutation, DetailPaymentInvoice, 'detail_payment_invoice', sender, **kwargs)

    return []


signal_mutation_module_validate["invoice"].connect(on_invoice_payment_mutation)
signal_mutation_module_validate["invoice"].connect(on_bill_payment_mutation)
signal_mutation_module_validate["invoice"].connect(on_payment_invoice_mutation)
