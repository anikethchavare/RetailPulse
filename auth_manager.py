# RetailPulse (Enterprise Sales Data Analyzer) - auth_manager.py

# Imports
import hashlib
from typing import Dict, Optional, Tuple, Set

# Class 1: AuthManager
class AuthManager:
    """ Manages user authentication, password hashing, and role permissions. """
    
    # Default Users Seeded with SHA-256 Hashed Passwords
    DEFAULT_USERS: Dict[str, Dict[str, str]] = {
        "admin": {
            "password_hash": hashlib.sha256("admin123".encode("utf-8")).hexdigest(),
            "role": "Admin",
            "email": "admin@retailpulse.internal"
        },
        "analyst": {
            "password_hash": hashlib.sha256("analyst123".encode("utf-8")).hexdigest(),
            "role": "Analyst",
            "email": "analyst@retailpulse.internal"
        },
        "viewer": {
            "password_hash": hashlib.sha256("viewer123".encode("utf-8")).hexdigest(),
            "role": "Viewer",
            "email": "viewer@retailpulse.internal"
        }
    }

    # Role Permission Matrix Defined Via Native Sets
    ROLE_PERMISSIONS: Dict[str, Set[str]] = {
        "Admin": {
            "view_sales",
            "execute_query",
            "view_analytics",
            "view_anomalies",
            "view_basket",
            "view_rfm",
            "export_reports",
            "dispatch_email",
            "view_audit_trail",
            "manage_users"
        },
        "Analyst": {
            "view_sales",
            "execute_query",
            "view_analytics",
            "view_anomalies",
            "view_basket",
            "view_rfm",
            "export_reports",
            "dispatch_email"
        },
        "Viewer": {
            "view_sales",
            "view_analytics"
        }
    }
    
    # Constructor: __init__
    def __init__(self) -> None:
        # Deep Copy of Users Dictionary
        self.users: Dict[str, Dict[str, str]] = {k: dict(v) for k, v in self.DEFAULT_USERS.items()}
        self.current_user: Optional[str] = None
        self.current_role: Optional[str] = None
    
    # Method 1: hash_password (Static)
    @staticmethod
    def hash_password(password: str) -> str:
        """ Hash a raw string password with SHA-256. """
        
        return hashlib.sha256(password.encode("utf-8")).hexdigest()
    
    # Method 2: authenticate
    def authenticate(self, username: str, password: str) -> Tuple[bool, str, Optional[str]]:
        """ Authenticate a user by verifying the entered password against the stored SHA-256 hash. """
        
        clean_user = username.strip().lower()
        
        if clean_user not in self.users:
            return False, "User not found.", None

        input_hash = self.hash_password(password.strip())
        stored_hash = self.users[clean_user]["password_hash"]

        if input_hash == stored_hash:
            self.current_user = clean_user
            self.current_role = self.users[clean_user]["role"]
            return True, "Authentication successful.", self.current_role

        return False, "Invalid credentials provided.", None
    
    # Method 3: logout
    def logout(self) -> None:
        """ Clear active user session state. """
        
        self.current_user = None
        self.current_role = None
    
    # Method 4: has_permission
    def has_permission(self, permission_name: str) -> bool:
        """ Check if the currently active role possesses a specific permission. """
        
        if not self.current_role:
            return False
        
        role_perms = self.ROLE_PERMISSIONS.get(self.current_role, set())
        
        return permission_name in role_perms
    
    # Method 5: add_user
    def add_user(self, username: str, password: str, role: str, email: str = "") -> Tuple[bool, str]:
        """ Add a new user credential to the system (Admin only feature). """
        
        if not self.has_permission("manage_users"):
            return False, "Access denied: Requires Admin privileges."

        clean_user = username.strip().lower()
        
        if clean_user in self.users:
            return False, f"User '{clean_user}' already exists."

        if role not in self.ROLE_PERMISSIONS:
            return False, f"Invalid role '{role}'. Valid roles: {list(self.ROLE_PERMISSIONS.keys())}"

        self.users[clean_user] = {
            "password_hash": self.hash_password(password.strip()),
            "role": role,
            "email": email.strip() or f"{clean_user}@retailpulse.internal"
        }
        
        return True, f"User '{clean_user}' successfully registered with role '{role}'."
    
    # Method 6: get_session_info
    def get_session_info(self) -> Dict[str, Optional[str]]:
        """ Return a snapshot of current user session metadata. """
        
        return {
            "username": self.current_user,
            "role": self.current_role,
            "email": self.users[self.current_user]["email"] if self.current_user else None
        }