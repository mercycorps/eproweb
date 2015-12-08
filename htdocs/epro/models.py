from decimal import Decimal

from django.core.urlresolvers import reverse_lazy
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError

from django.db.models import Q, Sum, Max, Min, Count
from django.db import models

from django.utils import timezone
from django.utils.timezone import utc

from django.contrib.auth.models import User

from djangocosign.models import UserProfile, Region, Country, Office

from .fields import USDCurrencyField
from django.utils.timezone import utc
import datetime, time, logging

def validate_even(value):
    if value % 2 != 0:
        raise ValidationError('%s is not an even number' % value)

def validate_positive(value):
    if value <= 0:
        raise ValidationError('%s is not greater than zero' % value)


class CommonBaseAbstractModel(models.Model):
    created_by = models.ForeignKey(UserProfile, blank=True, null=True, related_name="%(app_label)s_%(class)s_created")
    updated_by = models.ForeignKey(UserProfile, blank=True, null=True, related_name="%(app_label)s_%(class)s_updated")
    created = models.DateTimeField(editable=False, blank=True, null=True)
    updated = models.DateTimeField(editable=False, blank=True, null=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        now_utc = datetime.datetime.utcnow().replace(tzinfo=utc)
        if self.id:
            self.updated = now_utc
        else:
            self.created = now_utc
        super(CommonBaseAbstractModel, self).save(*args, **kwargs)


class Currency(CommonBaseAbstractModel):
    code = models.CharField(unique=True, max_length=3, null=False, blank=False)
    country = models.ForeignKey(Country, blank=False, null=False,
                                on_delete=models.CASCADE, related_name="currencies")
    name = models.CharField(max_length=50, null=True, blank=True)

    def __unicode__(self):
        return self.code

    def __str__(self):
        return self.code

    class Meta(object):
        verbose_name = 'Currency'
        ordering = ['country', 'code']


class FundCode(CommonBaseAbstractModel):
    code = models.CharField(unique=True, max_length=5, null=False, blank=False, db_index=True)

    def __unicode__(self):
        return u'%s' % self.code

    def __ustr__(self):
        return u'%s' % self.code

    class Meta(object):
        verbose_name = 'Fund Code'
        ordering = ['code']


class DeptCode(CommonBaseAbstractModel):
    code = models.CharField(unique=True, max_length=5, null=False, blank=False, db_index=True)

    def __unicode__(self):
        return u'%s' % self.code

    def __str__(self):
        return u'%s' % self.code

    class Meta(object):
        verbose_name = 'Department Code'
        ordering = ['code']

class PurchaseRequestManager(models.Manager):
    @property
    def goods(self):
        return self.get_query_set().filter(pr_type=PurchaseRequest.TYPE_GOODS)

    @property
    def services(self):
        return self.get_query_set().filter(pr_type=PurchaseRequest.TYPE_SERVICES)


class PurchaseRequest(CommonBaseAbstractModel):
    STATUS_DRAFT = 'drafted'
    STATUS_PENDING_PROCUREMENT_VERIFICATION = 'pending_procurement_verification'
    STATUS_PENDING_APPROVAL = 'pending_approval'
    STATUS_PENDING_FINANCIAL_REVIEW = 'pending_financial_review'
    STATUS_ONGOING = 'ongoing'
    STATUS_COMPLETED = 'completed'
    STATUS_ONHOLD = 'onhold'
    STATUS_CANCELED = 'canceled'
    STATUS_REJECTED = 'rejected'
    PR_STATUS_CHOICES = (
        (STATUS_DRAFT, 'Draf'),
        (STATUS_PENDING_PROCUREMENT_VERIFICATION, 'Pending Procurement Verification'),
        (STATUS_PENDING_APPROVAL, 'Pending Approval'),
        (STATUS_PENDING_FINANCIAL_REVIEW, 'Pending Financial Review'),
        (STATUS_ONGOING, 'Ongoing'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_ONHOLD, 'On Hold'),
        (STATUS_REJECTED, 'Rejected'),
        (STATUS_CANCELED, 'Canceled'),
    )

    TYPE_GOODS = 'goods'
    TYPE_SERVICES = 'services'
    PR_TYPE_CHOICES = (
        (TYPE_GOODS, 'Goods'),
        (TYPE_SERVICES, 'Services'),
    )

    EXPENSE_TYPE_PROGRAM = 'program'
    EXPENSE_TYPE_OPERATIONAL = 'operationa'
    EXPENSE_TYPE_CHOICES = (
        (EXPENSE_TYPE_PROGRAM, 'Program'),
        (EXPENSE_TYPE_OPERATIONAL, 'Operational'),
    )

    def is_finalized(self):
        return self.status == STATUS_COMPLETED

    def is_canceled(self):
        return self.status == STATUS_CANCELED

    #pr_number = models.PositiveIntegerField(validators=[validate_positive,])
    country = models.ForeignKey(Country, related_name='prs', null=False, blank=False, on_delete=models.CASCADE)
    office = models.ForeignKey(Office, related_name='prs', null=False, blank=False, on_delete=models.DO_NOTHING)
    currency = models.ForeignKey(Currency, related_name='prs', null=False, blank=False, on_delete=models.CASCADE)
    dollar_exchange_rate = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.0)], null=False, blank=False)
    delivery_address = models.CharField(max_length=100, blank=False, null=False)
    project_reference = models.CharField(max_length=250, null=False, blank=False)
    originator = models.ForeignKey(UserProfile, related_name='prs')
    origination_date = models.DateField(auto_now=False, auto_now_add=True)
    required_date = models.DateField(auto_now=False, auto_now_add=False, null=False, blank=False)
    submission_date = models.DateField(auto_now=False, auto_now_add=False, blank=True, null=True)
    approver1 = models.ForeignKey(UserProfile, related_name='pr_approvers1')
    approval1_date = models.DateField(auto_now=False, blank=True, null=True, auto_now_add=False)
    approver2 = models.ForeignKey(UserProfile, blank=True, null=True, related_name='pr_approver2')
    approval2_date = models.DateField(auto_now=False, auto_now_add=False, blank=True, null=True)
    finance_reviewer = models.ForeignKey(UserProfile, blank=True, null=True, related_name='pr_reviewer')
    finance_review_date = models.DateField(auto_now=False, auto_now_add=False, blank=True, null=True)
    status = models.CharField(max_length=50, choices=PR_STATUS_CHOICES, default=STATUS_ONGOING, blank=True, null=True)
    pr_type = models.CharField(max_length=50, choices=PR_TYPE_CHOICES, default=TYPE_GOODS, null=True, blank=True)
    expense_type = models.CharField(max_length=50, choices=EXPENSE_TYPE_CHOICES, null=True, blank=True)
    processing_office = models.ForeignKey(Office, related_name='pr_processing_office', blank=True, null=True)
    assignedTo = models.ForeignKey(UserProfile, blank=True, null=True, related_name='assignee')
    notes = models.TextField(max_length=255, null=True, blank=True)
    preferred_supplier = models.BooleanField(default=False)
    cancellation_date = models.DateTimeField(auto_now=False, auto_now_add=False, blank=True, null=True)
    objects = PurchaseRequestManager() # Changing the default manager

    def __unicode__(self):
        return '%s-%s: %s' % (self.office.name, self.pk, self.project_reference)

    def __str__(self):
        return '%s-%s: %s' % (self.office.name, self.pk, self.project_reference)

    def get_absolute_url(self):
        # Redirect to this URl after an object is created using CreateView
        return reverse_lazy('pr_view', kwargs={'pk': self.pk}) #args=[str(self.id)])

    def clean(self):
        # Don't allow draft purchase_requests to have a submission_date
        if self.status == 'draft' and self.submission_date is not None:
            raise ValidationError(_('Draft Purchase Requests may not have a submission date.'))

    class Meta(object):
        verbose_name = 'Purchase Request'
        ordering = ['country', 'office']
        get_latest_by = "submission_date"


