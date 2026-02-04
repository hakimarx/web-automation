"""
CAPTCHA Solver Module
Menggunakan OCR untuk solve CAPTCHA sederhana
"""

import io
import re
import requests
from PIL import Image
import logging

logger = logging.getLogger(__name__)

class CaptchaSolver:
    """CAPTCHA Solver menggunakan Tesseract OCR atau pytesseract"""
    
    def __init__(self):
        """Initialize CAPTCHA solver"""
        self.tesseract_available = self._check_tesseract()
    
    def _check_tesseract(self):
        """Check if Tesseract is available"""
        try:
            import pytesseract
            # Set path explicitly for Windows
            pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
            pytesseract.get_tesseract_version()
            return True
        except Exception:
            logger.warning("Tesseract OCR tidak tersedia, menggunakan fallback basic OCR")
            return False
    
    def preprocess_image(self, img):
        """Preprocess image for better OCR accuracy"""
        # Convert to grayscale
        if img.mode != 'L':
            img = img.convert('L')
            
        # Add Smooth filter (Critical for StarASN captcha)
        from PIL import ImageFilter
        img = img.filter(ImageFilter.SMOOTH)
        
        # Simple threshold
        threshold = 128
        img = img.point(lambda p: 255 if p > threshold else 0)
        
        return img
    
    def solve_from_url(self, url, cookies=None):
        """
        Download and solve CAPTCHA from URL
        
        Args:
            url: URL gambar CAPTCHA
            cookies: Dict cookies untuk authenticated request
        
        Returns:
            str: Teks CAPTCHA yang terdeteksi, atau None jika gagal
        """
        try:
            # Download image
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, cookies=cookies, timeout=10)
            response.raise_for_status()
            
            # Load image
            img = Image.open(io.BytesIO(response.content))
            
            return self.solve_image(img)
            
        except Exception as e:
            logger.error(f"Error downloading CAPTCHA: {e}")
            return None
    
    def solve_image(self, img, debug_save_path=None):
        """
        Solve CAPTCHA from PIL Image
        
        Args:
            img: PIL Image object
            debug_save_path: Optional path to save preprocessed image
            
        Returns:
            str: Teks CAPTCHA atau None
        """
        try:
            results = []
            
            # Helper to run OCR
            def run_ocr(image_obj, tag):
                if debug_save_path:
                    try:
                        image_obj.save(f"{debug_save_path}_{tag}.png")
                    except:
                        pass
                
                if self.tesseract_available:
                    import pytesseract
                    
                    # Try PSM 7 (Single line)
                    custom_config = r'--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                    text = pytesseract.image_to_string(image_obj, config=custom_config)
                    text = re.sub(r'[^A-Za-z0-9]', '', text).strip()
                    
                    # If PSM 7 is too short or too long, try PSM 8 (Single word) or PSM 6
                    if not (5 <= len(text) <= 6):
                        custom_config_8 = r'--oem 3 --psm 8 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                        text_8 = pytesseract.image_to_string(image_obj, config=custom_config_8)
                        text_8 = re.sub(r'[^A-Za-z0-9]', '', text_8).strip()
                        if 5 <= len(text_8) <= 6:
                            text = text_8
                        elif not text:
                             custom_config_6 = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                             text_6 = pytesseract.image_to_string(image_obj, config=custom_config_6)
                             text = re.sub(r'[^A-Za-z0-9]', '', text_6).strip()
                    
                    logger.info(f"OCR Strategy {tag} Result: {text}")
                    return text
                return None

            # Ensure grayscale
            if img.mode != 'L':
                base_img = img.convert('L')
            else:
                base_img = img.copy()

            from PIL import ImageFilter, ImageEnhance
            
            # Enhance contrast
            enhancer = ImageEnhance.Contrast(base_img)
            base_img = enhancer.enhance(2.0)
            
            # Enhance brightness
            enhancer = ImageEnhance.Brightness(base_img)
            base_img = enhancer.enhance(1.5)

            # Strategy 0: Color Filter (Specifically for StarASN's green text)
            try:
                rgb_img = img.convert('RGB')
                # Resize first to 2x for better precision
                rgb_img = rgb_img.resize((rgb_img.width * 2, rgb_img.height * 2), Image.Resampling.LANCZOS)
                data = rgb_img.getdata()
                new_data = []
                for item in data:
                    # If green is very dominant
                    if item[1] > item[0] + 30 and item[1] > item[2] + 30:
                        new_data.append(0) # Keep as black text
                    else:
                        new_data.append(255) # Make background white
                
                s0_img = Image.new('L', rgb_img.size)
                s0_img.putdata(new_data)
                res0 = run_ocr(s0_img, "color_filter_2x")
                if res0 and 5 <= len(res0) <= 6:
                    return res0
                if res0: results.append(res0)
            except Exception as e:
                logger.warning(f"Color filter failed: {e}")

            # Strategy 1: Smooth + Threshold (Best for connected lines)
            s1_img = base_img.filter(ImageFilter.SMOOTH)
            s1_img = s1_img.point(lambda p: 255 if p > 128 else 0)
            res1 = run_ocr(s1_img, "smooth")
            if res1 and 5 <= len(res1) <= 6:
                return res1
            if res1: results.append(res1)
            
            # Strategy 2: Simple Threshold (Fallback)
            s2_img = base_img.point(lambda p: 255 if p > 128 else 0)
            res2 = run_ocr(s2_img, "threshold")
            if res2 and 5 <= len(res2) <= 6:
                return res2
            if res2: results.append(res2)

            # Strategy 3: Median (Good for salt noise)
            s3_img = base_img.filter(ImageFilter.MedianFilter(size=3))
            s3_img = s3_img.point(lambda p: 255 if p > 128 else 0)
            res3 = run_ocr(s3_img, "median")
            if res3 and 5 <= len(res3) <= 6:
                return res3
            if res3: results.append(res3)

            # Strategy 4: Rescale + Denoise (Good for small, noisy images)
            # Resize image to 2x for better OCR
            s4_img = base_img.resize((base_img.width * 2, base_img.height * 2), Image.Resampling.LANCZOS)
            # Denoise
            s4_img = s4_img.filter(ImageFilter.MedianFilter(size=3))
            # Threshold
            s4_img = s4_img.point(lambda p: 255 if p > 140 else 0)
            res4 = run_ocr(s4_img, "denoise_2x")
            if res4 and 5 <= len(res4) <= 6:
                return res4
            if res4: results.append(res4)

            # Strategy 5: Sharpen + Threshold
            s5_img = base_img.filter(ImageFilter.SHARPEN)
            s5_img = s5_img.point(lambda p: 255 if p > 128 else 0)
            res5 = run_ocr(s5_img, "sharpen")
            if res5 and 5 <= len(res5) <= 6:
                return res5
            if res5: results.append(res5)

            # If no strategy yielded perfect length, return the best guess (longest or first)
            if results:
                # Prefer length 6, then 5
                results_6 = [r for r in results if len(r) == 6]
                if results_6:
                    return results_6[0]
                results_5 = [r for r in results if len(r) == 5]
                if results_5:
                    return results_5[0]
                
                # Fallback to longest
                best = max(results, key=len)
                logger.info(f"Fallback to best result: {best}")
                return best
                
            return None
                
        except Exception as e:
            logger.error(f"Error solving CAPTCHA: {e}")
            return None
    
    def solve_from_file(self, filepath):
        """
        Solve CAPTCHA from file path
        
        Args:
            filepath: Path ke file gambar
            
        Returns:
            str: Teks CAPTCHA atau None
        """
        try:
            img = Image.open(filepath)
            return self.solve_image(img)
        except Exception as e:
            logger.error(f"Error loading CAPTCHA file: {e}")
            return None


def manual_captcha_input():
    """
    Fungsi untuk input CAPTCHA manual dari user
    
    Returns:
        str: CAPTCHA yang diinput user
    """
    try:
        captcha = input("Masukkan CAPTCHA secara manual: ").strip()
        return captcha
    except Exception:
        return None


if __name__ == "__main__":
    # Test
    solver = CaptchaSolver()
    print(f"Tesseract available: {solver.tesseract_available}")
