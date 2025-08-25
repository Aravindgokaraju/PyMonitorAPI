# utils/premium.py
import hashlib
from datetime import datetime  # This is the better way
from django.conf import settings

def generate_upgrade_key(user_identifier, secret=settings.SECRET_KEY):
    """Generate a unique upgrade key"""
    data = f"{user_identifier}-{secret}-{datetime.date.today()}"
    return hashlib.sha256(data.encode()).hexdigest()[:20]

def validate_upgrade_key(key, user_identifier, secret=settings.SECRET_KEY):
    """Validate an upgrade key"""
    expected_key = generate_upgrade_key(user_identifier, secret)
    return key == expected_key

def upgrade_to_premium(user, upgrade_key=None):
    """Upgrade user to premium (with or without key validation)"""
    if upgrade_key:
        # TODO Validate key if provided
        if not validate_upgrade_key(upgrade_key, user.username):
            return False, "Invalid upgrade key"
    else:
        # user.user_type = 'premium'
        user.user_type = 'premium'
        user.upgraded_at = datetime.now()
        user.upgrade_key = upgrade_key
        user.save()
        return True, "Upgraded to premium successfully"
    

def downgrade_to_demo(user, upgrade_key=None):
    # user.user_type = 'premium'
    user.user_type = 'demo'
    user.upgraded_at = datetime.now()
    user.upgrade_key = upgrade_key
    user.save()
    return True, "Downgraded to demo successfully"