class Vendor(CommonBaseAbstractModel):
    name = models.CharField(max_length=100, null=False, blank=False)
    description = models.CharField(max_length=255, null=True, blank=True)
    contact_person = models.CharField(max_length=100, null=True, blank=True)
    address = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=25, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    black_listed = models.BooleanField(default=False)
    reason_black_listed = models.CharField(max_length=255, null=True, blank=True)
    black_listed_date = models.DateField(null=True, blank=True)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse_lazy('vendor', kwargs={'pk': self.pk}) #args=[str(self.id)])


class FinanceCodes(CommonBaseAbstractModel):
    gl_account = models.PositiveIntegerField(validators=[validate_positive,], null=False, blank=False)
    fund_code = models.ForeignKey(FundCode, null=False, blank=False)
    dept_code = models.ForeignKey(DeptCode, null=False, blank=False)
    office_code = models.ForeignKey(Office, null=False, blank=False)
    lin_code = models.CharField(max_length=9, blank=True, null=True)
    activity_code = models.CharField(max_length=9, blank=True, null=True)
    employee_id = models.PositiveIntegerField(validators=[validate_positive,], null=True, blank=True)
    allocation_percent = models.DecimalField(max_digits=5, decimal_places=2,
                                validators=[MaxValueValidator(100.00), MinValueValidator(1.00) ],
                                blank=False, null=False,
                                default=Decimal("100.00"))

    def __unicode__(self):
        return "%s-%s" % (self.gl_account, str(self.fund_code))

    def __str__(self):
        return "%s-%s" % (self.gl_account, str(self.fund_code))

    def get_absolute_url(self):
        return reverse_lazy('pr_view', kwargs={'pk': 1})

