from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Address, UserProfile
from .forms import UserRegistrationForm, UserLoginForm, AddressForm, UserUpdateForm, ProfileUpdateForm
from orders.models import Order


def user_register(request):
    if request.user.is_authenticated:
        return redirect('core:home')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to Buyzone, {user.first_name}! Your account was created successfully.")
            next_url = request.GET.get('next') or 'core:home'
            return redirect(next_url)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


def user_login(request):
    if request.user.is_authenticated:
        return redirect('core:home')

    next_url = request.GET.get('next', '')
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            return redirect(request.POST.get('next') or 'core:home')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = UserLoginForm()

    return render(request, 'accounts/login.html', {'form': form, 'next': next_url})


def user_logout(request):
    logout(request)
    messages.info(request, "You have been logged out safely.")
    return redirect('core:home')


@login_required
def profile(request):
    recent_orders = Order.objects.filter(user=request.user).order_by('-created_at')[:5]
    addresses = Address.objects.filter(user=request.user)

    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, "Your profile has been updated successfully!")
            return redirect('accounts:profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form,
        'recent_orders': recent_orders,
        'addresses': addresses,
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def address_book(request):
    addresses = Address.objects.filter(user=request.user)
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            if not addresses.exists():
                address.is_default = True
            address.save()
            messages.success(request, "New address added to your address book.")
            return redirect('accounts:address_book')
    else:
        form = AddressForm()

    return render(request, 'accounts/address_book.html', {'addresses': addresses, 'form': form})


@login_required
def address_edit(request, pk):
    address = get_object_or_404(Address, pk=pk, user=request.user)
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            messages.success(request, "Address updated successfully.")
            return redirect('accounts:address_book')
    else:
        form = AddressForm(instance=address)

    return render(request, 'accounts/address_edit.html', {'form': form, 'address': address})


@login_required
def address_delete(request, pk):
    address = get_object_or_404(Address, pk=pk, user=request.user)
    address.delete()
    messages.success(request, "Address removed successfully.")
    return redirect('accounts:address_book')


@login_required
def address_set_default(request, pk):
    address = get_object_or_404(Address, pk=pk, user=request.user)
    Address.objects.filter(user=request.user).update(is_default=False)
    address.is_default = True
    address.save()
    messages.success(request, f"Default delivery address updated to {address.full_name}.")
    return redirect('accounts:address_book')
