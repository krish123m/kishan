from decimal import Decimal
import razorpay
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib import messages
from app1.models import Category, Product, Cart,Checkout,OrderList


def home(request):
    return render(request,'home.html')

def create(request):
    if request.method == 'POST':
        name = request.POST['name']
        features = request.POST['features']
        price = request.POST['price']
        color = request.POST['color']
        rating = request.POST['rating']
        image = request.FILES['image']
        cat = request.POST['cat']

        cat = Category.objects.get(id=cat)

        s1 = Product.objects.create(
            name=name,
            features=features,
            price=price,
            color=color,
            rating=rating,
            image=image,
            cat=cat
        )
        return redirect('/minishop')

    Categories = Category.objects.all()

    return render(request, 'create.html', {'Categories': Categories})

def read(request):

    p1 = Product.objects.all()

    Categories = Category.objects.all()

    categoryid = request.GET.get('category')

    print(categoryid)

    if categoryid:

        p1 = Product.objects.filter(cat_id=categoryid)
    else:
        p1 = Product.objects.all()

    return render(request, 'read.html', {'p1': p1, 'Categories': Categories})


def singlepro(request,id):

    p1 = Product.objects.get(id=id)

    if request.method == "POST":
        name = request.POST['name']
        features = request.POST['features']
        price = request.POST['price']
        color = request.POST['color']
        rating = request.POST['rating']
        image = request.FILES['image']

        p1.name = name
        p1.features = features
        p1.price = price
        p1.color = color
        p1.rating = rating
        p1.image = image

        return redirect('/read')

    return render(request, 'singlepro.html', {'p1': p1})


@login_required(login_url='/login1')
def cart(request):
    user = request.user
    p2 = Cart.objects.filter(user=user)
    p_quantities = {}

    for q in p2:
        product = q.product
        if product in p_quantities:
            p_quantities[product] += q.quantity
        else:
            p_quantities[product] = q.quantity


    total_subtotal = float(sum(i.product.price * i.quantity for i in p2))

    tax_rate = 0.05
    tax_amount = total_subtotal * tax_rate

    total_total = total_subtotal + tax_amount

    context = {
        'p2': p2,
        'p_quantities': p_quantities,
        'total_subtotal': total_subtotal,
        'tax_amount': tax_amount,
        'total_total': total_total
    }
    return render(request, 'cart.html', context)


@login_required(login_url='/login1')
def addcart(request, id):
    user = request.user
    product = Product.objects.get(id=id)

    try:
        cart_item = Cart.objects.get(user=user, product=product)
        cart_item.quantity += 1
        cart_item.total = cart_item.price * cart_item.quantity
        cart_item.save()
        print(cart_item.quantity)
    except:
        Cart.objects.create(
            user=user,
            product=product,
            quantity=1,
            price=product.price,
            email=user.email,
            image=product.image,
            total=product.price
        )
    return redirect('/cart')

def changequantity(request,id):
    qu = Cart.objects.get(id=id)
    quantity = request.POST['quantity']
    print(quantity)
    if qu.quantity == 0:
        qu.delete()
        return redirect('/cart')
    else:
        qu.quantity = quantity
        qu.total = qu.price * int(quantity)
        qu.save()
        return redirect('/cart')


@login_required(login_url='/login1')
def billing(request):
    user = request.user
    p2 = Cart.objects.filter(user=user)
    p_quantities = {}

    for item in p2:
        product = item.product
        if product in p_quantities:
            p_quantities[product] += item.quantity
        else:
            p_quantities[product] = item.quantity

    subtotal = sum(Decimal(item.product.price) * item.quantity for item in p2)

    tax_rate = Decimal('0.10')
    tax_amount = subtotal * tax_rate
    total = subtotal + tax_amount

    shipping = Decimal('10')
    total_price = total + shipping

    if request.method == "POST":
        status = request.POST.get('status', 'pending')
        full_name = request.POST['full_name']
        email = request.POST['email']
        phone = request.POST['phone']
        address_line1 = request.POST['address_line1']
        address_line2 = request.POST['address_line2']
        city = request.POST['city']
        state = request.POST['state']
        country = request.POST['country']
        payment = request.POST.get('payment')


        if payment == 'razorpay':
            client = razorpay.Client(auth=('rzp_test_ytoQRUzHn3jtXL', 'Sc3eDMyJEuNfGzcf5r5eWiLz'))
            amount_in_paise = int(total_price * 100)
            razorpay_order = client.order.create({
                'amount': amount_in_paise,
                'currency': 'INR',
                'payment_capture': 1
            })
            s2 = Checkout.objects.create(
                user=user,
                full_name=full_name,
                email=email,
                phone=phone,
                address_line1=address_line1,
                address_line2=address_line2,
                city=city,
                state=state,
                country=country,
                total=total_price,
                payment="Razorpay",
                status="Pending",
                razorpay_order_id=razorpay_order['id']
            )
            p2.delete()
            context = {
                'p2': p2,
                'p_quantities': p_quantities,
                'total_subtotal': subtotal,
                'total': total,
                'cart': cart,
                'total_amount': total_price,
                'razorpay_order_id': razorpay_order['id'],
                'razorpay_key': 'rzp_test_ytoQRUzHn3jtXL',
                'currency': 'INR',
                'user':request.user
            }
            return render(request, 'billing.html', context)

        elif payment == 'cod':
            Checkout.objects.create(
                user=user,
                full_name=full_name,
                email=email,
                phone=phone,
                address_line1=address_line1,
                address_line2=address_line2,
                city=city,
                state=state,
                country=country,
                total=total_price,
                payment="COD",
                status="Pending"
            )
            OrderList.objects.create(
                user=user,
                name=full_name,
                email=email,
                number=phone,
                total_amount=total_price
            )
            p2.delete()
        return redirect('/billing')

    context = {
        'p2': p2,
        'p_quantities': p_quantities,
        'total_subtotal': subtotal,
        'tax_amount': tax_amount,
        'total': total,
        'cart': p2,
        'total_amount': total_price
    }
    return render(request, 'billing.html', context)


def deletecart(request,id):
    p2 = Cart.objects.get(id=id)
    p2.delete()
    return redirect('/cart')

def minishop(request):
    return render(request,'minishop.html')

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        email = request.POST['email']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']

        myuser = User.objects.create_user(username,email,pass1)
        myuser.first_name = firstname
        myuser.last_name = lastname
        myuser.save()
        messages.success(request,'your account has been successfully created.')

        return redirect('/login1')
    return render(request,'register.html')


def login1(request):
    if request.method == 'POST':
        username = request.POST['username']
        pass1 = request.POST['pass1']

        user = authenticate(username=username,password=pass1)
        if user is not None:
            login(request, user)
            fname = user.first_name
            return render(request,'minishop.html',{'fname':fname})
        else:
            messages.error(request,'Bed credentials!')
            return redirect('/minishop')
    return render(request,'login1.html')


def logout1(request):
    logout(request)
    messages.success(request, 'logged out successfully!')
    return redirect('/minishop')










