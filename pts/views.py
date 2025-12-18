from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from .models import Drug, Stock, Transaction
from .forms import DrugForm, TransactionForm
from datetime import date

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Logged in successfully.')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'pts/login.html')

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'Logged out successfully.')
    return redirect('login')

@login_required
def dashboard(request):
    low_stock = Stock.objects.filter(quantity__lt=10)
    expired_drugs = Drug.objects.filter(expiry_date__lt=date.today())
    transactions = Transaction.objects.order_by('-date')[:20]  # Last 20 transactions
    context = {
        'low_stock': low_stock,
        'expired_drugs': expired_drugs,
        'transactions': transactions,
    }
    return render(request, 'pts/dashboard.html', context)

@login_required
def stock_list(request):
    stocks = Stock.objects.all()
    return render(request, 'pts/stock_list.html', {'stocks': stocks})

@login_required
def drug_list(request):
    drugs = Drug.objects.all()
    return render(request, 'pts/drug_list.html', {'drugs': drugs})

@login_required
def drug_create(request):
    if not request.user.is_superuser:
        raise PermissionDenied("Only admins can create drugs.")
    if request.method == 'POST':
        form = DrugForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Drug added successfully.')
            return redirect('drug_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = DrugForm()
    return render(request, 'pts/drug_form.html', {'form': form, 'title': 'Create Drug'})

@login_required
def drug_update(request, pk):
    if not request.user.is_superuser:
        raise PermissionDenied("Only admins can update drugs.")
    drug = get_object_or_404(Drug, pk=pk)
    if request.method == 'POST':
        form = DrugForm(request.POST, instance=drug)
        if form.is_valid():
            form.save()
            messages.success(request, 'Drug updated successfully.')
            return redirect('drug_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = DrugForm(instance=drug)
    return render(request, 'pts/drug_form.html', {'form': form, 'title': 'Update Drug'})

@login_required
def drug_delete(request, pk):
    if not request.user.is_superuser:
        raise PermissionDenied("Only admins can delete drugs.")
    drug = get_object_or_404(Drug, pk=pk)
    if request.method == 'POST':
        drug.delete()
        messages.success(request, 'Drug deleted successfully.')
        return redirect('drug_list')
    return render(request, 'pts/drug_confirm_delete.html', {'drug': drug})

@login_required
def transaction_create(request):
    if not (request.user.is_staff or request.user.is_superuser):
        raise PermissionDenied("Only staff or admins can create transactions.")
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            try:
                transaction.save()
                messages.success(request, 'Transaction recorded successfully.')
                return redirect('dashboard')
            except ValidationError as e:
                messages.error(request, str(e))
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = TransactionForm()
    return render(request, 'pts/transaction_form.html', {'form': form})
