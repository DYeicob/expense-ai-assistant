import cv2
import numpy as np
from PIL import Image
import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)


def preprocess_image(image_path: str, target_size: Optional[Tuple[int, int]] = None) -> np.ndarray:
    """
    Preprocesses an image to improve OCR quality
    
    Args:
        image_path: Path to the image
        target_size: Target size (width, height), optional
        
    Returns:
        Processed image as a numpy array
    """
    try:
        # Read image
        image = cv2.imread(image_path)
        
        if image is None:
            raise ValueError(f"Could not read image: {image_path}")
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Resize if necessary
        if target_size:
            gray = cv2.resize(gray, target_size)
        
        # Apply bilateral filter to reduce noise while maintaining edges
        denoised = cv2.bilateralFilter(gray, 9, 75, 75)
        
        # Enhance contrast using CLAHE
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(denoised)
        
        # Adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            enhanced,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11,
            2
        )
        
        # Morphological operations for cleaning
        kernel = np.ones((1, 1), np.uint8)
        cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        
        return cleaned
        
    except Exception as e:
        logger.error(f"Preprocessing error: {e}")
        # Return original image in grayscale if it fails
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        return image


def rotate_image(image: np.ndarray, angle: float) -> np.ndarray:
    """
    Rotates an image by a given angle
    
    Args:
        image: Image as a numpy array
        angle: Rotation angle in degrees
        
    Returns:
        Rotated image
    """
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h), 
                             flags=cv2.INTER_CUBIC,
                             borderMode=cv2.BORDER_REPLICATE)
    
    return rotated


def deskew_image(image: np.ndarray) -> np.ndarray:
    """
    Corrects image skew
    
    Args:
        image: Image as a numpy array
        
    Returns:
        Corrected image
    """
    # Detect the skew angle
    coords = np.column_stack(np.where(image > 0))
    angle = cv2.minAreaRect(coords)[-1]
    
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
    
    # Rotate the image
    return rotate_image(image, angle)


def remove_shadows(image: np.ndarray) -> np.ndarray:
    """
    Removes shadows from the image
    
    Args:
        image: Image as a numpy array
        
    Returns:
        Image without shadows
    """
    # Convert to appropriate format
    if len(image.shape) == 3:
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    else:
        rgb = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
    
    # Dilate the image
    dilated = cv2.dilate(rgb, np.ones((7, 7), np.uint8))
    
    # Apply median blur
    bg = cv2.medianBlur(dilated, 21)
    
    # Calculate the difference
    diff = 255 - cv2.absdiff(rgb, bg)
    
    # Normalize
    norm = cv2.normalize(diff, None, alpha=0, beta=255, 
                        norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U)
    
    # Convert back to grayscale
    gray = cv2.cvtColor(norm, cv2.COLOR_RGB2GRAY)
    
    return gray


def enhance_receipt_image(image_path: str) -> np.ndarray:
    """
    Full enhancement pipeline for receipt images
    
    Args:
        image_path: Path to the image
        
    Returns:
        Enhanced image
    """
    # Read image
    image = cv2.imread(image_path)
    
    # Remove shadows
    no_shadow = remove_shadows(image)
    
    # Correct skew
    deskewed = deskew_image(no_shadow)
    
    # Preprocess
    processed = preprocess_image(image_path)
    
    return processed


def crop_to_content(image: np.ndarray, padding: int = 10) -> np.ndarray:
    """
    Crops the image to the relevant content
    
    Args:
        image: Image as a numpy array
        padding: Padding pixels around the content
        
    Returns:
        Cropped image
    """
    # Find contours
    coords = cv2.findNonZero(image)
    
    if coords is not None:
        x, y, w, h = cv2.boundingRect(coords)
        
        # Add padding
        x = max(0, x - padding)
        y = max(0, y - padding)
        w = min(image.shape[1] - x, w + 2 * padding)
        h = min(image.shape[0] - y, h + 2 * padding)
        
        # Crop
        cropped = image[y:y+h, x:x+w]
        return cropped
    
    return image


def resize_if_too_large(image: np.ndarray, max_dimension: int = 2000) -> np.ndarray:
    """
    Resizes the image if it is too large
    
    Args:
        image: Image as a numpy array
        max_dimension: Maximum allowed dimension
        
    Returns:
        Resized image if necessary
    """
    h, w = image.shape[:2]
    
    if max(h, w) > max_dimension:
        scale = max_dimension / max(h, w)
        new_w = int(w * scale)
        new_h = int(h * scale)
        
        resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)
        return resized
    
    return image


def save_processed_image(image: np.ndarray, output_path: str):
    """
    Saves a processed image
    
    Args:
        image: Image as a numpy array
        output_path: Output path
    """
    cv2.imwrite(output_path, image)
    logger.info(f"Processed image saved at: {output_path}")
