# Cipher Chat (End-to-End Encrypted Chat Application)

A secure, real-time chat application built with Django and WebSockets featuring **true end-to-end encryption (E2EE)**. Messages are encrypted on the client side and the server cannot decrypt them.

![Django](https://img.shields.io/badge/Django-4.x-green)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![WebSockets](https://img.shields.io/badge/WebSockets-Channels-orange)
![Encryption](https://img.shields.io/badge/Encryption-E2EE-red)

## Features

### Core Functionality

- **Real-time Messaging** - Instant message delivery using WebSockets
- **Private Chats** - One-on-one encrypted conversations
- **Group Chats** - Encrypted group conversations with multiple participants
- **User Search** - Find and start conversations with other users
- **Message History** - Access previous encrypted messages

### Security Features

- **True End-to-End Encryption** - Server cannot decrypt messages
- **ECDH Key Exchange** - Elliptic Curve Diffie-Hellman for private chats
- **AES-256-GCM Encryption** - Industry-standard symmetric encryption
- **Key Wrapping** - Secure distribution of group chat keys
- **Client-Side Key Storage** - Private keys never leave the browser
- **Forward Secrecy** - Each chat has unique encryption keys

## How It Works

### Private Chats (1-on-1)

```
User A                          Server                          User B
------                          ------                          ------
Generate ECDH key pair          Store public keys              Generate ECDH key pair
       ↓                               ↓                                ↓
   Public Key A    →→→→→    Server forwards    →→→→→        Public Key B
       ↓                                                              ↓
Derive shared AES key                                    Derive shared AES key
(using private A + public B)                            (using private B + public A)
       ↓                                                              ↓
    SAME KEY! ←←←←←←←←←←← Mathematical magic! ←←←←←←←←←←←←←←←← SAME KEY!
       ↓                                                              ↓
Encrypt with shared key  →→→  Server stores encrypted  ←←→  Decrypt with shared key
                                   (cannot read!)
```

### Group Chats
```
Creator                         Server                         Members
-------                         ------                         -------
Generate AES group key             |                              |
       ↓                           |                              |
Encrypt key for Member 1           |                              |
Encrypt key for Member 2    →→→    Store encrypted keys    →→→   Each member gets
Encrypt key for Member 3           (cannot decrypt!)             their encrypted copy
       ↓                           |                              ↓
All messages use                   |                     Decrypt personal copy
the same group key                 |                     of the group key
```

**Key Point:** The server only stores encrypted data and cannot decrypt any messages!

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Step 1: Clone the Repository
```bash
git clone https://github.com/Eihaab-cmyk/Cipher-Chat.git
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
cd chat_project
pip install -r requirements.txt
```

### Step 4: Configure Redis (for Channels)
Install Redis on your system:

**Windows:**
- Download from https://redis.io/download or use WSL
- Or use `choco install redis` (if you have Chocolatey)

**macOS:**
```bash
brew install redis
brew services start redis
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install redis-server
sudo systemctl start redis
```

### Step 5: Database Setup
```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 6: Create Superuser (Optional)
```bash
python manage.py createsuperuser
```

### Step 7: Run the Development Server
```bash

# Terminal: Start Daphne (for WebSockets)
daphne -p 8000 chat_project.asgi:application
```

Visit `http://localhost:8000` in your browser.

## 📁 Project Structure

```
chat_project/
├── chat/                      # Main chat application
│   ├── models.py             # Database models (Chat, Message, UserKeyPair)
│   ├── views.py              # API endpoints
│   ├── consumers.py          # WebSocket handlers
│   ├── urls.py               # URL routing
│   └── templates/
│       └── chat/
│           └── home.html     # Main chat interface with E2EE JavaScript
├── users/                     # User authentication
│   ├── views.py              # Login/signup/logout
│   └── forms.py              # User forms
├── manage.py
└── requirements.txt
```

## Usage

### 1. Create an Account
- Navigate to the signup page
- Create a username and password
- Encryption keys are automatically generated on first login

### 2. Start a Private Chat
- Search for a user by username
- Click on their name to start a chat
- Your browser automatically performs key exchange
- Start sending encrypted messages!

### 3. Create a Group Chat
- Click "Create Group" or similar button
- Enter a group name
- Search and select multiple users
- The group key is encrypted for each member
- All members can now chat securely

### 4. Verify Encryption
- Open browser Developer Tools (F12)
- Check the Network tab or Database
- Messages in the database should appear as Base64 gibberish
- This confirms the server cannot read your messages!

## Technical Details

### Encryption Specifications
- **Algorithm:** AES-GCM (Galois/Counter Mode)
- **Key Length:** 256 bits
- **IV Length:** 96 bits (12 bytes)
- **Key Exchange:** ECDH with P-256 curve
- **Key Storage:** Browser localStorage

### Database Models

#### UserKeyPair
Stores user's public key (private key stays in browser)
```python
- user: OneToOneField(User)
- public_key: TextField (JWK format)
- created_at: DateTimeField
```

#### Chat
```python
- name: CharField (for groups)
- is_group: BooleanField
- creator: ForeignKey(User) - for group key decryption
- created_at: DateTimeField
```

#### ChatMember
```python
- chat: ForeignKey(Chat)
- user: ForeignKey(User)
- encrypted_chat_key: TextField (for groups)
- partner_public_key: TextField (for private chats)
```

#### Message
```python
- chat: ForeignKey(Chat)
- sender: ForeignKey(User)
- content: TextField (encrypted)
- iv: TextField (initialization vector)
- timestamp: DateTimeField
```

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/register-public-key/` | POST | Register user's public key |
| `/api/get-public-key/<user_id>/` | GET | Get a user's public key |
| `/api/get-users-public-keys/` | GET | Batch fetch public keys |
| `/api/search-users/` | GET | Search for users |
| `/api/start-chat/<user_id>/` | POST | Start a private chat |
| `/api/my-chats/` | GET | Get user's chat list |
| `/api/messages/<chat_id>/` | GET | Get messages for a chat |
| `/api/create-group/` | POST | Create a group chat |

### WebSocket Events
- **Connection:** `/ws/chat/<chat_id>/`
- **Send Message:** `{ message: encrypted_content, iv: initialization_vector }`
- **Receive Message:** `{ message: encrypted_content, iv: iv, username: sender }`

## Security Considerations

### What This Provides
- **Server-Blind Encryption:** Server cannot read message content
- **Man-in-the-Middle Protection:** Public keys tied to user accounts
- **Authenticated Encryption:** AES-GCM provides integrity and confidentiality
- **Unique Session Keys:** Each chat has different encryption keys

### Current Limitations
1. **Key Storage:** Private keys in localStorage (vulnerable if device compromised)
2. **No Key Verification:** No UI for verifying partner's identity (safety numbers)
3. **No Key Backup:** Lost browser data = lost messages
4. **Single Device:** Keys don't sync across devices
5. **Metadata Visible:** Server knows who talks to whom and when
6. **No Perfect Forward Secrecy:** Old messages vulnerable if private key leaked

### Production Recommendations
1. **Use HTTPS:** Always use TLS/SSL in production
2. **Use WSS:** Secure WebSocket connections (wss://)
3. **Rate Limiting:** Prevent abuse of key registration
4. **Input Validation:** Sanitize all user inputs
5. **CSRF Protection:** Enabled by default in Django
6. **Key Rotation:** Implement periodic key updates
7. **Audit Logging:** Log security-relevant events

## Development

### Running Tests
```bash
python manage.py test
```

### Database Migrations
```bash
# After model changes:
python manage.py makemigrations
python manage.py migrate
```

### Clearing Test Data
```python
# In Django shell:
python manage.py shell

>>> from chat.models import Chat, Message
>>> Chat.objects.all().delete()
>>> Message.objects.all().delete()
```

### Debug Mode
Set in `settings.py`:
```python
DEBUG = True  # For development only!
```

## Troubleshooting

### Messages Not Decrypting
- **Clear browser cache** (Ctrl+Shift+R)
- Check browser console for JavaScript errors
- Verify both users have encryption keys set up
- For groups: Ensure creator's public key is accessible

### WebSocket Connection Failed
- Verify Redis is running: `redis-cli ping` (should return "PONG")
- Check Django Channels configuration
- Ensure ASGI application is properly configured

### "Encryption keys not set up" Error
- User needs to log out and log back in
- Keys are generated on first login after E2EE implementation
- Check browser localStorage for 'privateKey' and 'publicKey'

### Group Chat Only Works for Creator
- Ensure you've applied all migrations
- Check that `Chat.creator` field exists
- Verify frontend uses updated `decryptKeyForUser` function
- Backend should return `creator_public_key` for groups

## Additional Resources

- [Web Crypto API Documentation](https://developer.mozilla.org/en-US/docs/Web/API/Web_Crypto_API)
- [Django Channels Documentation](https://channels.readthedocs.io/)
- [ECDH Key Exchange Explained](https://en.wikipedia.org/wiki/Elliptic-curve_Diffie%E2%80%93Hellman)
- [Signal Protocol](https://signal.org/docs/) - For advanced E2EE features

## Contributing

Contributions are welcome! Areas for improvement:
- Key fingerprint verification UI
- Multi-device support
- Encrypted key backup with password
- Perfect forward secrecy (ratcheting)
- File sharing with encryption
- Voice/video calls

## Author

Muhammad Eihaab
- GitHub: https://github.com/Eihaab-cmyk
- Email: muhammadeihaab5@gmail.com

## Acknowledgments

- Inspired by Signal Protocol and Matrix
- Built with Django and Django Channels
- Uses Web Crypto API for client-side encryption

---

**⚠️ Disclaimer:** This is an educational project demonstrating E2EE concepts. For production use, conduct a thorough security audit and consider using established protocols like Signal Protocol or Matrix.

**🔐 Remember:** True security requires more than just encryption - it requires proper key management, regular updates, and security best practices!
