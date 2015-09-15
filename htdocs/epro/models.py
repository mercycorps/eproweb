from decimal import Decimal

from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError

from django.db.models import Q, Sum, Max
from django.db import models

from django.utils import timezone
from django.utils.timezone import utc

from django.contrib.auth.models import User

from eproweb.utils import USDCurrencyField

def validate_even(value):
    if value % 2 != 0:
        raise ValidationError('%s is not an even number' % value)

def validate_positive(value):
    if value <= 0:
        raise ValidationError('%s is not greater than zero' % value)

class CommonBaseAbstractModel(models.Model):
    created_by = models.ForeignKey(User, blank=False, null=False, related_name="%(app_label)s_%(class)s_created")
    last_updated_by = models.ForeignKey(User, blank=False, null=False, related_name="%(app_label)s_%(class)s_updated")
    created = models.DateTimeField(auto_now=False, auto_now_add=True, editable=False)
    updated = models.DateTimeField(auto_now=True, auto_now_add=False, editable=False, blank=True, null=True)

    class Meta:
        abstract = True

class Region(CommonBaseAbstractModel):
    code = models.CharField(unique=True, max_length=20, null=False, blank=False)
    name = models.CharField(unique=True, max_length=100, null=False, blank=False)

    @property
    def countries(self):
        return Country.objects.filter(region_id=self.pk)

    def __unicode__(self):
        return u'%s - %s' % (self.code, self.name)

    def __str__(self):
        return '%s - %s' % (self.code, self.name)

    class Meta(object):
        verbose_name = 'Region'
        ordering = ['code', 'name']


class Country(CommonBaseAbstractModel):
    name = models.CharField(unique=True, max_length=100, null=False, blank=False)
    iso2 = models.CharField('2 Digit ISO', max_length=2)
    region = models.ForeignKey(Region, related_name='countries', on_delete=models.DO_NOTHING)

    @property
    def offices(self):
        return Office.objects.filter(country_id=self.pk)

    @property
    def currencies(self):
        return Currency.objects.filter(currency_id=self.pk)

    def __unicode__(self):
        return u'%s - %s' % (self.iso2, self.name)

    def __str__(self):
        return '%s - %s' % (self.iso2, self.name)

    class Meta(object):
        verbose_name = 'Country'
        ordering = ['iso2', 'name']


class Office(CommonBaseAbstractModel):
    code = models.CharField(unique=True, max_length=4, 
                            null=True, blank=False, 
                            db_index=True)
    country = models.ForeignKey(Country, blank=False, null=False, 
                                on_delete=models.CASCADE, related_name="offices")
    name = models.CharField(max_length=50, null=True, blank=True)

    def __unicode__(self):
        return u'%s - %s' % (self.code, self.name)

    def __str__(self):
        return '%s - %s' % (self.code, self.name)

    class Meta(object):
        verbose_name = 'Office'
        ordering = ['country', 'code']

class Currency(CommonBaseAbstractModel):
    code = models.CharField(unique=True, max_length=3, null=False, blank=False)
    country = models.ForeignKey(Country, blank=False, null=False, 
                                on_delete=models.CASCADE, related_name="currencies")
    name = models.CharField(max_length=50, null=True, blank=True)

    def __unicode__(self):
        return u'%s - %s' % (self.code, self.name)

    def __str__(self):
        return '%s - %s' % (self.code, self.name)

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
    STATUS_COMPLETED = 0
    STATUS_ONGOING = 1
    STATUS_CANCELED = 2
    PR_STATUS_CHOICES = (
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_ONGOING, 'Ongoing'),
        (STATUS_CANCELED, 'Canceled'),
    )

    TYPE_GOODS = 0
    TYPE_SERVICES = 1
    PR_TYPE_CHOICES = (
        (TYPE_GOODS, 'Goods'),
        (TYPE_SERVICES, 'Services'),
    )

    def is_finalized(self):
        return self.status == STATUS_COMPLETED

    def is_canceled(self):
        return self.status == STATUS_CANCELED

    pr_number = models.PositiveIntegerField(validators=[validate_positive,])
    country = models.ForeignKey(Country, related_name='purchase_requests', on_delete=models.CASCADE)
    office = models.ForeignKey(Office, related_name='purchase_requests', on_delete=models.DO_NOTHING)
    currency = models.ForeignKey(Currency, related_name='purchase_requests', 
                                    on_delete=models.SET_NULL, null=True, blank=True)
    status = models.IntegerField(choices=PR_STATUS_CHOICES, default=STATUS_ONGOING)
    pr_type = models.IntegerField(choices=PR_TYPE_CHOICES, default=TYPE_GOODS)
    project_reference = models.CharField(max_length=250, null=True, blank=True)
    cancelled_on = models.DateTimeField(auto_now=False, auto_now_add=False, blank=True, null=True)
    notes = models.TextField(null=False, blank=True)
    objects = PurchaseRequestManager() # Changing the default manager

    def __unicode__(self):
        return u'%s-%s: %s' % (self.pr_number, self.name, self.project_reference)

    def __str__(self):
        return '%s-%s: %s' % (self.pr_number, self.name, self.project_reference)

    class Meta(object):
        verbose_name = 'Purchase Request'
        ordering = ['country', 'office', 'pr_number']
        get_latest_by = "pr_date"


class Vendor(CommonBaseAbstractModel):
    name = models.CharField(max_length=100, null=False, blank=False)


