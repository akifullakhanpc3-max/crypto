import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.asymmetric import rsa, padding, ec
from cryptography.hazmat.primitives import hashes, serialization, cmac
from cryptography.hazmat.backends import default_backend
import secrets
import base64

# Get master key from environment variable
MASTER_KEY = os.getenv("MASTER_KEY")
if not MASTER_KEY:
    raise ValueError("MASTER_KEY environment variable must be set")

# Convert hex string to bytes if needed
if isinstance(MASTER_KEY, str):
    try:
        MASTER_KEY = bytes.fromhex(MASTER_KEY)
    except ValueError:
        MASTER_KEY = MASTER_KEY.encode('utf-8')[:32]  # Truncate to 32 bytes if not hex

if len(MASTER_KEY) < 32:
    raise ValueError("MASTER_KEY must be at least 32 bytes")

def generate_key(key_type: str) -> bytes:
    """Generate a cryptographic key of the specified type"""
    if key_type == "AES128GCM":
        return secrets.token_bytes(16)  # 128 bits
    elif key_type == "AES256GCM":
        return secrets.token_bytes(32)  # 256 bits
    elif key_type == "AES256CBC":
        return secrets.token_bytes(32)  # 256 bits
    elif key_type == "ChaCha20Poly1305":
        return secrets.token_bytes(32)  # 256 bits
    elif key_type == "HMAC256":
        return secrets.token_bytes(32)  # 256 bits for HMAC-SHA256
    elif key_type == "HMAC512":
        return secrets.token_bytes(64)  # 512 bits for HMAC-SHA512
    elif key_type == "RSA2048":
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        return pem
    elif key_type == "RSA4096":
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=4096,
            backend=default_backend()
        )
        pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        return pem
    elif key_type == "ECC256":
        private_key = ec.generate_private_key(
            ec.SECP256R1(),
            backend=default_backend()
        )
        pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        return pem
    elif key_type == "ECC384":
        private_key = ec.generate_private_key(
            ec.SECP384R1(),
            backend=default_backend()
        )
        pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        return pem
    elif key_type == "Ed25519":
        from cryptography.hazmat.primitives.asymmetric import ed25519
        private_key = ed25519.Ed25519PrivateKey.generate()
        pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        return pem
    elif key_type == "RSA":  # Backward compatibility
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        return pem
    else:
        raise ValueError(f"Unsupported key type: {key_type}")

def encrypt_key_with_master(key_data: bytes) -> bytes:
    """Encrypt a key using the master key with AES-256-GCM"""
    # Generate a random nonce
    nonce = secrets.token_bytes(12)  # 96 bits for GCM
    
    # Create cipher
    cipher = Cipher(
        algorithms.AES(MASTER_KEY[:32]),
        modes.GCM(nonce),
        backend=default_backend()
    )
    encryptor = cipher.encryptor()
    
    # Encrypt the key
    ciphertext = encryptor.update(key_data) + encryptor.finalize()
    
    # Return nonce + tag + ciphertext
    return nonce + encryptor.tag + ciphertext

def decrypt_key_with_master(encrypted_data: bytes) -> bytes:
    """Decrypt a key using the master key"""
    # Extract nonce (first 12 bytes), tag (next 16 bytes), and ciphertext
    nonce = encrypted_data[:12]
    tag = encrypted_data[12:28]
    ciphertext = encrypted_data[28:]
    
    # Create cipher
    cipher = Cipher(
        algorithms.AES(MASTER_KEY[:32]),
        modes.GCM(nonce, tag),
        backend=default_backend()
    )
    decryptor = cipher.decryptor()
    
    # Decrypt the key
    key_data = decryptor.update(ciphertext) + decryptor.finalize()
    return key_data

