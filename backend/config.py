"""
TapQuote Configuration Settings
"""
import os
from dotenv import load_dotenv

load_dotenv()

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

# Pricing Configuration
LABOR_RATE = float(os.getenv("LABOR_RATE", "85.0"))  # $/hr
MATERIAL_MARKUP = float(os.getenv("MATERIAL_MARKUP", "20.0"))  # %

# Business Info (for PDF)
BUSINESS_NAME = os.getenv("BUSINESS_NAME", "TapQuote Electrical")
BUSINESS_ADDRESS = os.getenv("BUSINESS_ADDRESS", "123 Main Street, Sydney NSW 2000")
BUSINESS_PHONE = os.getenv("BUSINESS_PHONE", "(02) 1234 5678")
BUSINESS_EMAIL = os.getenv("BUSINESS_EMAIL", "quotes@tapquote.com.au")
TAX_RATE = float(os.getenv("TAX_RATE", "10.0"))  # GST %