class Item(CommonBaseAbstractModel):
    purchase_request = models.ForeignKey(PurchaseRequest, 
                                            related_name='items', 
                                            on_delete=models.CASCADE)
    unit = models.CharField(max_length=20, null=False, blank=False)
    quantity_requested = models.PositiveIntegerField(validators=[MinValueValidator(0.0)],)
    description_pr = models.TextField(null=False, blank=True)
    description_po = models.TextField(null=False, blank=True)
    price_estimated_local = models.DecimalField(max_digits=10, decimal_places=2,
                                        validators=[MinValueValidator(0.0)],
                                        verbose_name='Price in local currency',
                                        help_text='Price of one unit in local currency',
                                        default=Decimal('0.00'),)
    price_estimated_usd = USDCurrencyField(verbose_name='Price USD', help_text='Price of one unit in US Dollars')
    price_estimated_local_subtotal = models.DecimalField(max_digits=10, decimal_places=2,
                                        validators=[MinValueValidator(0.0)],
                                        verbose_name='Price estimated in local currency Subtotal',
                                        default=Decimal('0.00'),)
    price_estimated_usd_subtotal = models.DecimalField(max_digits=10, decimal_places=2,
                                        validators=[MinValueValidator(0.0)],
                                        verbose_name='Price estimated in US Dollars Subtotal',
                                        default=Decimal('0.00'),)
    """
    finance_codes
    """
                                        
    def __unicode__(self):
        return u'%s: %s' % (self.description_pr)

    def __str__(self):
        return '%s: %s' % (self.description_pr)

    def save(self, *args, **kwargs):
        if not self.description_po and self.description_pr:
            self.description_po = self.description_pr
        self.price_estimated_local_subtotal = self.price_estimated_local * self.quantity_requested
        self.price_estimated_usd_subtotal = self.price_estimated_usd * self.quantity_requested
        super(Item, self).save(*args, **kwargs)

    class Meta(object):
        verbose_name = 'Item'
        ordering = ['purchase_request']
        order_with_respect_to = 'purchase_request'

class PurchaseOrder(CommonBaseAbstractModel):
    purchase_request = models.ForeignKey(PurchaseRequest, 
                                            related_name='purchase_orders', 
                                            on_delete=models.CASCADE)
    po_number = models.PositiveIntegerField(validators=[MinValueValidator(0.0)],)
    country = models.ForeignKey(Country, related_name='purchase_orders', on_delete=models.CASCADE)
    office = models.ForeignKey(Office, related_name='purchase_orders', on_delete=models.DO_NOTHING)
    currency = models.ForeignKey(Currency, related_name='purchase_orders', 
                                    on_delete=models.SET_NULL, null=True, blank=True)
    po_date = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=True)
    vendor = models.ForeignKey(Vendor, related_name='purchase_orders', on_delete=models.DO_NOTHING)
    expected_delivery_date = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=True)
    #https://docs.djangoproject.com/en/1.8/topics/db/models/#extra-fields-on-many-to-many-relationships
    items = models.ManyToManyField(Item, through='PurchaseOrderItems')
    notes = models.TextField(null=False, blank=True)
    total_local = models.DecimalField(max_digits=10, decimal_places=2,
                                        validators=[MinValueValidator(0.0)],
                                        verbose_name='Total price in local currency ',
                                        default=Decimal('0.00'),)
    total_usd = USDCurrencyField(verbose_name='Total USD', help_text='Total Price in US Dollars')

    def save(self, *args, **kwargs):
        if self.pk:
            self.total_local = self.purchase_order_items.Aggregate(Sum(price_subtotal_local))
            self.total_usd = self.purchase_order_items.Aggregate(Sum(price_subtotal_usd))
        super(PurchaseOrder, self).save(*args, **kwargs)

    class Meta(object):
        verbose_name = 'Purchase Order'
        ordering = ['purchase_request', ]


class PurchaseOrderItems(CommonBaseAbstractModel):
    """
    A through table for the m2m relationship b/w PurchaseOrder and Item with additional fields.
    """
    purchase_order = models.ForeignKey(PurchaseOrder, related_name='purchase_order_items')
    item = models.ForeignKey(Item, related_name='purchase_order_items')
    quantity_ordered = models.PositiveIntegerField(validators=[MinValueValidator(0.0)],)
    price_local = models.DecimalField(max_digits=10, decimal_places=2,
                                        validators=[MinValueValidator(0.0)],
                                        verbose_name='Price in local currency',
                                        help_text='Price of one unit in local currency',
                                        default=Decimal('0.00'),)
    price_usd = USDCurrencyField(verbose_name='Price USD', help_text='Price of one unit in US Dollars')
    price_subtotal_local = models.DecimalField(max_digits=10, decimal_places=2,
                                        validators=[MinValueValidator(0.0)],
                                        verbose_name='Subtotal local currency',
                                        default=Decimal('0.00'),)
    price_subtotal_usd = USDCurrencyField(verbose_name='Subtal US Dollars')

    def save(self, *args, **kwargs):
        if self.pk:
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
    items = models.ManyToManyField(Item, through='GoodsReceivedNoteItems')
    
    class Meta(object):
        verbose_name = 'Goods Received Note'
        ordering = ['purchase_request',]


class GoodsReceivedNoteItems(CommonBaseAbstractModel):
    """
    A through table fro the m2m relationship b/w GoodsReceivedNote and Item with extra field
    """
    goods_received_note = models.ForeignKey(GoodsReceivedNote, 
                                            related_name='goods_received_note_items',
                                            on_delete=models.CASCADE)
    item = models.ForeignKey(Item, related_name='goods_received_note_items', on_delete=models.CASCADE)
    quantity_received = models.PositiveIntegerField(validators=[MinValueValidator(0.0)],)


class RequestForQuotation(CommonBaseAbstractModel):
    pass


class QuotationAnalysis(CommonBaseAbstractModel):
    pass


class PurchaseRecord(CommonBaseAbstractModel):
    # payment_voucher_num
    # payment_request_date
    # tender_yes_no
    # 
    pass


