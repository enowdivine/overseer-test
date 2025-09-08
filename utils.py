"""
Utility functions for the Cameroon Construction Project Management System
"""

import hashlib
import uuid
import datetime
import json
import re
import os
from typing import Dict, List, Any, Optional, Tuple


class ValidationUtils:
    """Utility class for data validation"""

    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate Cameroon phone number format"""
        # Remove all non-digits
        digits_only = re.sub(r'\D', '', phone)

        # Cameroon phone numbers typically start with 237 (country code)
        # and have 9 digits after country code
        if len(digits_only) == 12 and digits_only.startswith('237'):
            return True
        elif len(digits_only) == 9:
            return True

        return False

    @staticmethod
    def validate_password(password: str) -> Dict[str, bool]:
        """Validate password strength"""
        validations = {
            'length': len(password) >= 8,
            'has_upper': any(c.isupper() for c in password),
            'has_lower': any(c.islower() for c in password),
            'has_digit': any(c.isdigit() for c in password),
            'has_special': bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))
        }

        return validations

    @staticmethod
    def validate_price(price_str: str) -> Optional[float]:
        """Validate and parse price string"""
        try:
            # Remove commas and spaces
            clean_price = re.sub(r'[,\s]', '', price_str)
            price = float(clean_price)
            return price if price >= 0 else None
        except (ValueError, TypeError):
            return None


class CurrencyUtils:
    """Utility class for currency formatting and calculations"""

    @staticmethod
    def format_currency(amount: float, currency_code: str = 'XAF') -> str:
        """Format amount as currency"""
        if currency_code == 'XAF':
            return f"{amount:,.0f} FCFA"
        return f"{amount:,.2f} {currency_code}"

    @staticmethod
    def parse_currency(currency_str: str) -> Optional[float]:
        """Parse currency string to float"""
        try:
            # Remove currency symbols and spaces
            clean_str = re.sub(r'[^\d.,]', '', currency_str)
            clean_str = clean_str.replace(',', '')
            return float(clean_str)
        except (ValueError, TypeError):
            return None

    @staticmethod
    def calculate_tax(amount: float, tax_rate: float = 0.0) -> Dict[str, float]:
        """Calculate tax on amount"""
        tax_amount = amount * (tax_rate / 100)
        total_with_tax = amount + tax_amount

        return {
            'subtotal': amount,
            'tax_amount': tax_amount,
            'tax_rate': tax_rate,
            'total': total_with_tax
        }


class DateTimeUtils:
    """Utility class for date and time operations"""

    @staticmethod
    def format_date(date_obj: Any, format_str: str = '%d/%m/%Y') -> str:
        """Format datetime object to string"""
        if isinstance(date_obj, str):
            try:
                date_obj = datetime.datetime.fromisoformat(date_obj.replace('Z', '+00:00'))
            except ValueError:
                return date_obj

        return date_obj.strftime(format_str)

    @staticmethod
    def parse_date(date_str: str) -> Optional[datetime.datetime]:
        """Parse date string to datetime object"""
        formats = ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%Y-%m-%d %H:%M:%S']

        for format_str in formats:
            try:
                return datetime.datetime.strptime(date_str, format_str)
            except ValueError:
                continue

        return None

    @staticmethod
    def get_date_range(days: int = 30) -> Tuple[datetime.datetime, datetime.datetime]:
        """Get date range from today minus specified days to today"""
        end_date = datetime.datetime.now()
        start_date = end_date - datetime.timedelta(days=days)
        return start_date, end_date

    @staticmethod
    def is_business_day(date_obj: datetime.datetime) -> bool:
        """Check if date is a business day (Monday-Friday)"""
        return date_obj.weekday() < 5


class ReportUtils:
    """Utility class for report generation"""

    @staticmethod
    def generate_inventory_report(store_data: List[Dict]) -> Dict:
        """Generate inventory summary report"""
        total_items = len(store_data)
        total_value = sum(item.get('quantity', 0) * item.get('price', 0) for item in store_data)
        low_stock_items = [item for item in store_data if item.get('quantity', 0) < 10]

        categories: Dict[str, Dict[str, float]] = {}
        for item in store_data:
            category = item.get('category', 'Unknown')
            if category not in categories:
                categories[category] = {'count': 0, 'value': 0}
            categories[category]['count'] += 1
            categories[category]['value'] += item.get('quantity', 0) * item.get('price', 0)

        return {
            'total_items': total_items,
            'total_value': total_value,
            'low_stock_count': len(low_stock_items),
            'low_stock_items': low_stock_items,
            'categories': categories,
            'generated_date': datetime.datetime.now().isoformat()
        }

    @staticmethod
    def generate_sales_report(transactions: List[Dict], period_days: int = 30) -> Dict:
        """Generate sales summary report"""
        end_date = datetime.datetime.now()
        start_date = end_date - datetime.timedelta(days=period_days)

        period_transactions: List[Dict] = []
        for trans in transactions:
            trans_date = DateTimeUtils.parse_date(trans.get('transaction_date', ''))
            if trans_date and start_date <= trans_date <= end_date:
                period_transactions.append(trans)

        total_sales = len(period_transactions)
        total_revenue = sum(trans.get('total_amount', 0) for trans in period_transactions)
        avg_sale = total_revenue / total_sales if total_sales > 0 else 0

        # Group by date
        daily_sales: Dict[str, Dict[str, float]] = {}
        for trans in period_transactions:
            parsed = DateTimeUtils.parse_date(trans.get('transaction_date', ''))
            if parsed is None:
                continue
            date_key = DateTimeUtils.format_date(parsed)
            if date_key not in daily_sales:
                daily_sales[date_key] = {'count': 0, 'revenue': 0}
            daily_sales[date_key]['count'] += 1
            daily_sales[date_key]['revenue'] += trans.get('total_amount', 0)

        return {
            'period_days': period_days,
            'start_date': start_date.strftime('%d/%m/%Y'),
            'end_date': end_date.strftime('%d/%m/%Y'),
            'total_sales': total_sales,
            'total_revenue': total_revenue,
            'average_sale': avg_sale,
            'daily_breakdown': daily_sales
        }


class SecurityUtils:
    """Utility class for security operations"""

    @staticmethod
    def hash_password(password: str, salt: Optional[str] = None) -> tuple:
        """Hash password with salt"""
        if salt is None:
            salt = os.urandom(32).hex()

        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        )

        return password_hash.hex(), salt

    @staticmethod
    def verify_password(password: str, stored_hash: str, salt: str) -> bool:
        """Verify password against stored hash"""
        password_hash, _ = SecurityUtils.hash_password(password, salt)
        return password_hash == stored_hash

    @staticmethod
    def generate_session_token() -> str:
        """Generate secure session token"""
        return str(uuid.uuid4()) + str(uuid.uuid4()).replace('-', '')

    @staticmethod
    def is_safe_filename(filename: str) -> bool:
        """Check if filename is safe"""
        # Remove path separators and check for dangerous patterns
        safe_chars = re.match(r'^[a-zA-Z0-9._\-\s]+$', filename)
        no_dots = not filename.startswith('.') and '..' not in filename
        return bool(safe_chars and no_dots)


class FileUtils:
    """Utility class for file operations"""

    @staticmethod
    def ensure_directory(directory_path: str) -> bool:
        """Ensure directory exists, create if not"""
        try:
            os.makedirs(directory_path, exist_ok=True)
            return True
        except OSError:
            return False

    @staticmethod
    def get_file_size(file_path: str) -> int:
        """Get file size in bytes"""
        try:
            return os.path.getsize(file_path)
        except OSError:
            return 0

    @staticmethod
    def is_valid_file_type(filename: str, allowed_extensions: List[str]) -> bool:
        """Check if file type is allowed"""
        if not filename:
            return False

        extension = filename.lower().split('.')[-1]
        return extension in [ext.lower() for ext in allowed_extensions]

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename for safe storage"""
        # Remove invalid characters
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # Limit length
        if len(sanitized) > 255:
            name, ext = os.path.splitext(sanitized)
            sanitized = name[:255 - len(ext)] + ext

        return sanitized


