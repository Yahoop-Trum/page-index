import logging
import sys

try:
    import google.generativeai as genai
    print("google.generativeai imported successfully")
    print(f"Has GenerativeModel: {hasattr(genai, 'GenerativeModel')}")
except ImportError:
    print("google.generativeai NOT found")

try:
    import google.genai as genai
    print("google.genai imported successfully")
    print(f"Has GenerativeModel: {hasattr(genai, 'GenerativeModel')}")
except ImportError:
    print("google.genai NOT found")