class Item(CommonBaseAbstractModel):
    purchase_request = models.ForeignKey(PurchaseRequest,
                                            related_name='items',
                                            on_delete=models.CASCADE)
    quantity_requested = models.PositiveIntegerField(validators=[MinValueValidator(0.0)], verbose_name='Quantity')
    unit = models.CharField(max_length=20, null=False, blank=False)
    description_pr = models.TextField(null=False, blank=False, verbose_name='Description',
                                        help_text='Provide detailed description')
    description_po = models.TextField(null=False, blank=True)
    price_estimated_local = models.DecimalField(max_digits=10, decimal_places=2,
                                        validators=[MinValueValidator(0.0)],
                                        verbose_name='Price',
                                        help_text='Price of one unit in local currency',)
    price_estimated_usd = USDCurrencyField(verbose_name='Price USD', help_text='Price of one unit in US Dollars')
    price_estimated_local_subtotal = models.DecimalField(max_digits=10, decimal_places=2,
                                        validators=[MinValueValidator(0.0)],
                                        verbose_name='Price Subtotal',
                                        default=Decimal('0.00'),)
    price_estimated_usd_subtotal = models.DecimalField(max_digits=10, decimal_places=2,
                                        validators=[MinValueValidator(0.0)],
                                        verbose_name='Price estimated in US Dollars Subtotal',)
    finance_codes = models.ManyToManyField(FinanceCodes, related_name='items', null=False, blank=False)

    def __unicode__(self):
        return u'%s' % (self.description_pr)

    def __str__(self):
        return '%s' % (self.description_pr)

    def save(self, *args, **kwargs):
        if not self.description_po and self.description_pr:
            self.description_po = self.description_pr
        self.price_estimated_local_subtotal = round(self.price_estimated_local * self.quantity_requested,2)
        self.price_estimated_usd = round(self.price_estimated_local / self.purchase_request.dollar_exchange_rate, 2)
        self.price_estimated_usd_subtotal = round(self.price_estimated_usd * self.quantity_requested, 2)
        super(Item, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse_lazy('pr_view', kwargs={'pk': self.purchase_request.pk}) #args=[str(self.id)])

    class Meta(object):
        verbose_name = 'Item'
        ordering = ['purchase_request']
        order_with_respect_to = 'purchase_request'

class QuotationAnalysis(CommonBaseAbstractModel):
    analysis_date = models.DateField(null=True, blank=True, auto_now=False, auto_now_add=False)
    delivery_date = models.DateField(null=True, blank=True, auto_now=False, auto_now_add=False)
    selected_vendor = models.ForeignKey(Vendor, null=True, blank=True, related_name='qutoation_analyses')
    justification = models.TextField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)


