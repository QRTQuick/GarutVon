import os
import uuid
from PIL import Image
from backend.config import Config

class ImageConverterService:
    SUPPORTED_INPUT_FORMATS = {"PNG", "JPG", "JPEG", "WEBP", "BMP", "GIF", "TIFF", "ICO"}
    SUPPORTED_OUTPUT_FORMATS = {"PNG", "JPG", "WEBP", "BMP", "TIFF", "ICO"}
    
    # Mapping of conversions supported
    CONVERSIONS = {
        ("PNG", "JPG"): "png_to_jpg",
        ("PNG", "WEBP"): "png_to_webp",
        ("PNG", "BMP"): "png_to_bmp",
        ("PNG", "TIFF"): "png_to_tiff",
        ("PNG", "ICO"): "png_to_ico",
        ("JPG", "PNG"): "jpg_to_png",
        ("JPEG", "WEBP"): "jpg_to_webp",
        ("WEBP", "PNG"): "webp_to_png",
        ("BMP", "PNG"): "bmp_to_png",
        ("GIF", "PNG"): "gif_to_png",
        ("TIFF", "PNG"): "tiff_to_png",
        ("ICO", "PNG"): "ico_to_png"
    }

    @classmethod
    def validate_file(cls, filename, file_size):
        # 1. Check size limits
        if file_size > Config.MAX_CONTENT_LENGTH:
            return False, "File is too large. Maximum size is 16MB."
            
        # 2. Check extension
        ext = filename.split(".")[-1].upper() if "." in filename else ""
        if ext == "JPEG":
            ext = "JPG"
        if ext not in cls.SUPPORTED_INPUT_FORMATS:
            return False, f"Unsupported file extension: {ext}. We support PNG, JPG, JPEG, WEBP, BMP, GIF, TIFF, ICO."
            
        return True, ""

    @classmethod
    def validate_image_header(cls, file_path):
        """Perform actual MIME / header verification using PIL to verify if the file is truly a valid image."""
        try:
            with Image.open(file_path) as img:
                img.verify() # verifies image integrity
            return True, ""
        except Exception as e:
            return False, f"Invalid or corrupt image file: {str(e)}"

    @classmethod
    def convert_image(cls, input_path, target_format):
        """
        Converts input image at input_path into target_format.
        Returns the output path, output size, and content type.
        """
        target_format = target_format.upper()
        if target_format == "JPG" or target_format == "JPEG":
            target_format = "JPEG"
            ext = "jpg"
        else:
            ext = target_format.lower()
            
        out_filename = f"{uuid.uuid4().hex}.{ext}"
        os.makedirs(Config.OUTPUT_FOLDER, exist_ok=True)
        output_path = os.path.join(Config.OUTPUT_FOLDER, out_filename)
        
        try:
            with Image.open(input_path) as img:
                # Handle GIF: take first frame
                if img.format == "GIF":
                    img.seek(0)
                    img = img.convert("RGBA")
                
                # Handle alpha transparency channels when saving to JPG (which doesn't support alpha)
                if target_format == "JPEG" and img.mode in ("RGBA", "LA", "P"):
                    # Create white background to blend transparency onto
                    bg = Image.new("RGB", img.size, (255, 255, 255))
                    # Check if P mode has transparency or needs alpha conversion
                    if img.mode == "P":
                        img = img.convert("RGBA")
                    # Paste with transparency mask
                    if img.mode == "RGBA":
                        bg.paste(img, mask=img.split()[3])
                    else:
                        bg.paste(img)
                    img = bg
                elif target_format == "PNG" and img.mode not in ("RGB", "RGBA"):
                    img = img.convert("RGBA")
                elif target_format == "WEBP" and img.mode not in ("RGB", "RGBA"):
                    img = img.convert("RGBA")
                elif target_format == "BMP" and img.mode != "RGB":
                    img = img.convert("RGB")
                elif target_format == "TIFF" and img.mode not in ("RGB", "RGBA"):
                    img = img.convert("RGBA")
                elif target_format == "ICO":
                    # ICO files usually have specific sizes. We can resize or crop to 256x256 if too large.
                    img = img.convert("RGBA")
                    if img.width > 256 or img.height > 256:
                        img.thumbnail((256, 256))

                # Save based on format
                if target_format == "JPEG":
                    img.save(output_path, "JPEG", quality=90)
                elif target_format == "ICO":
                    img.save(output_path, "ICO", sizes=[(16,16), (32,32), (48,48), (256,256)])
                else:
                    img.save(output_path, target_format)
                    
            size = os.path.getsize(output_path)
            return True, output_path, out_filename, size
        except Exception as e:
            # Clean up if output file is created corruptly
            if os.path.exists(output_path):
                try:
                    os.remove(output_path)
                except Exception:
                    pass
            return False, str(e), "", 0
