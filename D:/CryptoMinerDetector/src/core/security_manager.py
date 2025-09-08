#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Security Manager for CryptoMinerDetector
Handles security, encryption, and access control.
"""

import logging
import hashlib
import hmac
import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import json

class SecurityManager:
    """
    Manages security aspects of the CryptoMinerDetector system.
    Handles encryption, decryption, access control, and security validation.
    """
    
    def __init__(self, config):
        """
        Initialize the security manager.
        
        Args:
            config: Configuration manager instance
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize encryption
        self._initialize_encryption()
        
        # Security settings
        self.session_timeout = config.getint('SECURITY', 'session_timeout_minutes', fallback=30)
        self.max_login_attempts = config.getint('SECURITY', 'max_login_attempts', fallback=3)
        
        # Session management
        self.active_sessions = {}
        self.failed_login_attempts = {}
        
    def _initialize_encryption(self):
        """Initialize encryption keys and cipher."""
        try:
            encryption_key_file = self.config.get('SECURITY', 'encryption_key_file')
            
            if os.path.exists(encryption_key_file):
                # Load existing key
                with open(encryption_key_file, 'rb') as f:
                    key = f.read()
            else:
                # Generate new key
                key = Fernet.generate_key()
                
                # Save key to file
                os.makedirs(os.path.dirname(encryption_key_file), exist_ok=True)
                with open(encryption_key_file, 'wb') as f:
                    f.write(key)
                    
            self.cipher = Fernet(key)
            self.logger.info("Encryption initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize encryption: {e}")
            raise
            
    def encrypt_data(self, data: str) -> str:
        """
        Encrypt sensitive data.
        
        Args:
            data: Data to encrypt
            
        Returns:
            Encrypted data as base64 string
        """
        try:
            if isinstance(data, str):
                data = data.encode('utf-8')
            encrypted_data = self.cipher.encrypt(data)
            return base64.b64encode(encrypted_data).decode('utf-8')
            
        except Exception as e:
            self.logger.error(f"Failed to encrypt data: {e}")
            raise
            
    def decrypt_data(self, encrypted_data: str) -> str:
        """
        Decrypt sensitive data.
        
        Args:
            encrypted_data: Encrypted data as base64 string
            
        Returns:
            Decrypted data
        """
        try:
            encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))
            decrypted_data = self.cipher.decrypt(encrypted_bytes)
            return decrypted_data.decode('utf-8')
            
        except Exception as e:
            self.logger.error(f"Failed to decrypt data: {e}")
            raise
            
    def hash_password(self, password: str, salt: Optional[str] = None) -> Dict[str, str]:
        """
        Hash a password with salt.
        
        Args:
            password: Password to hash
            salt: Optional salt (if None, generates new salt)
            
        Returns:
            Dictionary containing hash and salt
        """
        try:
            if salt is None:
                salt = os.urandom(32)
            else:
                salt = base64.b64decode(salt.encode('utf-8'))
                
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            
            key = base64.b64encode(kdf.derive(password.encode('utf-8')))
            salt_b64 = base64.b64encode(salt).decode('utf-8')
            
            return {
                'hash': key.decode('utf-8'),
                'salt': salt_b64
            }
            
        except Exception as e:
            self.logger.error(f"Failed to hash password: {e}")
            raise
            
    def verify_password(self, password: str, stored_hash: str, stored_salt: str) -> bool:
        """
        Verify a password against stored hash and salt.
        
        Args:
            password: Password to verify
            stored_hash: Stored password hash
            stored_salt: Stored password salt
            
        Returns:
            True if password matches, False otherwise
        """
        try:
            hash_result = self.hash_password(password, stored_salt)
            return hash_result['hash'] == stored_hash
            
        except Exception as e:
            self.logger.error(f"Failed to verify password: {e}")
            return False
            
    def generate_session_token(self, user_id: str) -> str:
        """
        Generate a session token for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Session token
        """
        try:
            # Create session data
            session_data = {
                'user_id': user_id,
                'created_at': datetime.now().isoformat(),
                'expires_at': (datetime.now() + timedelta(minutes=self.session_timeout)).isoformat()
            }
            
            # Encrypt session data
            session_json = json.dumps(session_data)
            encrypted_session = self.encrypt_data(session_json)
            
            # Create token with HMAC for integrity
            token_data = f"{user_id}:{encrypted_session}"
            hmac_signature = hmac.new(
                self.cipher._encryption_key,
                token_data.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            token = f"{token_data}:{hmac_signature}"
            return base64.b64encode(token.encode('utf-8')).decode('utf-8')
            
        except Exception as e:
            self.logger.error(f"Failed to generate session token: {e}")
            raise
            
    def validate_session_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Validate a session token.
        
        Args:
            token: Session token to validate
            
        Returns:
            Session data if valid, None otherwise
        """
        try:
            # Decode token
            token_bytes = base64.b64decode(token.encode('utf-8'))
            token_str = token_bytes.decode('utf-8')
            
            # Split token parts
            parts = token_str.split(':')
            if len(parts) != 3:
                return None
                
            user_id, encrypted_session, hmac_signature = parts
            
            # Verify HMAC
            token_data = f"{user_id}:{encrypted_session}"
            expected_hmac = hmac.new(
                self.cipher._encryption_key,
                token_data.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            if not hmac.compare_digest(hmac_signature, expected_hmac):
                return None
                
            # Decrypt session data
            session_json = self.decrypt_data(encrypted_session)
            session_data = json.loads(session_json)
            
            # Check expiration
            expires_at = datetime.fromisoformat(session_data['expires_at'])
            if datetime.now() > expires_at:
                return None
                
            return session_data
            
        except Exception as e:
            self.logger.error(f"Failed to validate session token: {e}")
            return None
            
    def create_user_session(self, user_id: str) -> str:
        """
        Create a new user session.
        
        Args:
            user_id: User ID
            
        Returns:
            Session token
        """
        try:
            token = self.generate_session_token(user_id)
            
            # Store session
            self.active_sessions[token] = {
                'user_id': user_id,
                'created_at': datetime.now(),
                'last_activity': datetime.now()
            }
            
            self.logger.info(f"Created session for user {user_id}")
            return token
            
        except Exception as e:
            self.logger.error(f"Failed to create user session: {e}")
            raise
            
    def validate_user_session(self, token: str) -> bool:
        """
        Validate a user session.
        
        Args:
            token: Session token
            
        Returns:
            True if session is valid, False otherwise
        """
        try:
            session_data = self.validate_session_token(token)
            if not session_data:
                return False
                
            # Update last activity
            if token in self.active_sessions:
                self.active_sessions[token]['last_activity'] = datetime.now()
                
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to validate user session: {e}")
            return False
            
    def end_user_session(self, token: str):
        """
        End a user session.
        
        Args:
            token: Session token to end
        """
        try:
            if token in self.active_sessions:
                user_id = self.active_sessions[token]['user_id']
                del self.active_sessions[token]
                self.logger.info(f"Ended session for user {user_id}")
                
        except Exception as e:
            self.logger.error(f"Failed to end user session: {e}")
            
    def cleanup_expired_sessions(self):
        """Clean up expired sessions."""
        try:
            current_time = datetime.now()
            expired_tokens = []
            
            for token, session in self.active_sessions.items():
                if current_time - session['last_activity'] > timedelta(minutes=self.session_timeout):
                    expired_tokens.append(token)
                    
            for token in expired_tokens:
                self.end_user_session(token)
                
            if expired_tokens:
                self.logger.info(f"Cleaned up {len(expired_tokens)} expired sessions")
                
        except Exception as e:
            self.logger.error(f"Failed to cleanup expired sessions: {e}")
            
    def record_login_attempt(self, user_id: str, success: bool):
        """
        Record a login attempt.
        
        Args:
            user_id: User ID
            success: Whether the login was successful
        """
        try:
            if user_id not in self.failed_login_attempts:
                self.failed_login_attempts[user_id] = []
                
            if not success:
                self.failed_login_attempts[user_id].append(datetime.now())
                
                # Clean old attempts
                cutoff_time = datetime.now() - timedelta(minutes=30)
                self.failed_login_attempts[user_id] = [
                    attempt for attempt in self.failed_login_attempts[user_id]
                    if attempt > cutoff_time
                ]
            else:
                # Clear failed attempts on successful login
                if user_id in self.failed_login_attempts:
                    del self.failed_login_attempts[user_id]
                    
        except Exception as e:
            self.logger.error(f"Failed to record login attempt: {e}")
            
    def is_account_locked(self, user_id: str) -> bool:
        """
        Check if an account is locked due to too many failed login attempts.
        
        Args:
            user_id: User ID
            
        Returns:
            True if account is locked, False otherwise
        """
        try:
            if user_id not in self.failed_login_attempts:
                return False
                
            recent_attempts = self.failed_login_attempts[user_id]
            return len(recent_attempts) >= self.max_login_attempts
            
        except Exception as e:
            self.logger.error(f"Failed to check account lock status: {e}")
            return False
            
    def get_failed_attempts_count(self, user_id: str) -> int:
        """
        Get the number of failed login attempts for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Number of failed attempts
        """
        try:
            if user_id not in self.failed_login_attempts:
                return 0
            return len(self.failed_login_attempts[user_id])
            
        except Exception as e:
            self.logger.error(f"Failed to get failed attempts count: {e}")
            return 0
            
    def generate_secure_random_string(self, length: int = 32) -> str:
        """
        Generate a secure random string.
        
        Args:
            length: Length of the string
            
        Returns:
            Secure random string
        """
        try:
            random_bytes = os.urandom(length)
            return base64.b64encode(random_bytes).decode('utf-8')[:length]
            
        except Exception as e:
            self.logger.error(f"Failed to generate secure random string: {e}")
            raise
            
    def validate_api_key(self, api_key: str, service: str) -> bool:
        """
        Validate an API key format.
        
        Args:
            api_key: API key to validate
            service: Service name
            
        Returns:
            True if API key format is valid, False otherwise
        """
        try:
            if not api_key or api_key.strip() == '':
                return False
                
            # Basic validation based on service
            if service == 'shodan':
                # Shodan API keys are typically 32 characters
                return len(api_key) == 32 and api_key.isalnum()
            elif service == 'censys':
                # Censys API keys are typically UUID format
                return len(api_key) == 36 and '-' in api_key
            elif service == 'ipinfo':
                # IPInfo tokens are typically alphanumeric
                return len(api_key) > 0 and api_key.isalnum()
            else:
                # Generic validation
                return len(api_key) > 0
                
        except Exception as e:
            self.logger.error(f"Failed to validate API key: {e}")
            return False
            
    def sanitize_input(self, input_data: str) -> str:
        """
        Sanitize user input to prevent injection attacks.
        
        Args:
            input_data: Input data to sanitize
            
        Returns:
            Sanitized input data
        """
        try:
            # Remove potentially dangerous characters
            dangerous_chars = ['<', '>', '"', "'", '&', ';', '|', '`', '$', '(', ')', '{', '}']
            sanitized = input_data
            
            for char in dangerous_chars:
                sanitized = sanitized.replace(char, '')
                
            # Remove multiple spaces
            sanitized = ' '.join(sanitized.split())
            
            return sanitized.strip()
            
        except Exception as e:
            self.logger.error(f"Failed to sanitize input: {e}")
            return input_data
            
    def validate_ip_address(self, ip_address: str) -> bool:
        """
        Validate IP address format.
        
        Args:
            ip_address: IP address to validate
            
        Returns:
            True if IP address is valid, False otherwise
        """
        try:
            import ipaddress
            ipaddress.ip_address(ip_address)
            return True
            
        except ValueError:
            return False
        except Exception as e:
            self.logger.error(f"Failed to validate IP address: {e}")
            return False
            
    def validate_cidr_range(self, cidr_range: str) -> bool:
        """
        Validate CIDR range format.
        
        Args:
            cidr_range: CIDR range to validate
            
        Returns:
            True if CIDR range is valid, False otherwise
        """
        try:
            import ipaddress
            ipaddress.ip_network(cidr_range, strict=False)
            return True
            
        except ValueError:
            return False
        except Exception as e:
            self.logger.error(f"Failed to validate CIDR range: {e}")
            return False