class RequestForQuotation(CommonBaseAbstractModel):
    purchase_request = models.ForeignKey(PurchaseRequest, related_name='rfqs', on_delete=models.CASCADE)
    vendor = models.ForeignKey(Vendor, related_name='rfqs', on_delete=models.SET_NULL, null=True, blank=True)
    date_submitted_to_vendor = models.DateField(null=True, blank=True, auto_now=False, auto_now_add=False)
    date_received_from_vendor = models.DateField(null=True, blank=True, auto_now=False, auto_now_add=False)
    insurance = models.DecimalField(max_digits=10, decimal_places=2,
                                        validators=[MinValueValidator(0.0)],
                                        default=Decimal('0.00'),)
    shipping_and_handling = models.DecimalField(max_digits=10, decimal_places=2,
                                        validators=[MinValueValidator(0.0)],
                                        default=Decimal('0.00'),)
    vat = models.DecimalField(max_digits=10, decimal_places=2,
                                        validators=[MinValueValidator(0.0)],
                                        default=Decimal('0.00'),)
    meets_specs = models.BooleanField(default=False)
    meets_compliance = models.BooleanField(default=False)
    complete_order_delivery_date = models.DateField(null=True, blank=True, auto_now=False, auto_now_add=False)
    complete_order_payment_terms = models.CharField(max_length=255, null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    quotation_analysis = models.ForeignKey(QuotationAnalysis, related_name='rfqs', null=True, blank=True)

    def save(self, *args, **kwargs):
        self.complete_order_delivery_date = self.rfq_items.aggregate(Max('delivery_date'))
        super(RequestForQuotation, self).save(*args, **kwargs)


class RequestForQuotationItem(CommonBaseAbstractModel):
    request_for_quotation = models.ForeignKey(RequestForQuotation, related_name='rfq_items')
    item = models.ForeignKey(Item, related_name='request_for_quotation_items')
    quoted_price_local_currency = models.DecimalField(max_digits=10, decimal_places=2,
                                        validators=[MinValueValidator(0.0)],
                                        default=Decimal('0.00'),)
    quoted_price_local_currency_subtotal = models.DecimalField(max_digits=10, decimal_places=2,
                                        validators=[MinValueValidator(0.0)],
                                        default=Decimal('0.00'),)
    payment_terms = models.CharField(max_length=255, null=True, blank=True)
    delivery_date = models.DateField(null=True, blank=True, auto_now=False, auto_now_add=False)
    warranty = models.CharField(max_length=255, null=True, blank=True)
    validity_of_offer = models.CharField(max_length=255, null=True, blank=True)
    origin_of_goods = models.CharField(max_length=255, null=True, blank=True)
    remarks = models.CharField(max_length=255, null=True, blank=True)


class PurchaseOrder(CommonBaseAbstractModel):
    purchase_request = models.ForeignKey(PurchaseRequest,
                                            related_name='purchase_orders',
                                            on_delete=models.CASCADE)
    country = models.ForeignKey(Country, related_name='purchase_orders', on_delete=models.CASCADE)
    office = models.ForeignKey(Office, related_name='purchase_orders', on_delete=models.DO_NOTHING)
    currency = models.ForeignKey(Currency, related_name='purchase_orders',
                                    on_delete=models.SET_NULL, null=True, blank=True)
    po_issued_date = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=True)
    vendor = models.ForeignKey(Vendor, related_name='purchase_orders', on_delete=models.DO_NOTHING, null=True, blank=True)
    expected_delivery_date = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=True)
    #https://docs.djangoproject.com/en/1.8/topics/db/models/#extra-fields-on-many-to-many-relationships
    items = models.ManyToManyField(Item, through='PurchaseOrderItem')
    notes = models.TextField(null=False, blank=True)
    total_local = models.DecimalField(max_digits=10, decimal_places=2,
                                        validators=[MinValueValidator(0.0)],
                                        verbose_name='Total price in local currency ',
                                        default=Decimal('0.00'),)
    total_usd = USDCurrencyField(verbose_name='Total USD', help_text='Total Price in US Dollars')
    quotation_analysis = models.ForeignKey(QuotationAnalysis, related_name='purchase_orders', null=True, blank=True)

    def save(self, *args, **kwargs):
        self.total_local = self.purchase_order_items.Aggregate(Sum(price_subtotal_local))
        self.total_usd = self.purchase_order_items.Aggregate(Sum(price_subtotal_usd))
        if self.quotation_analysis:
            self.vendor = self.quotation_analysis.selected_vendor
            self.expected_delivery_date = self.quotation_analysis.delivery_date
        super(PurchaseOrder, self).save(*args, **kwargs)

    class Meta(object):
        verbose_name = 'Purchase Order'
        ordering = ['purchase_request', ]


