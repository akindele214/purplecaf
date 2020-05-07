from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget
from .models import Item, Order
from django.forms import ModelForm


PAYMENT_CHOICES = (
    ('Card', 'Card Payment'),
    # ('Cash', 'Cash On Delivery')
)

SIZE_CHOICES = (
    ('SS', 'SS'),
    ('S', 'S'),
    ('M', 'M'),
    ('L', 'L'), 
    ('XL', 'XL'),
    ('XXL', 'XXL'),                  
)

RESIDENCE_CHOICE = (
    ('', 'Select Residence'),
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

DELIVERY_CHOICE = (
    ('RD', 'Residence Delivery'),
    ('PU', 'Pick Up At Cafeteria')
)


class CashCheckoutForm(forms.Form):
    shipping_address = forms.CharField(required=False)
    shipping_address2 = forms.CharField(required=False)
    shipping_country = CountryField(blank_label='(select country)').formfield(
        required=False,
        widget=CountrySelectWidget(attrs={
            'class': 'custom-select d-block w-100',
        }))
    shipping_zip = forms.CharField(required=False)
    payment_option = forms.ChoiceField(
        widget=forms.RadioSelect, choices=PAYMENT_CHOICES)
    set_default_shipping = forms.BooleanField(required=False)
    use_default_shipping = forms.BooleanField(required=False)


class CartForm(forms.Form):
    size = forms.ChoiceField(
        widget=forms.Select, choices=SIZE_CHOICES)


class CheckoutForm(forms.Form):
    block_number = forms.CharField(required=False)
    room_number = forms.CharField(required=False)
    student_number = forms.CharField(required=False)
    cell_phone = forms.CharField(required=False)  
    residence_name = forms.ChoiceField(choices =RESIDENCE_CHOICE, required=False, label="", initial='Select Residence', 
                widget=forms.Select(attrs={
                'class': 'custom-select d-block w-100',
                'required': False,
                'id': 'residence_name'
                }))
    set_default_shipping = forms.BooleanField(required=False)
    use_default_shipping = forms.BooleanField(required=False)
    
    
    # shipping_country = CountryField(blank_label='(select country)').formfield(
    #     required=False,
    #     widget=CountrySelectWidget(attrs={
    #         'class': 'custom-select d-block w-100',
    #     }))
    # shipping_zip = forms.CharField(required=False)

    # billing_address = forms.CharField(required=False)
    # billing_address2 = forms.CharField(required=False)
    # billing_country = CountryField(blank_label='(select country)').formfield(
    #     required=False,
    #     widget=CountrySelectWidget(attrs={
    #         'class': 'custom-select d-block w-100',
    #     }))
    # billing_zip = forms.CharField(required=False)

    # same_billing_address = forms.BooleanField(required=False)
    # set_default_billing = forms.BooleanField(required=False)
    # use_default_billing = forms.BooleanField(required=False)

    payment_option = forms.ChoiceField(
        widget=forms.RadioSelect, choices=PAYMENT_CHOICES)
    delivery_option = forms.ChoiceField(
        widget=forms.RadioSelect, choices=DELIVERY_CHOICE)

class CouponForm(forms.Form):
    code = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Promo code',
        'aria-label': 'Recipient\'s username',
        'aria-describedby': 'basic-addon2'
    }))


class RefundForm(forms.Form):
    ref_code = forms.CharField()
    message = forms.CharField(widget=forms.Textarea(attrs={
        'rows': 4
    }))
    email = forms.EmailField()


class ItemCreateForm(forms.ModelForm):
    description = forms.CharField(widget=forms.Textarea(attrs={
        'rows': 4
    }))
    class Meta:
        model = Item
        fields = (
            'title',
            'description',
            'price',
            'discount_price',
            'available',
            'category',
        )


class ItemEditForm(forms.ModelForm):

    class Meta:
        model = Item
        fields = (
            'title',
            'description',
            'price',
            'discount_price',
            'available',
            'category',
        )


class OrderDetailForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ('being_delivered','received',)
        # being_delivered = forms.BooleanField(required=False) 
        # delivered = forms.BooleanField(required=False)