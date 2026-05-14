from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Max, OuterRef, Subquery
from .forms import RegisterForm, ItemForm
from .models import Item, Message

def home(request):
    query = request.GET.get('q')
    item_type = request.GET.get('type')
    items = Item.objects.filter(status='active').order_by('-created_at')

    if query:
        items = items.filter(title__icontains=query)
    if item_type in ('lost', 'found'):
        items = items.filter(item_type=item_type)

    return render(request, 'home.html', {'items': items, 'query': query, 'item_type': item_type})

def item_detail(request, pk):
    item = get_object_or_404(Item, pk=pk)
    return render(request, 'item_detail.html', {'item': item})

def register_view(request):
    form = RegisterForm(request.POST or None)
    if form.is_valid():
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password'])
        user.save()
        login(request, user)
        return redirect('dashboard')
    return render(request, 'register.html', {'form': form})

def login_view(request):
    error = None
    if request.method == 'POST':
        user = authenticate(
            username=request.POST.get('username', ''),
            password=request.POST.get('password', '')
        )
        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            error = 'Invalid username or password.'
    return render(request, 'login.html', {'error': error})

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def dashboard(request):
    items = Item.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'dashboard.html', {'items': items})

@login_required
def add_lost_item(request):
    form = ItemForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        item = form.save(commit=False)
        item.user = request.user
        item.item_type = 'lost'
        item.save()
        messages.success(request, 'Lost item posted successfully.')
        return redirect('dashboard')
    return render(request, 'item_form.html', {'form': form, 'type': 'Lost'})

@login_required
def add_found_item(request):
    form = ItemForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        item = form.save(commit=False)
        item.user = request.user
        item.item_type = 'found'
        item.save()
        messages.success(request, 'Found item posted successfully.')
        return redirect('dashboard')
    return render(request, 'item_form.html', {'form': form, 'type': 'Found'})

@login_required
def edit_item(request, pk):
    item = get_object_or_404(Item, pk=pk, user=request.user)
    form = ItemForm(request.POST or None, request.FILES or None, instance=item)
    if form.is_valid():
        form.save()
        messages.success(request, 'Item updated successfully.')
        return redirect('dashboard')
    return render(request, 'item_form.html', {'form': form, 'type': item.get_item_type_display(), 'edit': True, 'item': item})

@login_required
def delete_item(request, pk):
    item = get_object_or_404(Item, pk=pk, user=request.user)
    if request.method == 'POST':
        item.delete()
        messages.success(request, 'Item deleted.')
        return redirect('dashboard')
    return render(request, 'confirm_delete.html', {'item': item})

@login_required
def mark_resolved(request, pk):
    item = get_object_or_404(Item, pk=pk, user=request.user)
    if request.method == 'POST':
        item.status = 'resolved'
        item.save()
        messages.success(request, 'Item marked as resolved.')
    return redirect('dashboard')

@login_required
def reopen_item(request, pk):
    item = get_object_or_404(Item, pk=pk, user=request.user)
    if request.method == 'POST':
        item.status = 'active'
        item.save()
        messages.success(request, 'Item reopened.')
    return redirect('dashboard')

# ── Messaging ────────────────────────────────────────────────────────────────

@login_required
def send_message(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if request.user == item.user:
        messages.error(request, "You can't message yourself.")
        return redirect('item_detail', pk=pk)
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            Message.objects.create(
                item=item,
                sender=request.user,
                recipient=item.user,
                content=content,
            )
            messages.success(request, f'Message sent to {item.user.username}.')
            return redirect('conversation', item_pk=item.pk, other_user_pk=item.user.pk)
    return redirect('item_detail', pk=pk)


@login_required
def inbox(request):
    user = request.user
    # Get all messages involving the current user
    all_msgs = Message.objects.filter(
        Q(sender=user) | Q(recipient=user)
    ).select_related('item', 'sender', 'recipient').order_by('-sent_at')

    # Build unique conversation keys: (item_id, other_user_id)
    seen = set()
    conversations = []
    for msg in all_msgs:
        other = msg.recipient if msg.sender == user else msg.sender
        key = (msg.item_id, other.pk)
        if key not in seen:
            seen.add(key)
            unread_count = Message.objects.filter(
                item=msg.item,
                sender=other,
                recipient=user,
                is_read=False
            ).count()
            conversations.append({
                'item': msg.item,
                'other_user': other,
                'last_message': msg,
                'unread_count': unread_count,
            })

    return render(request, 'inbox.html', {'conversations': conversations})


@login_required
def conversation(request, item_pk, other_user_pk):
    from django.contrib.auth.models import User as AuthUser
    item = get_object_or_404(Item, pk=item_pk)
    other_user = get_object_or_404(AuthUser, pk=other_user_pk)
    user = request.user

    # Only participants can view this conversation
    if user != item.user and user != other_user:
        return redirect('inbox')

    thread = Message.objects.filter(
        item=item
    ).filter(
        Q(sender=user, recipient=other_user) |
        Q(sender=other_user, recipient=user)
    ).order_by('sent_at')

    # Mark incoming messages as read
    thread.filter(recipient=user, is_read=False).update(is_read=True)

    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            Message.objects.create(
                item=item,
                sender=user,
                recipient=other_user,
                content=content,
            )
        return redirect('conversation', item_pk=item_pk, other_user_pk=other_user_pk)

    return render(request, 'conversation.html', {
        'item': item,
        'other_user': other_user,
        'thread': thread,
    })
