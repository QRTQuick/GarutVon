import datetime
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, ForeignKey, 
    Text, Float, JSON, Index, create_engine
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from backend.config import Config
from argon2 import PasswordHasher

Base = declarative_base()
ph = PasswordHasher()

# 1. Users Table
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(512), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)
    
    # Preferences and Status
    is_active = Column(Boolean, default=True, nullable=False)
    email_promo_pref = Column(Boolean, default=True, nullable=False)
    email_security_pref = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    api_keys = relationship("APIKey", back_populates="user", cascade="all, delete-orphan")
    conversion_history = relationship("ConversionHistory", back_populates="user", cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")
    donations = relationship("Donation", back_populates="user")

    def set_password(self, password):
        self.password_hash = ph.hash(password)

    def check_password(self, password):
        try:
            return ph.verify(self.password_hash, password)
        except Exception:
            return False

# 2. Sessions Table
class Session(Base):
    __tablename__ = 'sessions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_token = Column(String(255), unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(512), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    
    user = relationship("User", back_populates="sessions")

# 3. Email Tokens Table (Verification)
class EmailToken(Base):
    __tablename__ = 'email_tokens'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    token = Column(String(255), unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    purpose = Column(String(50), nullable=False)  # e.g., 'VERIFY_EMAIL', 'CHANGE_EMAIL'
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_used = Column(Boolean, default=False, nullable=False)

# 4. Password Reset Tokens Table
class PasswordResetToken(Base):
    __tablename__ = 'password_reset_tokens'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    token = Column(String(255), unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_used = Column(Boolean, default=False, nullable=False)

# 5. Plans Table
class Plan(Base):
    __tablename__ = 'plans'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False) # e.g., 'Free', 'Developer Pro', 'Business'
    price = Column(Float, nullable=False, default=0.0)
    currency = Column(String(3), nullable=False, default="USD")
    interval = Column(String(20), nullable=False, default="monthly") # e.g., 'monthly', 'yearly'
    conversion_limit = Column(Integer, nullable=False, default=10) # 10 per week or based on period
    features = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    
    subscriptions = relationship("Subscription", back_populates="plan")

# 6. Subscriptions Table
class Subscription(Base):
    __tablename__ = 'subscriptions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    plan_id = Column(Integer, ForeignKey('plans.id'), nullable=False)
    status = Column(String(50), nullable=False, default="active") # e.g., 'active', 'cancelled', 'expired'
    current_period_start = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    current_period_end = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    
    user = relationship("User", back_populates="subscriptions")
    plan = relationship("Plan", back_populates="subscriptions")

# 7. API Keys Table
class APIKey(Base):
    __tablename__ = 'api_keys'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    key_prefix = Column(String(10), nullable=False) # e.g., 'gv_'
    key_hash = Column(String(255), unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    name = Column(String(100), nullable=False, default="Default Key")
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    last_used_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    user = relationship("User", back_populates="api_keys")
    usage_records = relationship("APIUsage", back_populates="api_key", cascade="all, delete-orphan")

# 8. API Usage Table
class APIUsage(Base):
    __tablename__ = 'api_usage'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    api_key_id = Column(Integer, ForeignKey('api_keys.id', ondelete='CASCADE'), nullable=False, index=True)
    endpoint = Column(String(255), nullable=False)
    method = Column(String(10), nullable=False)
    status_code = Column(Integer, nullable=False)
    ip_address = Column(String(45), nullable=True)
    response_time_ms = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    
    api_key = relationship("APIKey", back_populates="usage_records")

# 9. Conversion History Table
class ConversionHistory(Base):
    __tablename__ = 'conversion_history'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=True, index=True) # nullable for anonymous conversion if allowed or API keys
    api_key_id = Column(Integer, ForeignKey('api_keys.id', ondelete='SET NULL'), nullable=True)
    service_type = Column(String(50), nullable=False, default="image_converter") # e.g. 'image_converter', 'ocr', 'pdf'
    input_file_name = Column(String(255), nullable=False)
    input_file_size = Column(Integer, nullable=False)
    input_format = Column(String(10), nullable=False)
    output_format = Column(String(10), nullable=False)
    status = Column(String(20), nullable=False, default="completed") # 'completed', 'failed', 'processing'
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    download_token = Column(String(255), unique=True, nullable=True, index=True) # for secure downloading
    
    user = relationship("User", back_populates="conversion_history")

# 10. Image Jobs Table
class ImageJob(Base):
    __tablename__ = 'image_jobs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    job_uuid = Column(String(255), unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=True)
    input_path = Column(String(512), nullable=False)
    output_path = Column(String(512), nullable=True)
    status = Column(String(50), default="pending", nullable=False) # 'pending', 'processing', 'completed', 'failed'
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)

# 11. Notifications Table
class Notification(Base):
    __tablename__ = 'notifications'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    
    user = relationship("User", back_populates="notifications")

# 12. Audit Logs Table
class AuditLog(Base):
    __tablename__ = 'audit_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True)
    action = Column(String(100), nullable=False) # e.g. 'LOGIN', 'REGISTER', 'GENERATE_API_KEY'
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(512), nullable=True)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    
    user = relationship("User", back_populates="audit_logs")

