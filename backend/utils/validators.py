"""
Validadores para la aplicación
"""
from datetime import datetime, timedelta
from typing import Optional
import re


class ValidationError(Exception):
    """Excepción personalizada para errores de validación"""
    pass


def validate_amount(amount: float, min_value: float = 0.01, max_value: float = 1000000) -> bool:
    """
    Valida que un monto sea válido
    
    Args:
        amount: Monto a validar
        min_value: Valor mínimo permitido
        max_value: Valor máximo permitido
        
    Returns:
        True si es válido
        
    Raises:
        ValidationError: Si el monto no es válido
    """
    if amount is None:
        raise ValidationError("El monto es requerido")
    
    if not isinstance(amount, (int, float)):
        raise ValidationError("El monto debe ser un número")
    
    if amount < min_value:
        raise ValidationError(f"El monto debe ser mayor o igual a {min_value}")
    
    if amount > max_value:
        raise ValidationError(f"El monto debe ser menor o igual a {max_value}")
    
    return True


def validate_date(
    date: datetime,
    allow_future: bool = False,
    max_past_days: Optional[int] = 365
) -> bool:
    """
    Valida una fecha
    
    Args:
        date: Fecha a validar
        allow_future: Si se permiten fechas futuras
        max_past_days: Máximo de días en el pasado (None = sin límite)
        
    Returns:
        True si es válida
        
    Raises:
        ValidationError: Si la fecha no es válida
    """
    if date is None:
        raise ValidationError("La fecha es requerida")
    
    if not isinstance(date, datetime):
        raise ValidationError("La fecha debe ser un objeto datetime")
    
    now = datetime.now()
    
    # Verificar si es futura
    if not allow_future and date > now:
        raise ValidationError("La fecha no puede ser en el futuro")
    
    # Verificar antigüedad
    if max_past_days is not None:
        max_date = now - timedelta(days=max_past_days)
        if date < max_date:
            raise ValidationError(f"La fecha no puede ser más antigua que {max_past_days} días")
    
    return True


def validate_category_id(category_id: int) -> bool:
    """
    Valida un ID de categoría
    
    Args:
        category_id: ID a validar
        
    Returns:
        True si es válido
        
    Raises:
        ValidationError: Si no es válido
    """
    if category_id is None:
        raise ValidationError("La categoría es requerida")
    
    if not isinstance(category_id, int):
        raise ValidationError("El ID de categoría debe ser un entero")
    
    if category_id <= 0:
        raise ValidationError("El ID de categoría debe ser positivo")
    
    return True


def validate_merchant_name(merchant: str, min_length: int = 2, max_length: int = 255) -> bool:
    """
    Valida el nombre de un comercio
    
    Args:
        merchant: Nombre del comercio
        min_length: Longitud mínima
        max_length: Longitud máxima
        
    Returns:
        True si es válido
        
    Raises:
        ValidationError: Si no es válido
    """
    if merchant is None:
        return True  # Merchant es opcional
    
    if not isinstance(merchant, str):
        raise ValidationError("El nombre del comercio debe ser texto")
    
    merchant = merchant.strip()
    
    if len(merchant) < min_length:
        raise ValidationError(f"El nombre del comercio debe tener al menos {min_length} caracteres")
    
    if len(merchant) > max_length:
        raise ValidationError(f"El nombre del comercio no puede exceder {max_length} caracteres")
    
    return True


def validate_description(description: str, max_length: int = 1000) -> bool:
    """
    Valida una descripción
    
    Args:
        description: Descripción a validar
        max_length: Longitud máxima
        
    Returns:
        True si es válida
        
    Raises:
        ValidationError: Si no es válida
    """
    if description is None:
        return True  # Descripción es opcional
    
    if not isinstance(description, str):
        raise ValidationError("La descripción debe ser texto")
    
    if len(description) > max_length:
        raise ValidationError(f"La descripción no puede exceder {max_length} caracteres")
    
    return True


def validate_payment_method(payment_method: str) -> bool:
    """
    Valida un método de pago
    
    Args:
        payment_method: Método de pago
        
    Returns:
        True si es válido
        
    Raises:
        ValidationError: Si no es válido
    """
    valid_methods = [
        "efectivo",
        "tarjeta_debito",
        "tarjeta_credito",
        "transferencia",
        "paypal",
        "bizum",
        "otro"
    ]
    
    if payment_method is None:
        return True  # Opcional
    
    if not isinstance(payment_method, str):
        raise ValidationError("El método de pago debe ser texto")
    
    if payment_method.lower() not in valid_methods:
        raise ValidationError(
            f"Método de pago no válido. Opciones: {', '.join(valid_methods)}"
        )
    
    return True


