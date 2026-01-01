from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.db.models import Q
from .models import Chat, ChatMember, UserKeyPair
import json
from django.views.decorators.http import require_http_methods

@login_required
def home(request):
    return render(request, 'chat/home.html')

# Register user's public key and encrypted private key
@login_required
@require_http_methods(["POST"])
def register_public_key(request):
    data = json.loads(request.body)
    public_key = data.get("public_key")
    encrypted_private_key = data.get("encrypted_private_key")
    salt = data.get("salt")
    
    if not public_key or not encrypted_private_key or not salt:
        return JsonResponse({"error": "Missing required fields"}, status=400)
    
    # Create or update user's keys
    keypair, created = UserKeyPair.objects.update_or_create(
        user=request.user,
        defaults={
            'public_key': public_key,
            'encrypted_private_key': encrypted_private_key,
            'salt': salt
        }
    )
    
    return JsonResponse({
        "success": True,
        "message": "Keys registered",
        "created": created
    })

# Get user's encrypted private key (for multi-device sync)
@login_required
def get_my_encrypted_key(request):
    try:
        keypair = UserKeyPair.objects.get(user=request.user)
        return JsonResponse({
            "public_key": keypair.public_key,
            "encrypted_private_key": keypair.encrypted_private_key,
            "salt": keypair.salt
        })
    except UserKeyPair.DoesNotExist:
        return JsonResponse({"error": "No keys found"}, status=404)

# Get user's public key
@login_required
def get_public_key(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        keypair = UserKeyPair.objects.get(user=user)
        return JsonResponse({
            "user_id": user_id,
            "username": user.username,
            "public_key": keypair.public_key
        })
    except (User.DoesNotExist, UserKeyPair.DoesNotExist):
        return JsonResponse({"error": "User or key not found"}, status=404)

# Search Users API
@login_required
def search_users(request):
    query = request.GET.get("q", "")
    if not query:
        return JsonResponse({"users": []})
    users = User.objects.filter(
        Q(username__icontains=query) | Q(email__icontains=query)
    ).exclude(id=request.user.id)
    return JsonResponse({
        "users": [{"id": u.id, "username": u.username, "email": u.email} for u in users]
    })

# Start private chat
@login_required
def start_private_chat(request, user_id):
    current_user = request.user
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            my_public_key_for_chat = data.get("my_public_key")
        except:
            my_public_key_for_chat = None
    else:
        my_public_key_for_chat = None
    
    try:
        target = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)
    
    if not UserKeyPair.objects.filter(user=target).exists():
        return JsonResponse({"error": "Target user hasn't set up encryption keys"}, status=400)
    
    if not UserKeyPair.objects.filter(user=current_user).exists():
        return JsonResponse({"error": "You haven't set up encryption keys"}, status=400)
    
    existing_chat = Chat.objects.filter(
        is_group=False,
        members__user=current_user
    ).filter(
        members__user=target
    ).first()

    if existing_chat:
        my_membership = ChatMember.objects.get(chat=existing_chat, user=current_user)
        return JsonResponse({
            "chat_id": existing_chat.id,
            "partner_public_key": my_membership.partner_public_key
        })
    
    chat = Chat.objects.create(is_group=False)
    
    target_keypair = UserKeyPair.objects.get(user=target)
    current_keypair = UserKeyPair.objects.get(user=current_user)
    
    ChatMember.objects.create(
        chat=chat, 
        user=current_user,
        partner_public_key=target_keypair.public_key
    )
    ChatMember.objects.create(
        chat=chat, 
        user=target,
        partner_public_key=current_keypair.public_key
    )

    return JsonResponse({
        "chat_id": chat.id,
        "partner_public_key": target_keypair.public_key
    })

@login_required
def my_chats(request):
    chats = Chat.objects.filter(members__user=request.user).distinct()
    data = []
    for chat in chats:
        members = chat.members.all()
        data.append({
            "chat_id": chat.id,
            "is_group": chat.is_group,
            "name": chat.name if chat.is_group else " & ".join([m.user.username for m in members]),
            "members": [m.user.username for m in members]
        })

    return JsonResponse({"chats": data})

@login_required
def get_messages(request, chat_id):
    try:
        chat = Chat.objects.get(id=chat_id)
    except Chat.DoesNotExist:
        return JsonResponse({"error": "Chat not found"}, status=404)
    
    try:
        my_membership = ChatMember.objects.get(chat=chat, user=request.user)
    except ChatMember.DoesNotExist:
        return JsonResponse({"error": "Not allowed"}, status=403)
    
    messages = chat.messages.order_by("timestamp")
    
    response_data = {
        "messages": [
            {
                "sender": msg.sender.username,
                "content": msg.content,
                "timestamp": msg.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "iv": msg.iv
            }
            for msg in messages
        ],
        "is_group": chat.is_group
    }
    
    if chat.is_group:
        response_data["encrypted_chat_key"] = my_membership.encrypted_chat_key
        try:
            creator_keypair = UserKeyPair.objects.get(user=chat.creator)
            response_data["creator_public_key"] = creator_keypair.public_key
        except (UserKeyPair.DoesNotExist, AttributeError):
            return JsonResponse({"error": "Group creator's key not found"}, status=500)
    else:
        response_data["partner_public_key"] = my_membership.partner_public_key
    
    return JsonResponse(response_data)

@login_required
@require_http_methods(["POST"])
def create_group(request):
    data = json.loads(request.body)
    name = data.get("name")
    user_ids = data.get("members", [])
    encrypted_keys = data.get("encrypted_keys", {})
    
    if not name or not user_ids:
        return JsonResponse({"error": "Missing fields"}, status=400)
    
    members_without_keys = []
    for uid in user_ids + [request.user.id]:
        if not UserKeyPair.objects.filter(user_id=uid).exists():
            try:
                user = User.objects.get(id=uid)
                members_without_keys.append(user.username)
            except User.DoesNotExist:
                pass
    
    if members_without_keys:
        return JsonResponse({
            "error": f"These users haven't set up encryption: {', '.join(members_without_keys)}"
        }, status=400)
    
    chat = Chat.objects.create(name=name, is_group=True, creator=request.user)
    
    ChatMember.objects.create(
        chat=chat, 
        user=request.user,
        encrypted_chat_key=encrypted_keys.get(str(request.user.id))
    )

    for uid in user_ids:
        try:
            user = User.objects.get(id=uid)
            ChatMember.objects.create(
                chat=chat, 
                user=user,
                encrypted_chat_key=encrypted_keys.get(str(uid))
            )
        except User.DoesNotExist:
            pass

    return JsonResponse({"chat_id": chat.id})

@login_required
def get_users_public_keys(request):
    user_ids_str = request.GET.get('user_ids', '')
    if not user_ids_str:
        return JsonResponse({"keys": {}})
    
    user_ids = [int(uid) for uid in user_ids_str.split(',') if uid.strip().isdigit()]
    
    keys = {}
    for uid in user_ids:
        try:
            keypair = UserKeyPair.objects.get(user_id=uid)
            keys[str(uid)] = keypair.public_key
        except UserKeyPair.DoesNotExist:
            keys[str(uid)] = None
    
    return JsonResponse({"keys": keys})