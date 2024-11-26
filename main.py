import google.generativeai as genai
from google.generativeai import caching
from pdf2image import convert_from_path
import tempfile
import datetime
import time
import pandas as pd
import typing_extensions as typing
from typing import Literal
import os
import json
import matplotlib.pyplot as plt
import math
from pathlib import Path

print("Starting manual processing application...")


class InformationSegment(typing.TypedDict):
    contributing_information: str
    contributing_information_type: Literal["text", "diagram", "table"]


class Page(typing.TypedDict):
    manual_page_num: str
    information_segements: list[InformationSegment]


class Response(typing.TypedDict):
    relevant_pages: list[Page]
    query_answer: str


# Fetch the GOOGLE_API_KEY from environment variables
google_api_key = os.getenv("GOOGLE_API_KEY")
if not google_api_key:
    print("Warning: GOOGLE_API_KEY not found in environment variables!")
else:
    print("Successfully loaded Google API key")

genai.configure(api_key=google_api_key)


def get_cached_images(pdf_path: str, cache_dir: str = "cached_images") -> list:
    """
    Get images from cache if they exist, otherwise convert PDF and cache them.

    Args:
        pdf_path (str): Path to the PDF file
        cache_dir (str): Directory to store cached images

    Returns:
        list: List of PIL Image objects
    """
    # Create cache directory if it doesn't exist
    cache_path = Path(cache_dir)
    cache_path.mkdir(exist_ok=True)

    # Create PDF-specific subdirectory
    pdf_name = Path(pdf_path).stem
    pdf_cache_path = cache_path / pdf_name
    pdf_cache_path.mkdir(exist_ok=True)

    # Generate a unique cache key based on PDF path and modification time
    pdf_stat = os.stat(pdf_path)
    pdf_modified_time = pdf_stat.st_mtime

    # Check if cached images exist and are up to date
    cache_info_file = pdf_cache_path / "cache_info.json"
    if cache_info_file.exists():
        with open(cache_info_file, "r") as f:
            cache_info = json.load(f)
            if cache_info.get("pdf_modified_time") == pdf_modified_time:
                print("Found valid cached images, loading from disk...")
                from PIL import Image

                cached_images = []
                for i in range(cache_info["num_pages"]):
                    image_path = pdf_cache_path / f"page_{i+1}.jpg"
                    if image_path.exists():
                        cached_images.append(Image.open(image_path))
                print(f"Successfully loaded {len(cached_images)} cached images")
                return cached_images

    print(f"Converting PDF to images: {pdf_path}")
    pages = convert_from_path(pdf_path)
    print(f"Successfully converted {len(pages)} pages from PDF")

    # Cache the newly converted images
    print("Caching converted images to disk...")
    for i, page in enumerate(pages):
        image_path = pdf_cache_path / f"page_{i+1}.jpg"
        page.save(image_path, "JPEG")
        print(f"Caching page {i + 1}/{len(pages)}", end="\r")

    # Save cache info
    cache_info = {"pdf_modified_time": pdf_modified_time, "num_pages": len(pages)}
    with open(cache_info_file, "w") as f:
        json.dump(cache_info, f)

    print("\nSuccessfully cached all pages")
    return pages


def get_or_upload_files(
    pages, pdf_path: str, cache_dir: str = "cached_images", max_pages: int = 10
) -> list:
    """
    Get or upload files to Gemini, using cached filenames if they exist and are valid.
    Returns list of uploaded file names.
    """
    cache_path = Path(cache_dir)
    cache_path.mkdir(exist_ok=True)

    # Create PDF-specific subdirectory
    pdf_name = Path(pdf_path).stem
    pdf_cache_path = cache_path / pdf_name
    pdf_cache_path.mkdir(exist_ok=True)

    # Check for cached filenames
    filename_cache = pdf_cache_path / "uploaded_filenames.json"
    if filename_cache.exists():
        print("Found cached upload filenames, verifying they still exist...")
        with open(filename_cache, "r") as f:
            cached_names = json.load(f)

        # Test the first filename to see if it's still valid
        try:
            test_file = genai.get_file(cached_names[0])
            print("Cached filenames are still valid, using them...")
            return cached_names[:max_pages]  # Return only first max_pages names
        except Exception as e:
            print(f"Cached filenames are invalid ({str(e)}), will re-upload files...")

    # If we get here, we need to upload the files
    uploaded_names = []
    print("Starting temporary file processing...")
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Created temporary directory at: {temp_dir}")
        for i, page in enumerate(pages[:max_pages]):
            image_path = f"{temp_dir}/page_{i + 1}.jpg"
            page.save(image_path, "JPEG")
            print(f"Processing page {i + 1}/{min(len(pages), max_pages)}", end="\r")

            uploaded_file = genai.upload_file(image_path)
            uploaded_names.append(uploaded_file.name)

    print("\nSuccessfully processed first 10 pages")

    # Cache the filenames
    with open(filename_cache, "w") as f:
        json.dump(uploaded_names, f)
    print("Cached upload filenames for future use")

    return uploaded_names


