from django.shortcuts import render, redirect, get_object_or_404
import random
import pytz
from datetime import datetime
import string, json
import requests
from itertools import chain
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, View, RedirectView
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User, Group
from django.http import HttpResponse, HttpResponseRedirect
from webpush import send_user_notification
#from django.contrib.gis.utils import GeoIP

# Create your views here.
from .models import Item, Images, Order, OrderItem, Address, Payment, VoucherAccount, VoucherLog
from .forms import ItemCreateForm, ItemEditForm, CheckoutForm, CouponForm, OrderDetailForm, IDForm, SearchForm, VoucherForm
from django.forms import modelformset_factory

# REST FRAMEWORK
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions


def is_valid_form(values):
    valid = True
    for field in values:
        if field == '':
            valid = False
    return valid

def is_idform_valid(values):
    valid = True
    for field in values:
        if field == '':
            valid = False
    return valid


def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))

def products(request):
    context = {
        'object_list': Item.objects.all()
    }
    return render(request, "home.html", context)

class HomeView(ListView):
    model = Item
    template_name = 'home.html'
    paginate_by = 12
    ordering = ['pk']

    def get_context_data(self, *args, **kwargs):
        prod_ = Item.objects.all().order_by('pk')
        item = []
        context = super().get_context_data(*args, **kwargs)
        if self.request.user.is_authenticated:
            order = Order.objects.filter(user=self.request.user, ordered=False)
            if order.exists():
                order = order[0]
                for i in order.item.all():
                    item.append(i.item)
        context['cart'] = item        
        return context  

class SearchView(ListView): 
    model = Item
    template_name = 'home.html'
    paginate_by = 12
    ordering = ['pk']

    def get_context_data(self, *args, **kwargs):
        prod_ = Item.objects.all().order_by('pk')
        item = []
        context = super().get_context_data(*args, **kwargs)
        if self.request.user.is_authenticated:
            order = Order.objects.filter(user=self.request.user, ordered=False)
            if order.exists():
                order = order[0]
                for i in order.item.all():
                    item.append(i.item)
        context['cart'] = item        
        return context  

    def get_queryset(self):
        request = self.request
        query = request.GET.get('q', None)
        if len(query) > 2:
            blog_results = Item.objects.filter(title__icontains=query)
            queryset_chain = chain(blog_results)
            qs = sorted(queryset_chain, key=lambda instance: instance.pk,
                        reverse=True)
            return qs
        return Item.objects.none() 