class CalculationUtils:
    """Utility class for mathematical calculations"""

    @staticmethod
    def calculate_percentage_change(old_value: float, new_value: float) -> float:
        """Calculate percentage change between two values"""
        if old_value == 0:
            return 100.0 if new_value != 0 else 0.0

        return ((new_value - old_value) / old_value) * 100

    @staticmethod
    def calculate_compound_interest(principal: float, rate: float, time: float,
                                    compound_frequency: int = 12) -> float:
        """Calculate compound interest"""
        return principal * (1 + rate / compound_frequency) ** (compound_frequency * time)

    @staticmethod
    def calculate_material_requirements(area: float, material_coverage: float,
                                        waste_factor: float = 0.1) -> float:
        """Calculate material requirements with waste factor"""
        if material_coverage == 0:
            return 0.0
        basic_requirement = area / material_coverage
        with_waste = basic_requirement * (1 + waste_factor)
        return with_waste

    @staticmethod
    def round_to_nearest(value: float, nearest: float = 0.01) -> float:
        """Round value to nearest specified unit"""
        if nearest == 0:
            return value
        return round(value / nearest) * nearest


class DataExportUtils:
    """Utility class for data export operations"""

    @staticmethod
    def export_to_csv(data: List[Dict], filename: str) -> bool:
        """Export data to CSV file"""
        try:
            import csv

            if not data:
                return False

            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = list(data[0].keys())
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)

            return True
        except Exception:
            return False

    @staticmethod
    def export_to_json(data: Any, filename: str) -> bool:
        """Export data to JSON file"""
        try:
            with open(filename, 'w', encoding='utf-8') as jsonfile:
                json.dump(data, jsonfile, indent=2, ensure_ascii=False, default=str)

            return True
        except Exception:
            return False


class NotificationUtils:
    """Utility class for system notifications"""

    @staticmethod
    def create_notification(user_id: str, title: str, message: str,
                            notification_type: str = 'info', related_id: Optional[str] = None) -> Dict:
        """Create notification dictionary"""
        return {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'title': title,
            'message': message,
            'notification_type': notification_type,
            'created_date': datetime.datetime.now().isoformat(),
            'is_read': False,
            'related_id': related_id
        }

    @staticmethod
    def format_notification_message(template: str, **kwargs) -> str:
        """Format notification message with parameters"""
        try:
            return template.format(**kwargs)
        except KeyError:
            return template


# Configuration constants
class Constants:
    """System constants"""

    # File upload limits
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_IMAGE_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif']
    ALLOWED_DOCUMENT_EXTENSIONS = ['pdf', 'doc', 'docx', 'txt']

    # Pagination
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100

    # System limits
    MAX_FAILED_LOGIN_ATTEMPTS = 5
    SESSION_TIMEOUT_HOURS = 8
    PASSWORD_MIN_LENGTH = 8

    # Report periods
    REPORT_PERIODS = {
        'daily': 1,
        'weekly': 7,
        'monthly': 30,
        'quarterly': 90,
        'yearly': 365
    }

    # Material categories
    MATERIAL_CATEGORIES = [
        'Cement', 'Blocks', 'Steel', 'Timber', 'Roofing',
        'Electrical', 'Plumbing', 'Finishing', 'Tools',
        'Aggregates', 'Doors', 'Windows', 'Other'
    ]