class PurchaseOrderItem(CommonBaseAbstractModel):
    """
    A through table for the m2m relationship b/w PurchaseOrder and Item with additional fields.
    """
    purchase_order = models.ForeignKey(PurchaseOrder, related_name='purchase_order_items')
    item = models.ForeignKey(Item, related_name='purchase_order_items')
    quantity_ordered = models.PositiveIntegerField(validators=[MinValueValidator(0.0)],null=False, blank=False)
    price_local = models.DecimalField(max_digits=10, decimal_places=2,
                                        validators=[MinValueValidator(0.0)],
                                        verbose_name='Price in local currency',
                                        help_text='Price of one unit in local currency',
                                        default=Decimal('0.00'),
                                        blank=False, null=False)
    price_usd = USDCurrencyField(verbose_name='Price USD', help_text='Price of one unit in US Dollars', blank=False, null=False)
    price_subtotal_local = models.DecimalField(max_digits=10, decimal_places=2,
                                        validators=[MinValueValidator(0.0)],
                                        verbose_name='Subtotal local currency',
                                        default=Decimal('0.00'),)
    price_subtotal_usd = USDCurrencyField(verbose_name='Subtal US Dollars')

    def save(self, *args, **kwargs):
        self.price_subtotal_local = self.price_local * self.quantity_ordered
        self.price_subtotal_usd = self.price_usd * self.quantity_ordered
        super(PurchaseOrderItems, self).save(*args, **kwargs)


class GoodsReceivedNote(CommonBaseAbstractModel):
    purchase_request = models.ForeignKey(PurchaseRequest,
                                            related_name='goods_received_notes',
                                            on_delete=models.CASCADE)
    po_number = models.PositiveIntegerField(validators=[MinValueValidator(0.0)],)
    country = models.ForeignKey(Country, related_name='goods_received_notes', on_delete=models.CASCADE)
    office = models.ForeignKey(Office, related_name='goods_received_notes', on_delete=models.DO_NOTHING)
    received_date = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=True)
    items = models.ManyToManyField(Item, through='GoodsReceivedNoteItem')

    class Meta(object):
        verbose_name = 'Goods Received Note'
        ordering = ['purchase_request',]


class GoodsReceivedNoteItem(CommonBaseAbstractModel):
    """
    A through table fro the m2m relationship b/w GoodsReceivedNote and Item with extra field
    """
    goods_received_note = models.ForeignKey(GoodsReceivedNote,
                                            related_name='goods_received_note_items',
                                            on_delete=models.CASCADE)
    item = models.ForeignKey(Item, related_name='goods_received_note_items', on_delete=models.CASCADE)
    quantity_received = models.PositiveIntegerField(validators=[MinValueValidator(0.0)],)


class PurchaseRecord(CommonBaseAbstractModel):
    # payment_voucher_num
    # payment_request_date
    # tender_yes_no
    #
    pass


class Feedback(CommonBaseAbstractModel):
    ISSUE_BUG = 'bug'
    TYPE_FEATURE = 'feature'
    TYPE_GENERAL = 'general'
    ISSUE_TYPE_CHOICES = (
        (TYPE_GENERAL, 'General Feedback'),
        (TYPE_FEATURE, 'Feature Request'),
        (ISSUE_BUG, 'Bug'),
    )
    REPORTER_ROLE_CHOICES = (
        ('originator', 'Originator'),
        ('procurement_manager', 'Procurement Manager'),
        ('procurement', 'Procurement'),
        ('finance', 'Finance'),
        ('approving_manager', 'Approving Manager'),
    )
    reporter_role = models.CharField(max_length=50, choices=REPORTER_ROLE_CHOICES, null=False, blank=False, verbose_name='Your Role')
    issue_type = models.CharField(max_length=50, choices=ISSUE_TYPE_CHOICES, null=False, blank=False)
    summary = models.CharField(max_length=80, null=False, blank=False, help_text="Provide a one sentence summary of the issue")
    description = models.CharField(max_length=500, null=False, blank=False,
        help_text="Provide detail description of the problem/bug including steps to replicate it; if it is a feature request, describe how the feature should work and what probelm will it solve")
    reference = models.URLField(null=True, blank=True,
        help_text="Include the link to the page, where the bug/problem occurs or if applicable where the feature should be implemented")
