import core
import datetime

import logging
from uuid import uuid4

import graphene
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ValidationError
from policyholder.models import PolicyHolder
from django.db import transaction
from core.gql.gql_mutations.base_mutation import BaseMutation, BaseHistoryModelDeleteMutationMixin, \
    BaseHistoryModelCreateMutationMixin
from core.models import MutationLog
from core.schema import OpenIMISMutation
from invoice.apps import InvoiceConfig
from invoice.models import Bill
from django.db.models import Q

from invoice.services import BillService
from worker_voucher.models import WorkerVoucher
from worker_voucher.services import economic_unit_user_filter, create_voucher_bill

logger = logging.getLogger(__name__)


class DeleteBillMutation(BaseHistoryModelDeleteMutationMixin, BaseMutation):
    _mutation_class = "DeleteBillMutation"
    _mutation_module = "invoice"
    _model = Bill

    @classmethod
    def _validate_mutation(cls, user, **data):
        if type(user) is AnonymousUser or not user.id or not user.has_perms(
                InvoiceConfig.gql_bill_delete_perms):
            raise ValidationError("mutation.authentication_required")

    class Input(OpenIMISMutation.Input):
        uuids = graphene.List(graphene.UUID)


class CreateMonthBillMutation(BaseHistoryModelCreateMutationMixin, BaseMutation):
    _mutation_class = "CreateMonthBillMutation"
    _mutation_module = "invoice"
    _model = Bill

    @classmethod
    def _validate_mutation(cls, user, month: int, **_):
        if not (0 < month < 13):
            raise ValidationError("month.invalid")

        if (type(user) is AnonymousUser or not user.id ):
                # or not user.has_perms(
                # InvoiceConfig.gql_bill_create_perms))
            raise ValidationError("mutation.authentication_required")

    @classmethod
    def _mutate(cls, user, month: int, economic_unit_code: int, **data):
        now = datetime.datetime.now()

        year = datetime.datetime.now().year
        if now.month < month:
            year -= 1

        policyholder = PolicyHolder.objects.filter(
            code=economic_unit_code,
            is_deleted=False,
        ).first()

        # Get all unpaid vouchers for the specified month (status AWAITING_PAYMENT)
        unpaid_vouchers = WorkerVoucher.objects.filter(
            Q(status=WorkerVoucher.Status.ASSIGNED) &
            Q(assigned_date__year=year) &
            Q(assigned_date__month=month) &
            Q(bill_code=None)
        ).filter(
            is_deleted=False,
        ).filter(
            economic_unit_user_filter(user, prefix='policyholder__')
        )

        if not unpaid_vouchers.exists():
            raise ValidationError("mutation.no_vouchers_without_bill")

        voucher_ids = [voucher.id for voucher in unpaid_vouchers]

        with transaction.atomic():
            create_voucher_bill(user, voucher_ids, policyholder.id, month, year)
        return None

    class Input(OpenIMISMutation.Input):
        month = graphene.Int(required=True, description='Start from 1 ( january )')
        economic_unit_code = graphene.ID(required=True)