# Get the pages from cache or convert PDF
pdf_path = "./data/manual_130.pdf"
pages = get_cached_images(pdf_path)

MAX_PAGES = len(pages)
# Get or upload files to Gemini
uploaded_file_names = get_or_upload_files(pages, pdf_path=pdf_path, max_pages=MAX_PAGES)

print("Creating interleaved content with page numbers...")
uploaded_files = []
for i, filename in enumerate(uploaded_file_names):
    # Add page number text
    page_num = i + 1
    uploaded_files.append(f"ACTUAL PAGE NUMBER: {page_num}")
    # Add the image file
    uploaded_files.append(genai.get_file(filename))

print(f"Created content array with {len(uploaded_files)} items (text + images)")

system_instruction = (
    "You are an expert in machine repair using manuals, and your job is to answer "
    "the user's query based on the images of machine manual pages you have access to. "
    "Ensure your answer is detailed and directly references relevant instructions from the manual. "
    "The page number is provided before each image with the text 'ACTUAL PAGE NUMBER: X'."
)

# skipping for now, running into some sort of api rate limit
# Cache context
# print("Creating cache context...")
# cache = caching.CachedContent.create(
#     model="models/gemini-1.5-pro-002",
#     display_name="manual 130",
#     system_instruction=(
#         "You are an expert in machine repair using manuals, and your job is to answer "
#         "the user's query based on the images of machine manual pages you have access to. "
#         "Ensure your answer is detailed and directly references relevant instructions from the manual. "
#         "The page number is provided before each image with the text 'ACTUAL PAGE NUMBER: X'."
#     ),
#     contents=uploaded_files,
#     ttl=datetime.timedelta(hours=2),
# )
# print("Cache context created successfully")

# Construct model that uses caching
print("Initializing Gemini model...")
model = genai.GenerativeModel(
    model_name="gemini-1.5-pro-002",
    system_instruction=system_instruction,
)
print("Model initialized successfully")

prompt = "QUESTION: Describe the diagram of page 23"
print(f"\nGenerating response for query: {prompt}")
response = model.generate_content(
    contents=uploaded_files + [prompt],
    generation_config=genai.GenerationConfig(
        response_mime_type="text/plain",
        # response_mime_type="application/json", response_schema=Response
    ),
)
print("Response generated successfully")
print(response)


def extract_page_numbers(response):
    """
    Extracts page numbers from the response.

    Args:
        response (GenerateContentResponse): The response containing relevant page numbers.

    Returns:
        list: A list of zero-based page indexes.
    """
    try:
        print("Extracting page numbers from response...")
        # Extract the JSON string from the response content
        json_string = response.candidates[0].content.parts[0].text
        response_data = json.loads(json_string)

        # Extract relevant pages
        relevant_pages = response_data.get("relevant_pages", [])
        print(f"Found {len(relevant_pages)} relevant pages")

        # Convert manual page numbers to zero-based indexes
        page_numbers = [int(page["manual_page_num"]) - 1 for page in relevant_pages]
        answer = response_data.get("query_answer")
        return page_numbers, answer
    except (KeyError, json.JSONDecodeError) as e:
        print(f"Error extracting page numbers: {e}")
        return [], None


# page_nums, answer = extract_page_numbers(response)
# print("\nAnswer from the manual:")
# print("-" * 80)
# print(answer)
# print("-" * 80)
# print("\nDisplaying relevant pages...")
# display_selected_pages(pages, page_nums)