def validate_file_size(file_size: int, max_size: int = 10 * 1024 * 1024) -> bool:
    """
    Valida el tamaño de un archivo
    
    Args:
        file_size: Tamaño en bytes
        max_size: Tamaño máximo permitido (por defecto 10MB)
        
    Returns:
        True si es válido
        
    Raises:
        ValidationError: Si el archivo es muy grande
    """
    if file_size > max_size:
        max_mb = max_size / (1024 * 1024)
        raise ValidationError(f"El archivo no puede exceder {max_mb:.1f}MB")
    
    return True


def validate_file_extension(filename: str, allowed_extensions: list = None) -> bool:
    """
    Valida la extensión de un archivo
    
    Args:
        filename: Nombre del archivo
        allowed_extensions: Lista de extensiones permitidas
        
    Returns:
        True si es válida
        
    Raises:
        ValidationError: Si la extensión no es válida
    """
    if allowed_extensions is None:
        allowed_extensions = ["jpg", "jpeg", "png", "pdf"]
    
    if not filename:
        raise ValidationError("El nombre de archivo es requerido")
    
    # Obtener extensión
    ext = filename.split('.')[-1].lower()
    
    if ext not in allowed_extensions:
        raise ValidationError(
            f"Extensión no válida. Permitidas: {', '.join(allowed_extensions)}"
        )
    
    return True


def validate_confidence_score(confidence: float) -> bool:
    """
    Valida un score de confianza
    
    Args:
        confidence: Score entre 0 y 1
        
    Returns:
        True si es válido
        
    Raises:
        ValidationError: Si no es válido
    """
    if confidence is None:
        return True  # Opcional
    
    if not isinstance(confidence, (int, float)):
        raise ValidationError("La confianza debe ser un número")
    
    if confidence < 0 or confidence > 1:
        raise ValidationError("La confianza debe estar entre 0 y 1")
    
    return True


def validate_email(email: str) -> bool:
    """
    Valida un email
    
    Args:
        email: Email a validar
        
    Returns:
        True si es válido
        
    Raises:
        ValidationError: Si no es válido
    """
    if not email:
        raise ValidationError("El email es requerido")
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(pattern, email):
        raise ValidationError("El formato del email no es válido")
    
    return True


def validate_password(password: str, min_length: int = 8) -> bool:
    """
    Valida una contraseña
    
    Args:
        password: Contraseña a validar
        min_length: Longitud mínima
        
    Returns:
        True si es válida
        
    Raises:
        ValidationError: Si no es válida
    """
    if not password:
        raise ValidationError("La contraseña es requerida")
    
    if len(password) < min_length:
        raise ValidationError(f"La contraseña debe tener al menos {min_length} caracteres")
    
    # Verificar que contenga al menos una letra y un número
    has_letter = any(c.isalpha() for c in password)
    has_number = any(c.isdigit() for c in password)
    
    if not (has_letter and has_number):
        raise ValidationError("La contraseña debe contener letras y números")
    
    return True


class ExpenseValidator:
    """Validador completo para gastos"""
    
    @staticmethod
    def validate_expense_data(expense_data: dict) -> bool:
        """
        Valida todos los datos de un gasto
        
        Args:
            expense_data: Diccionario con datos del gasto
            
        Returns:
            True si todo es válido
            
        Raises:
            ValidationError: Si algún dato no es válido
        """
        # Validar campos requeridos
        if 'date' in expense_data:
            validate_date(expense_data['date'])
        
        if 'category_id' in expense_data:
            validate_category_id(expense_data['category_id'])
        
        if 'amount' in expense_data:
            validate_amount(expense_data['amount'])
        
        # Validar campos opcionales
        if 'merchant' in expense_data and expense_data['merchant']:
            validate_merchant_name(expense_data['merchant'])
        
        if 'description' in expense_data and expense_data['description']:
            validate_description(expense_data['description'])
        
        if 'payment_method' in expense_data and expense_data['payment_method']:
            validate_payment_method(expense_data['payment_method'])
        
        if 'confidence' in expense_data and expense_data['confidence']:
            validate_confidence_score(expense_data['confidence'])
        
        return True
