import uuid

from django.db import models
from django.db.models import Sum
from django.db.models.deletion import SET_NULL

from django_countries.fields import CountryField

from games.models import Edition
from adoption.models import Package
from profiles.models import UserProfile


class Product(models.Model):
    game = models.ForeignKey(
        Edition,
        null=True,
        blank=True,
        on_delete=models.CASCADE
    )
    adoption = models.ForeignKey(
        Package,
        null=True,
        blank=True,
        on_delete=models.CASCADE
    )

    sku = models.CharField(
        max_length=12,
        editable=False,
        unique=True,
        blank=True,
    )
    price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        if self.game:
            name = self.game.friendly_name_full
        elif self.adoption:
            animal = self.adoption.adoption.animal
            package = self.adoption.friendly_name
            name = animal.title() + ' ' + package
        return name


class Order(models.Model):
    order_number = models.CharField(max_length=32, null=False, editable=False)

    user_profile = models.ForeignKey(
        UserProfile,
        on_delete=SET_NULL,
        null=True,
        blank=True,
        related_name='orders'
    )

    first_name = models.CharField(max_length=50, null=False, blank=False)
    last_name = models.CharField(max_length=50, null=False, blank=False)
    email = models.EmailField(max_length=254, null=False, blank=False)
    street_address = models.CharField(max_length=80, null=False, blank=False)
    street_address_2 = models.CharField(max_length=80, null=True, blank=True)
    country = CountryField(blank_label='Select country *', null=False, blank=False)
    town_or_city = models.CharField(max_length=40, null=False, blank=False)
    county = models.CharField(max_length=80, null=True, blank=True)
    postcode = models.CharField(max_length=20, null=False, blank=False)
    phone_number = models.CharField(max_length=20, null=False, blank=False)
    date = models.DateTimeField(auto_now_add=True)
    order_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=False,
        default=0
    )
    grand_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=False,
        default=0
    )
    original_cart = models.TextField(null=False, blank=False, default='')
    stripe_pid = models.CharField(
        max_length=254,
        null=False,
        blank=False,
        default=''
    )

    def _generate_order_number(self):
        """ Generate a random, unique order number using UUID  """

        return uuid.uuid4().hex.upper()

    def update_total(self):
        """ Update grand total each time a line item is added """

        self.order_total = self.lineitems.aggregate(
            Sum('lineitem_total'))['lineitem_total__sum'] or 0

        self.grand_total = self.order_total
        self.save()

    def save(self, *args, **kwargs):
        """ Override original save method to set order number """

        if not self.order_number:
            self.order_number = self._generate_order_number()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.order_number


class OrderLineItem(models.Model):
    order = models.ForeignKey(
        Order,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name='lineitems'
    )
    product = models.ForeignKey(
        Product,
        null=False,
        blank=False,
        on_delete=models.CASCADE
    )

    quantity = models.IntegerField(null=True, blank=True, default=0)
    lineitem_total = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=False,
        blank=False,
        editable=False
    )

    def save(self, *args, **kwargs):
        """ Override original save method to set order number """

        self.lineitem_total = self.product.price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        if self.product.game:
            sku = self.product.game.sku
        elif self.product.adoption:
            sku = self.product.adoption.sku
        return f'SKU {sku.upper()} on order {self.order.order_number}'
