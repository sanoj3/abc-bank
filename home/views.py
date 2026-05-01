from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import Customer, Transaction
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from decimal import Decimal


def registration(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone_number = request.POST.get('phone_number')
        aadhaar_number = request.POST.get('aadhaar_number')

        if not all([email, password, first_name, last_name, phone_number, aadhaar_number]):
            messages.error(request, 'All fields are required')
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return redirect('register')

        if len(password) < 8:
            messages.error(request, 'Password must be at least 8 characters')
            return redirect('register')

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password
        )

        Customer.objects.create(
            user=user,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            aadhar_number=aadhaar_number
        )

        messages.success(request, 'Account created successfully')
        return redirect('login')

    return render(request, 'register.html', {'page': 'register'})


def login_user(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not email or not password:
            messages.error(request, 'Email and password required')
            return redirect('login')

        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful')
            return redirect('home')

        messages.error(request, 'Invalid email or password')
        return redirect('login')

    return render(request, 'login.html', {'page': 'login'})


@login_required
def home_page(request):
    customer = Customer.objects.filter(user=request.user).first()
    return render(request, 'home.html', {'customer': customer})


@login_required
def logout_page(request):
    logout(request)
    messages.success(request, 'Logged out successfully')
    return redirect('login')


@login_required
def profile_page(request):
    customer = Customer.objects.filter(user=request.user).first()
    return render(request, 'profile.html', {'customer': customer})


@login_required
def deposit_page(request):
    customer = Customer.objects.get(user=request.user)

    if request.method == 'POST':
        amount = request.POST.get('amount')

        if not amount:
            messages.error(request, 'Enter amount')
            return redirect('deposit')

        try:
            amount = Decimal(amount)
        except:
            messages.error(request, 'Invalid amount')
            return redirect('deposit')

        if amount <= 0:
            messages.error(request, 'Amount must be greater than 0')
            return redirect('deposit')

        customer.balance += amount
        customer.save()

        Transaction.objects.create(
            customer=customer,
            amount=amount,
            transaction_type='deposit',
            after_balance=customer.balance,
            description='Self deposit'
        )

        messages.success(request, 'Deposit successful')
        return redirect('home')

    return render(request, 'deposit.html', {'customer': customer})


@login_required
def withdraw_page(request):
    customer = Customer.objects.get(user=request.user)

    if request.method == 'POST':
        amount = request.POST.get('amount')

        try:
            amount = Decimal(amount)
        except:
            messages.error(request, 'Invalid amount')
            return redirect('withdraw')

        if amount <= 0:
            messages.error(request, 'Amount must be greater than 0')
            return redirect('withdraw')

        if amount > customer.balance:
            messages.error(request, 'Insufficient balance')
            return redirect('withdraw')

        customer.balance -= amount
        customer.save()

        Transaction.objects.create(
            customer=customer,
            amount=amount,
            transaction_type='withdraw',
            after_balance=customer.balance,
            description='Self withdraw'
        )

        messages.success(request, 'Withdraw successful')
        return redirect('home')

    return render(request, 'withdraw.html', {'customer': customer})

@login_required 
def transaction_history(request): 
    customer = Customer.objects.get(user=request.user) 
    transactions = Transaction.objects.filter(customer=customer).order_by('-created_at') 
    return render(request, 'transaction.html', { 'transactions' : transactions })


@login_required
def transfer_money(request):
    sender = Customer.objects.get(user=request.user)

    if request.method == 'POST':
        receiver_username = request.POST.get('receiver')
        amount = request.POST.get('amount')

        if not receiver_username or not amount:
            messages.error(request, 'All fields are required')
            return redirect('transfer')

        try:
            amount = Decimal(amount)
        except:
            messages.error(request, 'Invalid amount')
            return redirect('transfer')

        if amount <= 0:
            messages.error(request, 'Amount must be greater than zero')
            return redirect('transfer')

        try:
            receiver_user = User.objects.get(username=receiver_username)
            receiver = Customer.objects.get(user=receiver_user)
        except:
            messages.error(request, 'Receiver not found')
            return redirect('transfer')

        if sender == receiver:
            messages.error(request, 'Cannot send money to yourself')
            return redirect('transfer')

        if amount > sender.balance:
            messages.error(request, 'Insufficient balance')
            return redirect('transfer')

        sender.balance -= amount
        receiver.balance += amount
        sender.save()
        receiver.save()

        Transaction.objects.create(
            customer=sender,
            amount=amount,
            transaction_type='withdraw',
            after_balance=sender.balance,
            description=f"Sent to {receiver.first_name} {receiver.last_name}"
        )

        Transaction.objects.create(
            customer=receiver,
            amount=amount,
            transaction_type='deposit',
            after_balance=receiver.balance,
            description=f"Received from {sender.first_name} {sender.last_name}"
        )

        messages.success(request, 'Money sent successfully')
        return redirect('home')

    return render(request, 'transfer.html', {'customer': sender})


@login_required
def edit_profile(request):
    customer = Customer.objects.get(user=request.user)

    if request.method == "POST":
        customer.first_name = request.POST.get('first_name')
        customer.last_name = request.POST.get('last_name')
        customer.phone_number = request.POST.get('phone_number')

        if 'profile_pic' in request.FILES:
            customer.profile_pic = request.FILES['profile_pic']

        customer.save()

        user = request.user
        user.first_name = customer.first_name
        user.last_name = customer.last_name
        user.save()

        messages.success(request, 'Profile updated successfully')  # ✅ FIXED
        return redirect('profile')

    return render(request, 'edit_profile.html', {'customer': customer})