from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import reverse
from PIL import Image
from django.utils.text import slugify
import time

# Create your models here.

CATEGORY_CHOICES = (
    ('RI', 'Rice'),
    ('CH', 'Chips'),
    ('DR', 'Drinks'),    
    ('PA', 'Pap'),
    ('BR', 'Bread'),
    ('BI', 'Biscuit'),
    ('BE', 'Beef'),
    ('CK', 'Chicken'),
    ('CL', 'Chocolate'),
)

RESIDENCE_CHOICE = (
    ('KD', 'Kgosi Dick'),
    ('MB', 'Mbada'),
    ('KH', 'Khayelitsha'),
    ('HV', 'Hopeville'),
    ('SP', 'Sol Plat'),
    ('JM', 'James'),
    ('M', 'Modiri'),
    ('N', 'Nkandla'),
    ('S', 'Sedibeng'),
    ('PG', 'Post Grad'),
    ('LC', 'Lost City'),
)

PAYMENT_CHOICES = (
    ('Card', 'Card Payment'),
    # ('Cash', 'Cash On Delivery')
)

ADDRESS_CHOICES = (
    ('B', 'billing'),
    ('S', 'shipping'),
    ('C', 'cash'),
)

DELIVERY_CHOICE = (
    ('RD', 'Residence Delivery + R10'),
    ('PU', 'Pick Up At Cafeteria + R5')
)


class Item(models.Model):
    title = models.CharField(max_length=100)
    price = models.FloatField()
    discount_price = models.FloatField(blank=True, null=True)
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=2)
    available = models.BooleanField(default=True)
    # label = models.CharField(choices=LABEL_CHOICES, max_length=1)
    slug = models.SlugField(unique=True, null = True, blank = True)
    description = models.TextField()

    def __str__(self):
        return f'{self.title} - {self.price}'

    def save(self, *args, **kwargs):
        title = self.title
        t_ = str(time.time_ns())
        slug_ = str(title +"-"+ t_)
        self.slug = slugify(slug_)
        super(Item, self).save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('core:product', kwargs={'slug': self.slug})

class Images(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='item_pic/', blank=True, null=True)

    def save(self, *args, **kwargs):
        super(Images, self).save(*args, **kwargs)

        img = Image.open(self.image.path)
        if img.height > 0 or img.width > 0:
            output_size = (400, 400)
            img.thumbnail(output_size)
            img.save(self.image.path)

    def __str__(self):
        return f'{self.item.title} - {self.item.price}'

class Voucher(models.Model):
    pass


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    residence_name = models.CharField(max_length=2, choices=RESIDENCE_CHOICE)
    block_number = models.CharField(max_length=10)
    room_number = models.CharField(max_length=4)
    student_number = models.CharField(max_length=10)
    cell_phone = models.CharField(max_length=10)
    default = models.BooleanField(default=False)
    address_type = models.CharField(max_length=1, choices=ADDRESS_CHOICES)

    def __str__(self):
        return f'{self.user} - {self.student_number}'


class Payment(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.SET_NULL, blank=True, null=True)
    m_payment_id = models.CharField(max_length=50, blank=True, null=True)
    pf = models.CharField(max_length=50, blank=True, null=True)
    ref_code = models.CharField(max_length=50, blank=True, null=True)
    amount_gross = models.CharField(max_length=20, blank=True, null=True)
    amount_fee = models.CharField(max_length=20,blank=True, null=True)
    amount_net = models.CharField(max_length=20,blank=True, null=True)
    signature = models.CharField(max_length=50, blank=True, null=True)
    payment_option = models.CharField(max_length=5, choices=PAYMENT_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username

class OrderItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1) 
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.item} of {self.quantity}"

    def get_total_item_price(self):
        return self.quantity * self.item.price

    def get_total_discount_item_price(self):
        return self.quantity * self.item.discount_price
    
    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_total_discount_item_price()

    def get_final_price(self):
        if self.item.discount_price:
            return self.get_total_discount_item_price()
        return self.get_total_item_price()


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ref_code = models.CharField(max_length=20, blank=True, null=True)
    item = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False) 
    shipping_address = models.ForeignKey(
        'Address', related_name='shipping_address', on_delete=models.SET_NULL, blank=True, null=True)        
    payment = models.ForeignKey(
        'Payment', on_delete=models.SET_NULL, blank=True, null=True)
    delivery_option = models.CharField(max_length=2, choices=DELIVERY_CHOICE, blank=True, null=True)
    being_delivered = models.BooleanField(default=False)
    received = models.BooleanField(default=False)
    student_number = models.CharField(max_length=8, blank=True, null=True)
    service_charge = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} {self.get_total()}"
    
    def get_total(self):
        total = 0
        for order_item in self.item.all():
            total += order_item.get_final_price() 
        
        return round(total,2)
    
    def get_total_quote(self):
        total = 0
        for order_item in self.item.all():
            total += order_item.get_final_price() 
        
        return round(total + self.service_charge,2)