# 13. Admins Table
class Admin(Base):
    __tablename__ = 'admins'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(512), nullable=False)
    full_name = Column(String(255), nullable=True)
    role_id = Column(Integer, ForeignKey('roles.id'), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    
    role = relationship("Role", back_populates="admins")

    def set_password(self, password):
        self.password_hash = ph.hash(password)

    def check_password(self, password):
        try:
            return ph.verify(self.password_hash, password)
        except Exception:
            return False

# 14. Roles Table
class Role(Base):
    __tablename__ = 'roles'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False) # e.g., 'super_admin', 'support', 'viewer'
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    
    admins = relationship("Admin", back_populates="role")
    permissions = relationship("Permission", secondary="role_permissions", back_populates="roles")

# 15. Permissions Table
class Permission(Base):
    __tablename__ = 'permissions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False) # e.g. 'manage_users', 'view_logs'
    description = Column(String(255), nullable=True)
    
    roles = relationship("Role", secondary="role_permissions", back_populates="permissions")

# Association Table for Role-Permissions
class RolePermission(Base):
    __tablename__ = 'role_permissions'
    
    role_id = Column(Integer, ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True)
    permission_id = Column(Integer, ForeignKey('permissions.id', ondelete='CASCADE'), primary_key=True)

# 16. Settings Table
class Setting(Base):
    __tablename__ = 'settings'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(100), unique=True, nullable=False, index=True)
    value = Column(Text, nullable=True)
    category = Column(String(50), nullable=False, default="general") # e.g. 'general', 'email', 'api'
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

# 17. Feature Flags Table
class FeatureFlag(Base):
    __tablename__ = 'feature_flags'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(String(255), nullable=True)
    is_enabled = Column(Boolean, default=False, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

# 18. Donations Table
class Donation(Base):
    __tablename__ = 'donations'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    donation_id = Column(String(255), unique=True, nullable=False, index=True) # From payment provider / Happer
    transaction_ref = Column(String(255), unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True) # Optional link to registered user
    amount = Column(Float, nullable=False)
    currency = Column(String(3), nullable=False, default="USD")
    payment_status = Column(String(50), nullable=False, default="pending") # 'pending', 'completed', 'failed'
    payment_provider = Column(String(50), nullable=False, default="Happer") # 'Happer', 'Stripe', etc.
    donor_name = Column(String(255), nullable=True)
    donor_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    
    user = relationship("User", back_populates="donations")

# 19. Donation Settings Table
class DonationSettings(Base):
    __tablename__ = 'donation_settings'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    target_amount = Column(Float, nullable=False, default=5000.0) # monthly hosting/dev target
    current_progress = Column(Float, nullable=False, default=0.0)
    currency = Column(String(3), nullable=False, default="USD")
    headline = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

# Create Database Helper Session
engine = create_engine(Config.DATABASE_URL, connect_args={"check_same_thread": False} if Config.DATABASE_URL.startswith("sqlite") else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
    # Seed plans, default settings, feature flags if empty
    db = SessionLocal()
    try:
        # 1. Seed plans
        if db.query(Plan).count() == 0:
            free_plan = Plan(
                name="Free Plan",
                price=0.0,
                currency="USD",
                interval="weekly",
                conversion_limit=10,
                features={"image_conversion": True, "api_keys": False, "future_access": False}
            )
            pro_plan = Plan(
                name="Developer Pro",
                price=29.0,
                currency="USD",
                interval="monthly",
                conversion_limit=10000,
                features={"image_conversion": True, "api_keys": True, "future_access": True}
            )
            db.add_all([free_plan, pro_plan])
            db.commit()
            
        # 2. Seed feature flags
        flags = [
            ("pdf_conversion", "PDF Conversion Tool", False),
            ("ocr", "OCR Extraction Tool", False),
            ("ai_chat", "GarutVON AI Assistant", False),
            ("image_background_removal", "AI Image Background Removal", False),
        ]
        for name, desc, enabled in flags:
            if not db.query(FeatureFlag).filter_by(name=name).first():
                db.add(FeatureFlag(name=name, description=desc, is_enabled=enabled))
        
        # 3. Seed default roles & permissions
        if db.query(Role).count() == 0:
            super_role = Role(name="super_admin", description="Full System Administrator")
            support_role = Role(name="support", description="Support agent with logs access")
            db.add_all([super_role, support_role])
            db.commit()
            
            p1 = Permission(name="manage_users", description="Ability to view and edit users")
            p2 = Permission(name="view_logs", description="Ability to view audit & system logs")
            p3 = Permission(name="manage_flags", description="Ability to toggle feature flags")
            db.add_all([p1, p2, p3])
            db.commit()
            
            super_role.permissions.extend([p1, p2, p3])
            support_role.permissions.append(p2)
            db.commit()
            
        # 4. Seed donation settings
        if db.query(DonationSettings).count() == 0:
            db.add(DonationSettings(
                target_amount=1000.0,
                current_progress=120.0,
                currency="USD",
                headline="Help Sustain GarutVON's Server Infrastructure",
                description="Your donations help us keep our core services free and run our high-performance file-conversion algorithms on premium database clusters."
            ))
            db.commit()
            
        # 5. Seed an admin account if none exists
        if db.query(Admin).count() == 0:
            admin_role = db.query(Role).filter_by(name="super_admin").first()
            if admin_role:
                new_admin = Admin(
                    email="admin@garutvon.com",
                    full_name="GarutVON SuperAdmin",
                    role_id=admin_role.id,
                    is_active=True
                )
                new_admin.set_password("AdminSecurePass2026!")
                db.add(new_admin)
                db.commit()
                
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()
