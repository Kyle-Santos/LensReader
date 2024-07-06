import pytest
from PyQt6.QtGui import QImage

from project import convert_grayscale, noise_reduction, resize_image


def test_noise_reduction():
    # Create a sample QImage for testing
    sample_image = QImage(100, 100, QImage.Format.Format_ARGB32)
    sample_image.fill(0xFF0000FF)  # Fill with semi-transparent blue color

    # Perform noise reduction
    result_image = noise_reduction(sample_image)

    # Assert general properties of the result image
    assert result_image.size() == sample_image.size()
    assert result_image.format() == sample_image.format()
    
    # Check that the result image is not entirely transparent
    assert result_image.hasAlphaChannel()

def test_convert_grayscale():
    # Create a sample image in ARGB32 format
    sample_image = QImage(100, 100, QImage.Format.Format_ARGB32)
    sample_image.fill(0xFF0000FF)  # Fill with semi-transparent blue color

    # Perform grayscale conversion
    result_image = convert_grayscale(sample_image)

    # Assert general properties of the result image
    assert result_image.size() == sample_image.size()
    assert result_image.format() == QImage.Format.Format_Grayscale8

    # Check a few pixels to ensure correct grayscale conversion
    assert result_image.pixelColor(0, 0).value() == 70  
    assert result_image.pixelColor(50, 50).value() == 70  
    assert result_image.pixelColor(99, 99).value() == 70  

    # Check that the result image does not have an alpha channel
    assert not result_image.hasAlphaChannel()

def test_resize_image():
    # Create a sample QPixmap for testing
    sample_image = QImage(100, 100, QImage.Format.Format_ARGB32)

    # Perform resizing
    result_image = resize_image(sample_image, 50)

    expected_result = QImage(50, 50, QImage.Format.Format_ARGB32)

    # Assert general properties of the result image
    assert result_image.size() == expected_result.size() 
    assert result_image.size() != sample_image.size()