def encrypt_with_key(plaintext: str, key_data: bytes, key_type: str) -> bytes:
    """Encrypt plaintext using the specified key"""
    plaintext_bytes = plaintext.encode('utf-8')
    
    if key_type in ["AES128GCM", "AES256GCM"]:
        # Generate a random nonce
        nonce = secrets.token_bytes(12)
        
        # Create cipher
        cipher = Cipher(
            algorithms.AES(key_data),
            modes.GCM(nonce),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        
        # Encrypt
        ciphertext = encryptor.update(plaintext_bytes) + encryptor.finalize()
        
        # Return nonce + tag + ciphertext
        return nonce + encryptor.tag + ciphertext
    
    elif key_type == "AES256CBC":
        # Generate a random IV
        iv = secrets.token_bytes(16)
        
        # Create cipher
        cipher = Cipher(
            algorithms.AES(key_data),
            modes.CBC(iv),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        
        # Pad plaintext to block size (16 bytes for AES)
        from cryptography.hazmat.primitives import padding as sym_padding
        padder = sym_padding.PKCS7(128).padder()
        padded_data = padder.update(plaintext_bytes) + padder.finalize()
        
        # Encrypt
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        
        # Return IV + ciphertext
        return iv + ciphertext
    
    elif key_type == "ChaCha20Poly1305":
        from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
        
        # Generate a random nonce
        nonce = secrets.token_bytes(12)
        
        # Create cipher
        cipher = ChaCha20Poly1305(key_data)
        ciphertext = cipher.encrypt(nonce, plaintext_bytes, None)
        
        # Return nonce + ciphertext (which includes tag)
        return nonce + ciphertext
    
    elif key_type in ["HMAC256", "HMAC512"]:
        # HMAC is for authentication, not encryption
        # We'll compute HMAC and return it (this is signing, not encrypting)
        import hmac
        import hashlib
        
        if key_type == "HMAC256":
            digest = hmac.new(key_data, plaintext_bytes, hashlib.sha256).digest()
        else:  # HMAC512
            digest = hmac.new(key_data, plaintext_bytes, hashlib.sha512).digest()
        
        # Return plaintext + HMAC for verification
        return plaintext_bytes + b'|HMAC|' + digest
        
    elif key_type in ["RSA2048", "RSA4096"]:
        # Deserialize the private key to get the public key
        private_key = serialization.load_pem_private_key(
            key_data,
            password=None,
            backend=default_backend()
        )
        public_key = private_key.public_key()
        
        # Encrypt with public key
        ciphertext = public_key.encrypt(
            plaintext_bytes,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return ciphertext
    
    elif key_type in ["ECC256", "ECC384"]:
        # ECC is typically used for digital signatures, not encryption
        # We'll create a digital signature
        private_key = serialization.load_pem_private_key(
            key_data,
            password=None,
            backend=default_backend()
        )
        
        signature = private_key.sign(
            plaintext_bytes,
            ec.ECDSA(hashes.SHA256())
        )
        
        # Return plaintext + signature for verification
        return plaintext_bytes + b'|ECC|' + signature
    
    elif key_type == "Ed25519":
        # Ed25519 is for digital signatures
        from cryptography.hazmat.primitives.asymmetric import ed25519
        
        private_key = serialization.load_pem_private_key(
            key_data,
            password=None,
            backend=default_backend()
        )
        
        signature = private_key.sign(plaintext_bytes)
        
        # Return plaintext + signature for verification
        return plaintext_bytes + b'|Ed25519|' + signature
    
    elif key_type == "RSA":  # Backward compatibility
        # Deserialize the private key to get the public key
        private_key = serialization.load_pem_private_key(
            key_data,
            password=None,
            backend=default_backend()
        )
        public_key = private_key.public_key()
        
        # Encrypt with public key
        ciphertext = public_key.encrypt(
            plaintext_bytes,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return ciphertext
    
    else:
        raise ValueError(f"Unsupported key type: {key_type}")

def decrypt_with_key(ciphertext: bytes, key_data: bytes, key_type: str) -> str:
    """Decrypt ciphertext using the specified key (or verify for signature algorithms)"""
    if key_type in ["AES128GCM", "AES256GCM"]:
        # Extract nonce (first 12 bytes), tag (next 16 bytes), and ciphertext
        nonce = ciphertext[:12]
        tag = ciphertext[12:28]
        actual_ciphertext = ciphertext[28:]
        
        # Create cipher
        cipher = Cipher(
            algorithms.AES(key_data),
            modes.GCM(nonce, tag),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()
        
        # Decrypt
        plaintext_bytes = decryptor.update(actual_ciphertext) + decryptor.finalize()
        return plaintext_bytes.decode('utf-8')
    
    elif key_type == "AES256CBC":
        # Extract IV (first 16 bytes) and ciphertext
        iv = ciphertext[:16]
        actual_ciphertext = ciphertext[16:]
        
        # Create cipher
        cipher = Cipher(
            algorithms.AES(key_data),
            modes.CBC(iv),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()
        
        # Decrypt
        padded_plaintext = decryptor.update(actual_ciphertext) + decryptor.finalize()
        
        # Unpad
        from cryptography.hazmat.primitives import padding as sym_padding
        unpadder = sym_padding.PKCS7(128).unpadder()
        plaintext_bytes = unpadder.update(padded_plaintext) + unpadder.finalize()
        
        return plaintext_bytes.decode('utf-8')
    
    elif key_type == "ChaCha20Poly1305":
        from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
        
        # Extract nonce (first 12 bytes) and ciphertext
        nonce = ciphertext[:12]
        actual_ciphertext = ciphertext[12:]
        
        # Create cipher and decrypt
        cipher = ChaCha20Poly1305(key_data)
        plaintext_bytes = cipher.decrypt(nonce, actual_ciphertext, None)
        
        return plaintext_bytes.decode('utf-8')
    
    elif key_type in ["HMAC256", "HMAC512"]:
        # HMAC verification - extract plaintext and HMAC
        try:
            plaintext_part, hmac_part = ciphertext.split(b'|HMAC|', 1)
        except ValueError:
            raise ValueError("Invalid HMAC format")
        
        import hmac
        import hashlib
        
        # Recompute HMAC
        if key_type == "HMAC256":
            expected_digest = hmac.new(key_data, plaintext_part, hashlib.sha256).digest()
        else:  # HMAC512
            expected_digest = hmac.new(key_data, plaintext_part, hashlib.sha512).digest()
        
        # Verify HMAC
        if not hmac.compare_digest(hmac_part, expected_digest):
            raise ValueError("HMAC verification failed")
        
        return plaintext_part.decode('utf-8')
        
    elif key_type in ["RSA2048", "RSA4096"]:
        # Deserialize the private key
        private_key = serialization.load_pem_private_key(
            key_data,
            password=None,
            backend=default_backend()
        )
        
        # Decrypt with private key
        plaintext_bytes = private_key.decrypt(
            ciphertext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return plaintext_bytes.decode('utf-8')
    
    elif key_type in ["ECC256", "ECC384"]:
        # ECC signature verification - extract plaintext and signature
        try:
            plaintext_part, signature_part = ciphertext.split(b'|ECC|', 1)
        except ValueError:
            raise ValueError("Invalid ECC signature format")
        
        # Load private key to get public key
        private_key = serialization.load_pem_private_key(
            key_data,
            password=None,
            backend=default_backend()
        )
        public_key = private_key.public_key()
        
        # Verify signature
        try:
            public_key.verify(
                signature_part,
                plaintext_part,
                ec.ECDSA(hashes.SHA256())
            )
        except Exception:
            raise ValueError("ECC signature verification failed")
        
        return plaintext_part.decode('utf-8')
    
    elif key_type == "Ed25519":
        # Ed25519 signature verification - extract plaintext and signature
        try:
            plaintext_part, signature_part = ciphertext.split(b'|Ed25519|', 1)
        except ValueError:
            raise ValueError("Invalid Ed25519 signature format")
        
        from cryptography.hazmat.primitives.asymmetric import ed25519
        
        # Load private key to get public key
        private_key = serialization.load_pem_private_key(
            key_data,
            password=None,
            backend=default_backend()
        )
        public_key = private_key.public_key()
        
        # Verify signature
        try:
            public_key.verify(signature_part, plaintext_part)
        except Exception:
            raise ValueError("Ed25519 signature verification failed")
        
        return plaintext_part.decode('utf-8')
    
    elif key_type == "RSA":  # Backward compatibility
        # Deserialize the private key
        private_key = serialization.load_pem_private_key(
            key_data,
            password=None,
            backend=default_backend()
        )
        
        # Decrypt with private key
        plaintext_bytes = private_key.decrypt(
            ciphertext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return plaintext_bytes.decode('utf-8')
    
    else:
        raise ValueError(f"Unsupported key type: {key_type}")