class ViewVoucherAccount(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        u = request.user
        voucher_account = VoucherAccount.objects.get(user=u)
        order = Order.objects.filter(user=u)
        context = {
            'voucher_account': voucher_account,
            'order': order,
        }

        return render(self.request, 'view_voucher.html', context)

class SearchVoucher(UserPassesTestMixin, LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        context = {
            'response': ""
        }
        return render(request, 'voucher.html')
    
    def post(self, request, *args, **kwargs):
        request = self.request       
        query = request.POST.get('q', None)
        account = VoucherAccount.objects.filter(user__username__icontains=query)

        context = {
            'accounts':account,
            'response': "Not Found, Please Check Username"
        }
        return render(request, 'voucher.html', context)
              
    def test_func(self):
        staffs = Group.objects.get(name="Caf Staff")
        is_permissioned = False
        if self.request.user in staffs.user_set.all() or self.request.user.is_superuser:
            is_permissioned = True
        return is_permissioned

class AddVoucher(UserPassesTestMixin, LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        username = kwargs['username']
        user = User.objects.get(username=username)
        voucher_account = VoucherAccount.objects.get(user=user)
        form = VoucherForm()
        order = Order.objects.filter(user__exact=user)

        context = {
            'form': form,
            'voucher_account': voucher_account,
            'order': order,
            'username': username,
        }
        return render(request, 'addvoucher.html', context)
    
    def post(self, request, *args, **kwargs):
        username = kwargs['username']
        user = User.objects.get(username=username)
        voucher_account = VoucherAccount.objects.get(user=user)
        form = VoucherForm(self.request.POST or None)
        order = Order.objects.filter(user__exact=user)
        if request.method == 'POST':
            if form.is_valid():
                amount = form.cleaned_data.get('amount')
                voucher_account.amount += amount
                voucher_account.save()
                log_transaction = VoucherLog.objects.create(user=request.user, amount=amount, loaded_account=user)
                log_transaction.save()
                messages.success(request, f"R{amount} has been added to {username} voucher balance")
                return redirect("core:load-voucher", username=username)
            else:
                messages.warning(request, 'Invalid Form')
                return redirect('core:home')

        context = {
            'form': form,
            'voucher_account': voucher_account,
            'order': order,
            'username': username,
        }
        return render(request, 'addvoucher.html', context)        

    def test_func(self):
        staffs = Group.objects.get(name="Caf Staff")
        is_permissioned = False
        if self.request.user in staffs.user_set.all() or self.request.user.is_superuser:
            is_permissioned = True
        return is_permissioned

class AddItemView(UserPassesTestMixin, View):
    
    def get(self, request):
        ImageFormset = modelformset_factory(Images, fields=('image',), extra=4)
        formset = ImageFormset(queryset=Images.objects.none())
        form = ItemCreateForm()
        context = {
            'form': form,
            'formset': formset,
            'page': 'A',
        }
        return render(request, 'create_item.html', context)

    def post(self, request):
        ImageFormset = modelformset_factory(Images, fields=('image',), extra=4)
        if request.method == 'POST':
            form = ItemCreateForm(request.POST, request.FILES or None)
            formset = ImageFormset(request.POST or None, request.FILES or None)
            
            if form.is_valid() and formset.is_valid():
                post = form.save(commit=False)
                post.user = request.user
                post.save()

                for f in formset:
                    try:
                        photo = Images(item=post, image=f.cleaned_data['image'])
                        photo.save()
                    except Exception as e:
                        pass
                return redirect('core:home')
        else:
            form = ItemCreateForm()
            formset = ImageFormset(queryset=Images.objects.none())
        context = {
            'form': form,
            'formset': formset, 
        }
        return render(request, 'create_item.html', context)

    def test_func(self):
        staffs = Group.objects.get(name="Caf Staff")
        is_permissioned = False
        if self.request.user in staffs.user_set.all() or self.request.user.is_superuser:
            is_permissioned = True
        return is_permissioned

class ItemDetailView(DetailView):
    model = Item
    template_name = 'product.html'

    def get(self, *args, **kwargs):
        slug = self.kwargs['slug']
        item = Item.objects.get(slug=slug)
        # form = CartForm()
        context = {
            'object': item,
           # 'form': form
        }
        return render(self.request, 'product.html', context)

    def post(self, *args, **kwargs):        
        slug = self.kwargs['slug']
        request = self.request
        if request.user.is_authenticated:
            item = get_object_or_404(Item, slug=slug)
            if request.method == 'POST':
                # size = form.cleaned_data.get('size')
                order_item, created = OrderItem.objects.get_or_create(item=item, 
                                        user=request.user, ordered=False)
                order_qs = Order.objects.filter(user__exact=request.user, ordered=False)            
                if order_qs.exists():
                    order = order_qs[0]
                    if order_item in order.item.all():
                        order_item.quantity += 1
                        order_item.save()
                        messages.info(request, "This item item quanity was updated.")
                        return redirect("core:order-summary")
                    
                    else:
                        order.item.add(order_item)
                        messages.info(request,"This item was added to your cart.")
                        return redirect("core:order-summary")
                else:
                    order_date = timezone.now()
                    ref = create_ref_code()
                    order = Order.objects.create(user=request.user, ordered_date=order_date, ref_code=ref)
                    order.item.add(order_item)
                    messages.info(request, "This item was added to your cart.")
                    return redirect("core:order-summary")
            else:
                return redirect('core:order-summary')
        else:
            messages.info(request, "You need to be signed in")
            redirect("account_login")

class EditItemView(UserPassesTestMixin, View):
    def get(self, request, *args, **kwargs):
        slug = kwargs['slug']
        item = get_object_or_404(Item, slug=slug)
        form = ItemEditForm(instance=item)
        ImageFormset = modelformset_factory(Images, fields=('image',), extra=4, max_num=4)
        formset = ImageFormset(queryset=Images.objects.filter(item=item))
        context = {
            'form': form,
            'item': item,
            'formset': formset,
            'page': 'E'
        }
        return render(request, 'create_item.html', context)


    def test_func(self):
        staffs = Group.objects.get(name="Caf Staff")
        is_permissioned = False
        if self.request.user in staffs.user_set.all() or self.request.user.is_superuser:
            is_permissioned = True
        return is_permissioned

class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order
            }
            return render(self.request, 'order_summary.html', context)

        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("/")

@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(item=item, user=request.user,ordered=False)
    order_qs = Order.objects.filter(user=request.user, ordered=False)

    if order_qs.exists():
        order = order_qs[0]
        if order.item.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "This item item quanity was updated.")
            return redirect("core:order-summary")
            # return redirect("core:product", slug=slug)
        
        else:
            order.item.add(order_item)
            messages.info(request,"This item was added to your cart.")
            return redirect("core:order-summary")
            #  return redirect("core:product", slug=slug)

    else:
        order_date = timezone.now()
        ref = create_ref_code()
        order = Order.objects.create(user=request.user, ordered_date=order_date, ref_code=ref)
        order.item.add(order_item)
        messages.info(request, "This item was added to your cart.")
        return redirect("core:order-summary")
        # return redirect("core:product", slug=slug)


@login_required
def delete_from_cart(request, slug):  
    item = get_object_or_404(Item, slug=slug)   
    order_qs = Order.objects.filter(user=request.user, ordered=False)

    if order_qs.exists():
        order = order_qs[0]
        if order.item.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(item=item, user=request.user,ordered=False)
            for order_it in order_item:
                order.item.remove(order_it)
            messages.info(request, "This item was removed to your cart.")
            # return redirect("core:product", slug=slug)
            return redirect("core:order-summary")

        else:
            # add a messge saying the order was not in the cart
            messages.info(request, "This item was not in your cart.")
            # return redirect("core:order-summary")            
            return redirect("core:product", slug=slug) 
    else:
        # add a message saying the doesnt have an order
        messages.info(request, "You do not have an active order.")
        return redirect("core:product", slug=slug)


@login_required
def remove_from_cart(request, slug):  
    item = get_object_or_404(Item, slug=slug)   
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    order_item = OrderItem.objects.get(item=item, user=request.user,ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order_item in order.item.all():            
            order.item.remove(order_item)
            messages.info(request, "This item was removed to your cart.")
            # return redirect("core:product", slug=slug)
            return redirect("core:order-summary")

        else:
            # add a messge saying the order was not in the cart
            messages.info(request, "This item was not in your cart.")
            # return redirect("core:order-summary")            
            return redirect("core:product", slug=slug) 
    else:
        # add a message saying the doesnt have an order
        messages.info(request, "You do not have an active order.")
        return redirect("core:product", slug=slug)
            

@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    order_item = OrderItem.objects.get(
                item=item,
                user=request.user,
                ordered=False,
            )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order_item in order.item.all():
        # if order.item.filter(item__slug=item.slug).exists():
            """order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]"""
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.item.remove(order_item)
            messages.info(request, "This item quantity was updated.")
            return redirect("core:order-summary")


@login_required
def add_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    order_item = OrderItem.objects.get(
        item=item,
        user=request.user,
        ordered=False,
    )    
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order_item in order.item.all():
            if order_item.quantity:
                order_item.quantity += 1
                order_item.save()
            else:
                order.item.remove(order_item)
            messages.info(request, "This item quantity was updated.")
            return redirect("core:order-summary")


class CategoryListView(ListView):
    paginate_by = 12
    template_name = 'home.html'
  
    def get_context_data(self, **kwargs):
        category = self.kwargs['cat']
        context = super(CategoryListView, self).get_context_data(**kwargs)
        context['page'] = category
        return context

    def get_queryset(self):
        category = self.kwargs['cat']
        qs = Item.objects.filter(category=category).order_by('-pk')
        return qs


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order
            }
            return render(self.request, 'order_summary.html', context)

        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("/")


class CheckOutView(LoginRequiredMixin, View):

    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)    
            form = CheckoutForm()
            idform = IDForm()
            context = {
                'form': form,
                'idform': idform,
                'couponform': CouponForm(),
                'order': order,
                'DISPLAY_COUPON_FORM': False,
            }
            shipping_address_qs = Address.objects.filter(
                user=self.request.user,
                default=True
            )

            if shipping_address_qs.exists():
                context.update({'default_shipping_address': shipping_address_qs[0]})

            return render(self.request, "cash_checkout.html", context)
        except ObjectDoesNotExist:
            messages.info(self.request, "You do not have an active order")
            return redirect('core:checkout')

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        idform = IDForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid() and idform.is_valid():
                use_default_shipping = form.cleaned_data.get(
                    'use_default_shipping')
                delivery_option = form.cleaned_data.get('delivery_option')
                if delivery_option == 'RD':
                    if use_default_shipping:
                        address_qs = Address.objects.filter(
                            user=self.request.user,
                            address_type='S',
                            default=True
                        )
                        if address_qs.exists():
                            shipping_address = address_qs[0]
                            order.delivery_option = delivery_option
                            order.shipping_address = shipping_address
                            order.service_charge = 10
                            order.save()
                        else:
                            messages.info(
                                self.request, "No default shipping address available")
                            return redirect('core:checkout')
                    else:
                        block_number = form.cleaned_data.get(
                            'block_number')
                        room_number = form.cleaned_data.get(
                            'room_number')
                        student_number = form.cleaned_data.get(
                            'student_number')
                        cell_phone = form.cleaned_data.get('cell_phone')
                        residence_name = form.cleaned_data.get('residence_name')

                        if is_valid_form([block_number, room_number, student_number, cell_phone, residence_name]):
                            shipping_address = Address(
                                user=self.request.user,
                                block_number=block_number,
                                room_number=room_number,
                                residence_name=residence_name,
                                cell_phone = cell_phone,
                                student_number = student_number,
                                address_type='S'
                            )
                            shipping_address.save()

                            order.shipping_address = shipping_address
                            order.delivery_option = delivery_option
                            order.student_number = student_number
                            order.service_charge = 10
                            order.save()

                            set_default_shipping = form.cleaned_data.get(
                                'set_default_shipping')
                            if set_default_shipping:
                                shipping_address.default = True
                                shipping_address.save()

                        else:
                            messages.info(
                                self.request, "Please fill in the required delivery address fields")
                            return redirect('core:checkout')

                elif delivery_option == 'PU':
                    id_ = idform.cleaned_data.get('idform')
                    if is_idform_valid([id_]):
                        order.delivery_option = delivery_option
                        order.student_number = id_
                        order.service_charge = 5
                        order.save()
                    else:
                        messages.info(self.request, "Please fill in the required student/id number field if you'll like to pick up your order at the caf")
                        # return render(self.request, 'cash_checkout.html')
                        return redirect('core:checkout')

                payment_option = form.cleaned_data.get('payment_option')
                if payment_option == 'Card':
                    return redirect('core:card-payment')
                elif payment_option == 'Voucher':
                    return redirect('core:voucher-payment')
                else:
                    messages.warning(
                        self.request, "Invalid payment option selected")
                    return redirect('core:checkout')
            else:
                messages.info(self.request, 'Please fill in required fields')
                return redirect('core:checkout')
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("core:order-summary")


