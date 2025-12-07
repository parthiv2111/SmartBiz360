"""
OTP service for generating and validating OTPs
"""
import random
import string
from datetime import datetime, timedelta
from models import db, PasswordResetOTP, User
import logging

logger = logging.getLogger(__name__)

class OTPService:
    def __init__(self):
        self.otp_length = 6
        self.otp_expiry_minutes = 10
        self.max_attempts = 3
        
    def generate_otp(self) -> str:
        """
        Generate a 6-digit OTP
        """
        return ''.join(random.choices(string.digits, k=self.otp_length))
    
    def create_otp_for_user(self, email: str) -> dict:
        """
        Create OTP for password reset
        """
        try:
            # Check if user exists
            user = User.query.filter_by(email=email).first()
            if not user:
                return {
                    'success': False,
                    'error': 'No account found with this email address'
                }
            
            # Deactivate any existing OTPs for this user
            existing_otps = PasswordResetOTP.query.filter_by(
                user_id=user.id, 
                is_used=False
            ).all()
            
            for otp in existing_otps:
                otp.is_used = True
            
            # Generate new OTP
            otp_code = self.generate_otp()
            expires_at = datetime.utcnow() + timedelta(minutes=self.otp_expiry_minutes)
            
            # Create new OTP record
            otp_record = PasswordResetOTP(
                user_id=user.id,
                email=email,
                otp_code=otp_code,
                expires_at=expires_at
            )
            
            db.session.add(otp_record)
            db.session.commit()
            
            logger.info(f"OTP created for user {email}")
            
            return {
                'success': True,
                'otp_id': str(otp_record.id),
                'expires_at': expires_at.isoformat(),
                'user_name': f"{user.first_name} {user.last_name}".strip()
            }
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to create OTP for {email}: {str(e)}")
            return {
                'success': False,
                'error': 'Failed to create OTP. Please try again.'
            }
    
    def verify_otp(self, email: str, otp_code: str) -> dict:
        """
        Verify OTP code
        """
        try:
            # Find the most recent valid OTP for this email
            otp_record = PasswordResetOTP.query.filter_by(
                email=email,
                is_used=False
            ).order_by(PasswordResetOTP.created_at.desc()).first()
            
            if not otp_record:
                return {
                    'success': False,
                    'error': 'No OTP found for this email address'
                }
            
            # Check if OTP is expired
            if otp_record.is_expired():
                otp_record.is_used = True
                db.session.commit()
                return {
                    'success': False,
                    'error': 'OTP has expired. Please request a new one.'
                }
            
            # Check if OTP code matches
            if otp_record.otp_code != otp_code:
                return {
                    'success': False,
                    'error': 'Invalid OTP code. Please check and try again.'
                }
            
            # Mark OTP as used
            otp_record.is_used = True
            db.session.commit()
            
            logger.info(f"OTP verified successfully for {email}")
            
            return {
                'success': True,
                'user_id': str(otp_record.user_id),
                'message': 'OTP verified successfully'
            }
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to verify OTP for {email}: {str(e)}")
            return {
                'success': False,
                'error': 'Failed to verify OTP. Please try again.'
            }
    
    def cleanup_expired_otps(self):
        """
        Clean up expired OTPs (can be called periodically)
        """
        try:
            expired_otps = PasswordResetOTP.query.filter(
                PasswordResetOTP.expires_at < datetime.utcnow(),
                PasswordResetOTP.is_used == False
            ).all()
            
            for otp in expired_otps:
                otp.is_used = True
            
            db.session.commit()
            
            if expired_otps:
                logger.info(f"Cleaned up {len(expired_otps)} expired OTPs")
                
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to cleanup expired OTPs: {str(e)}")
    
    def get_otp_status(self, email: str) -> dict:
        """
        Get the status of OTP for an email
        """
        try:
            otp_record = PasswordResetOTP.query.filter_by(
                email=email,
                is_used=False
            ).order_by(PasswordResetOTP.created_at.desc()).first()
            
            if not otp_record:
                return {
                    'has_otp': False,
                    'message': 'No active OTP found'
                }
            
            if otp_record.is_expired():
                return {
                    'has_otp': False,
                    'message': 'OTP has expired'
                }
            
            time_remaining = (otp_record.expires_at - datetime.utcnow()).total_seconds()
            
            return {
                'has_otp': True,
                'expires_at': otp_record.expires_at.isoformat(),
                'time_remaining_seconds': int(time_remaining),
                'message': f'OTP expires in {int(time_remaining // 60)} minutes'
            }
            
        except Exception as e:
            logger.error(f"Failed to get OTP status for {email}: {str(e)}")
            return {
                'has_otp': False,
                'message': 'Error checking OTP status'
            }

# Global OTP service instance
otp_service = OTPService()
