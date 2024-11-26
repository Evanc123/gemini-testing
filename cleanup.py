import google.generativeai as genai
from google.generativeai import caching
import os

google_api_key = os.getenv("GOOGLE_API_KEY")

genai.configure(api_key=google_api_key)


print("My files:")
for f in genai.list_files():
    f.delete()
    print("  ", f.name)