class CashPaymentView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        if order.shipping_address:
            context = {
                'order': order,
                'DISPLAY_COUPON_FORM': False,
                'method': 'Cash'
            }        
            return render(self.request, "payment.html", context)
        else:
            messages.info(self.request, "You have not added a shipping address")
            return redirect('core:checkout')

    def post(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        payment_option  = self.kwargs['payment_option']
        amount = int(order.get_total() * 100)
        
        try:
            payment = Payment()
            payment.user = self.request.user
            payment.amount_gross = order.get_total()
            payment.payment_option = payment_option
            payment.ref_code = order.ref_code
            payment.save()

            # assign the payment to the order

            order_items = order.item.all()
            order_items.update(ordered=True)

            for item in order_items:
                item.save()

            order.ordered = True
            order.payment = payment
            order.save()

            messages.success(self.request, "Your order was successful!")
            return redirect("/")

        except Exception as e:
            messages.warning(
                self.request, "A serious error occurred. We have been notifed.")
            return redirect("/")


class ProfileSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        order_item = []
        order = Order.objects.filter(user__exact=self.request.user, ordered=True)
        for order in order.all():
            for item in order.item.all():
                order_item.append(item)

        context = {
            'order': Order.objects.filter(user__exact=self.request.user, ordered=True).all(),
            'obejct': order_item,
        }
        return render(self.request, 'profile.html', context)


class OrderDetailView(UserPassesTestMixin, View):
    def get(self, *args, **kwargs):
        ref = self.kwargs['ref']
        try:
            order_item = []
            
            order = Order.objects.get(ref_code=ref, ordered=True)
            form = OrderDetailForm(instance=order)
            for item in order.item.all():
                order_item.append(item)
            context = {
                'object': order,
                'order_': order_item,
                'length': len(order_item),
                'form': form,
            }
            return render(self.request, 'order_detail.html', context)

        except ObjectDoesNotExist:
            messages.warning(self.request, "Invalid Link")
            return redirect("/")

    def post(self, *args, **kwargs):
        request = self.request
        if request.method == 'POST':
            ref = self.kwargs['ref']
            order = Order.objects.get(ref_code=ref)
            form = OrderDetailForm(request.POST)
            if form.is_valid():
                b_d = form.cleaned_data['being_delivered']
                received = form.cleaned_data['received']
                
                order.being_delivered = b_d
                if received:
                    order.being_delivered = received
                    order.received = received
                order.save()
                return redirect('core:orders')

    def test_func(self):
        staffs = Group.objects.get(name="Caf Staff")
        is_permissioned = False
        if self.request.user in staffs.user_set.all() or self.request.user.is_superuser:
            is_permissioned = True
        return is_permissioned


class OrderListView(UserPassesTestMixin, View):
    def get(self, *args, **kwargs):
        try:
            form = SearchForm()
            order = Order.objects.filter(ordered=True).order_by('-pk')
            context = {
                'object': order,
                'form': form
            }
            return render(self.request, 'order.html', context)

        except ObjectDoesNotExist:
            messages.warning(self.request, "No Orders Have Been Made")
            return redirect("/")

    def post(self, *args, **kwargs):
        if self.request.method == 'POST':
            form = SearchForm(self.request.POST, self.request.FILES or None)
            ID = form['searchfield'].data
            order = Order.objects.filter(ordered=True, student_number=ID).order_by('-pk')
            context = {
                'object': order,
                'form': form,
            }
            return render(self.request, 'order.html', context)
        else:
            messages.warning(self.request, "Invalid Request")
            return redirect('/')


    def test_func(self):
        staffs = Group.objects.get(name="Caf Staff")
        is_permissioned = False
        if self.request.user in staffs.user_set.all() or self.request.user.is_superuser:
            is_permissioned = True
        return is_permissioned

class ProcessPaymentView(LoginRequiredMixin, View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        if request.method == 'POST':
            form = request.POST.dict()
            m_paymemt_id = form['m_payment_id']
            pf = form['pf_payment_id']
            item_name = form['item_name']
            amount_gross = form['amount_gross']
            amount_fee = form['amount_fee']
            amount_net = form['amount_net']
            signature = form['signature']
            MID = form['merchant_id']
            email = form['email_address']
            order = Order.objects.get(ref_code=item_name)

            # Validate Response
            res = requests.post('https://sandbox.payfast.co.za/eng/query/validate'
                                , data={'pf_payment_id': pf, 'signature':signature,
                                        'merchant_id': MID, })
            if res.text == 'VALID':
                # create the payment
                user = User.objects.get(email=email)
                payment = Payment()
                payment.user = user
                payment.amount_gross = amount_gross
                payment.amount_fee = amount_fee
                payment.amount_net = amount_net
                payment.payment_option = 'Card'
                payment.signature = signature
                payment.MID = MID
                payment.pf = pf
                payment.ref_code = item_name
                payment.save()
                order.ordered = True
                order.payment = payment
                order_items = order.item.all()
                order_items.update(ordered=True)
                for item in order_items:
                    item.save()
                order.save()
                user_ = User.objects.get(username='lekan')
                payload = {"head": "Order Alert!", "body": "New Order Alert", 
                            "icon": "https://i.imgur.com/dRDxiCQ.png", "url": f"https://35bd7a4671dd.ngrok.io/order/{item_name}/"}
                send_user_notification(user=user_, payload=payload, ttl=1000)
                messages.success(self.request, 'Payment Successful')                
                return render(self.request, 'home.html')
            else:
                messages.warning(self.request, 'Payment Unsuccessful')
                return render(self.request, 'home.html')
        return super(ProcessPaymentView, self).dispatch(request, *args, **kwargs)

    def post(self, *args, **kwargs):
        request = self.request
        if request.method == 'POST':
            m_paymemt_id = request.form['m_payment_id']
            pf = request.form['pf_payment_id']
            item_name = request.form['item_name']
            amount_gross = request.form['amount_gross']
            amount_fee = request.form['amount_fee']
            amount_net = request.form['amount_net']
            signature = request.form['signature']
            MID = request.form['merchant_id']
            order = Order.objects.get(ref_code=item_name)

            # Validate Response
            res = requests.post('https://sandbox.payfast.co.za/eng/query/validate'
                                , data={'pf_payment_id': pf, 'signature':signature,
                                        'merchant_id': MID, })
            if res.text == 'VALID':
                # create the payment
                payment = Payment()
                payment.user = self.request.user
                payment.amount_gross = amount_gross
                payment.amount_fee = amount_fee
                payment.amount_net = amount_net
                payment.payment_option = 'Card'
                payment.signature = signature
                payment.MID = MID
                payment.pf = pf
                payment.ref_code = item_name
                payment.save()
                order.ordered = True
                order.payment = payment
                order_items = order.item.all()
                order_items.update(ordered=True)
                for item in order_items:
                    item.save()
                order.save()
                user_ = User.objects.get(username='lekan')
                payload = {"head": "Order Alert!", "body": "New Order Alert", 
                            "icon": "https://i.imgur.com/dRDxiCQ.png", "url": f"https://35bd7a4671dd.ngrok.io/order/{item_name}/"}
                # payload = {"head": "Welcome!", "body": "Hello World"}
                send_user_notification(user=user_, payload=payload, ttl=1000)
                messages.success(self.request, 'Payment Successful, Order Completed')
                return redirect('core:home')
            else:
                messages.warning(self.request, 'Payment Unsuccessful')
                return redirect('core:home')
        else:
            messages.info(request, 'Only POST Method Allowed')
            return redirect("/")

class CardPaymentView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        user = self.request.user
        is_closed = False
        service_charge = order.service_charge
        closed_hour = [1,2,3,4,5,6,7,22,24]
        sa_time = datetime.now(pytz.timezone('Africa/Johannesburg'))
        if sa_time.hour in closed_hour:
            is_closed = True

        if service_charge == 5 or 10:                
            if order.delivery_option == 'RD':
                if order.shipping_address:
                    context = {
                        'order': order,
                        'DISPLAY_COUPON_FORM': False,
                        'method': 'Card',
                        'is_closed': is_closed,
                        'service_charge': service_charge,
                        'user': user
                    }        
                    return render(self.request, "payment.html", context)
                else:
                    messages.info(self.request, "You have not added a shipping address")
                    return redirect('core:checkout')
            elif order.delivery_option == 'PU':
                context = {
                    'order': order,
                    'DISPLAY_COUPON_FORM': False,
                    'method': 'Card',
                    'is_closed': is_closed,
                    'service_charge': service_charge,
                    'user': user        
                    }
                return render(self.request, "payment.html", context)
            else:
                messages.info(self.request, "Please select a delivery option")
                return redirect('core:checkout')

        return render(self.request, 'home.html')

class VoucherPaymentView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        user = self.request.user
        account = VoucherAccount.objects.get(user=self.request.user)
        is_closed = False
        balance = False
        service_charge = order.service_charge
        closed_hour = [1,2,3,4,5,6,7,23,24]
        sa_time = datetime.now(pytz.timezone('Africa/Johannesburg'))
        if sa_time.hour in closed_hour:
            is_closed = True
        if (account.amount - order.get_total_quote()) >= 0:
            balance = True

        if service_charge == 5 or 10:                
            if order.delivery_option == 'RD':
                if order.shipping_address:
                    context = {
                        'order': order,
                        'DISPLAY_COUPON_FORM': False,
                        'method': 'Voucher',
                        'account': account,
                        'balance': balance,
                        'is_closed': is_closed,
                        'service_charge': service_charge,
                        'user': user
                    }        
                    return render(self.request, "payment.html", context)
                else:
                    messages.info(self.request, "You have not added a shipping address")
                    return redirect('core:checkout')
            elif order.delivery_option == 'PU':
                context = {
                    'order': order,
                    'DISPLAY_COUPON_FORM': False,
                    'method': 'Voucher',
                    'account': account,
                    'balance': balance,
                    'is_closed': is_closed,
                    'service_charge': service_charge,
                    'user': user        
                    }
                return render(self.request, "payment.html", context)
            else:
                messages.info(self.request, "Please select a delivery option")
                return redirect('core:checkout')

        return render(self.request, 'home.html')    
    
    def post(self, *args, **kwargs):
        if self.request.method == 'POST':
            order = Order.objects.get(user=self.request.user, ordered=False)
            user = self.request.user
            account = VoucherAccount.objects.get(user=self.request.user)
            is_closed = False
            balance = False
            service_charge = order.service_charge
            closed_hour = [1,2,3,4,5,6,7,22,23,24]
            sa_time = datetime.now(pytz.timezone('Africa/Johannesburg'))
            if sa_time.hour in closed_hour:
                is_closed = True
            if (account.amount - order.get_total_quote()) >= 0:
                balance = True


            if balance:
                if service_charge == 5 or 10:                
                    if order.delivery_option == 'RD':
                        if order.shipping_address:
                            account.amount -= order.get_total_quote()
                            account.save()
                            payment = Payment()
                            payment.user = user
                            payment.amount_gross = order.get_total_quote()
                            payment.amount_fee = order.service_charge
                            payment.amount_net = order.get_total()
                            payment.payment_option = 'Voucher'
                            payment.ref_code = order.ref_code
                            payment.save()
                            order.ordered = True
                            order.payment = payment
                            order_items = order.item.all()
                            order_items.update(ordered=True)
                            for item in order_items:
                                item.save()
                            order.save() 
                            user_ = User.objects.get(username='lekan')
                            payload = {"head": "Order Alert!", "body": "New Order Alert", 
                                        "icon": "https://i.imgur.com/dRDxiCQ.png", "url": f"https://35bd7a4671dd.ngrok.io/order/{order.ref_code}/"}
                            # payload = {"head": "Welcome!", "body": "Hello World"}
                            send_user_notification(user=user_, payload=payload, ttl=1000)
                            messages.success(self.request, 'Payment Successful, Order Completed')
                            return redirect('core:home')
                        else:
                            messages.info(self.request, "You have not added a shipping address")
                            return redirect('core:checkout')
                    elif order.delivery_option == 'PU':
                        account.amount -= order.get_total_quote()
                        account.save()
                        payment = Payment()
                        payment.user = user
                        payment.amount_gross = order.get_total_quote()
                        payment.amount_fee = order.service_charge
                        payment.amount_net = order.get_total()
                        payment.payment_option = 'Voucher'
                        payment.ref_code = order.ref_code
                        payment.save()
                        order.ordered = True
                        order.payment = payment
                        order_items = order.item.all()
                        order_items.update(ordered=True)
                        for item in order_items:
                            item.save()
                        order.save() 
                        user_ = User.objects.get(username='lekan')
                        payload = {"head": "Order Alert!", "body": "New Order Alert", 
                                    "icon": "https://i.imgur.com/dRDxiCQ.png", "url": f"https://35bd7a4671dd.ngrok.io/order/{order.ref_code}/"}
                        send_user_notification(user=user_, payload=payload, ttl=1000)
                        messages.success(self.request, 'Payment Successful, Order Completed')
                        return redirect('core:home')
                    else:
                        messages.info(self.request, "Please select a delivery option")
                        return redirect('core:checkout')
                return render(self.request, 'home.html')
            else:
                messages.warning(self.request, 'Insufficient Voucher Balance')
                render(self.request, 'home.html')
        else:
            return render(self.request, 'home.html')        

class CardPaymentSucessView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        messages.success(self.request, 'Payment Successful')
        return redirect('core:home')

class CardPaymentCancelView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        messages.info(self.request, 'Payment Unsuccessful')
        return redirect('core:home')

@login_required
def add_to_cart_json(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(item=item, user=request.user,ordered=False)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    cart = False
    count = 0
    if order_qs.exists():
        order = order_qs[0]
        if order.item.filter(item__slug=item.slug).exists():
            order.item.remove(order_item)
            order_item.save()
            count = order.item.count()
            cart = False            
            context = {
                'cart': cart,
                'count': count
            }
            return HttpResponse(json.dumps(context), content_type="application/json")

        else:
            order.item.add(order_item)
            cart = True
            count = order.item.count()
            context = {
                'cart': cart,
                'count': count
            }
            return HttpResponse(json.dumps(context), content_type="application/json")

    else:
        order_date = timezone.now()
        ref = create_ref_code()
        order = Order.objects.create(user=request.user, ordered_date=order_date, ref_code=ref)
        order.item.add(order_item)
        cart = True
        count = order.item.count()
        context = {
            'cart': cart,
            'count': count
        }
        return HttpResponse(json.dumps(context), content_type="application/json")
 