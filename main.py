import google.generativeai as genai
from google.generativeai import caching
from pdf2image import convert_from_path
import tempfile
import datetime
import time
import os
import json
from pathlib import Path

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


QUESTIONS = [
    {
        "id": "1",
        "query": "Where can I find information on towing?",
        "ground_truth_location": "page 27, 28",
        "ground_truth_answer": "N/A",
    },
    {
        "id": "2a",
        "query": "What are the steps to adjusting the hydraulic valve lifters?",
        "ground_truth_location": "page 133",
        "ground_truth_answer": """- back out adjusting screws in rocker arms until ball shaped end is flush with surface of arm
- turn crankshaft until cylinder No. 1 is at TDC
  - mark on rotor must be in line with mark on distributor housing
- turn adjusting screws in until they just touch valve stems
- turn adjusting screws 2 turns clockwise and tighen lock nuts
- rotate crankshaft 180° clockwise and adjust next cylinder
- repeat until all cylinders are adjusted""",
    },
    {
        "id": "2b",
        "query": "Show me the exploded schematic for the drive belt cover.",
        "ground_truth_location": "page 65",
        "ground_truth_answer": "N/A",
    },
    {
        "id": "3",
        "query": "What is the part number for a valve adjusting disc with thickness 3.40?",
        "ground_truth_location": "page 114",
        "ground_truth_answer": "056 109 563",
    },
]

NUM_TRIALS = 5


def print_result(question: dict, trial: int, chain_of_thought: str, answer: str):
    """Print a single trial result in a readable format"""
    print(f"\nQuestion {question['id']} (Trial {trial}):")
    print("-" * 40)
    print(f"Query: {question['query']}")
    print(f"Ground Truth Location: {question['ground_truth_location']}")
    print(f"Ground Truth Answer: {question['ground_truth_answer']}")
    print("\nModel Response:")
    print("Chain of Thought:")
    print(chain_of_thought)
    print("\nFinal Answer:")
    print(answer)
    print("-" * 40)


def save_results(results: list, output_file: str = "model_comparison_results"):
    """Save the results to both text and JSON formats"""
    # Save as formatted text
    with open(f"{output_file}.txt", "w") as f:
        f.write("Model Comparison Results\n")
        f.write("=" * 80 + "\n\n")

        for question in QUESTIONS:
            f.write(f"Question {question['id']}: {question['query']}\n")
            f.write("-" * 80 + "\n")
            f.write(f"Ground Truth Location: {question['ground_truth_location']}\n")
            f.write(f"Ground Truth Answer: {question['ground_truth_answer']}\n\n")

            # Write model responses for this question
            question_results = [
                r for r in results if r["question_id"] == question["id"]
            ]
            for i, result in enumerate(question_results, 1):
                f.write(f"Trial {i}:\n")
                f.write("Chain of Thought:\n")
                f.write(f"{result['chain_of_thought']}\n\n")
                f.write("Final Answer:\n")
                f.write(f"{result['answer']}\n\n")

            f.write("=" * 80 + "\n\n")

    # Save as JSON
    json_output = {"questions": QUESTIONS, "trials": results}
    with open(f"{output_file}.json", "w") as f:
        json.dump(json_output, f, indent=2)


def main():
    # Get the pages from cache or convert PDF
    pdf_path = "./data/manual_130.pdf"
    pages = get_cached_images(pdf_path)

    MAX_PAGES = len(pages)  # Allow all pages now
    # Get or upload files to Gemini
    uploaded_file_names = get_or_upload_files(
        pages, pdf_path=pdf_path, max_pages=MAX_PAGES
    )

    print("Creating interleaved content with page numbers...")
    uploaded_files = []
    for i, filename in enumerate(uploaded_file_names):
        # Add page number text
        page_num = i + 1
        uploaded_files.append(f"START OF ACTUAL PAGE NUMBER: {page_num}")
        # Add the image file
        uploaded_files.append(genai.get_file(filename))
        uploaded_files.append(f"END OF ACTUAL PAGE NUMBER: {page_num}\nBREAK\n")

    file_preamble = """
    Please answer questions with respect to the "ACTUAL_PAGE_NUMBER" indices, rather than the page numbers / section numbers in the manual itself. We *have* to use the actual page numbers because the manual itself does not have consistent page numbering.

    For questions, please answer with the page numbers where the actual answers occurs, rather than the section numbers referenced in the manual's table of contents for the question. 
"""

    print(f"Created content array with {len(uploaded_files)} items (text + images)")

    # Initialize model
    print("Initializing Gemini model...")
    model = genai.GenerativeModel(model_name="gemini-1.5-pro-002")

    # Run trials for each question
    results = []
    for question in QUESTIONS:
        print(f"\nProcessing question {question['id']}: {question['query']}")
        for trial in range(NUM_TRIALS):
            print(f"  Trial {trial + 1}/{NUM_TRIALS}", end="\r")
            try:
                prompt = f"""Based on the manual pages provided, answer the following question: {question['query']}

Please provide your response in two parts:
1. Page scan thoughts: Explain your reasoning process, including which pages you looked at and why. Please exhaustively check every page in the input, and talk about your thoughts about each set of 10 pages. Like, I will first look at 1-10. I see nothing related to my query here. I now processed 11-20, and so on for all of the input.
2. Chain of Thought: For the given pages, extract the page contents. If the answer is in a table or diagram, extract the entire table / diagram, so that you can clearly see the data you want to extract.
2(a): [Optional] Error Correction: If you made a mistake, or need to look at a different page, use this space to look at that page and extract data as needed. If no errors are detected, write "No errors detected".
3. Final Answer: Give the precise answer to the question, as well as the pages referenced (it is possible that the answer is simply pages).

Format your response exactly like this:
Chain of Thought:
[your detailed reasoning here]

Final Answer:
[your precise answer here]"""

                response = model.generate_content(
                    contents=[file_preamble] + uploaded_files + [prompt]
                )

                if response:
                    text = response.text
                    # Split the response into chain of thought and answer
                    try:
                        parts = text.split("Final Answer:")
                        if len(parts) != 2:
                            print(f"\nUnexpected response format: {text}")
                            continue

                        chain_of_thought = (
                            parts[0].replace("Chain of Thought:", "").strip()
                        )
                        answer = parts[1].strip()

                        result = {
                            "question_id": question["id"],
                            "trial": trial + 1,
                            "chain_of_thought": chain_of_thought,
                            "answer": answer,
                            "timestamp": datetime.datetime.now().isoformat(),
                        }
                        results.append(result)
                        print_result(question, trial + 1, chain_of_thought, answer)
                    except Exception as e:
                        print(
                            f"\nError processing response for question {question['id']}, trial {trial + 1}: {e}"
                        )
                        print(f"Raw response was: {text}")
            except Exception as e:
                print(
                    f"\nError generating content for question {question['id']}, trial {trial + 1}: {e}"
                )
            time.sleep(2)  # Delay between requests

    # Save results
    if results:
        save_results(results)
        print(
            "\nResults have been saved to model_comparison_results.txt and model_comparison_results.json"
        )
    else:
        print("\nNo valid results were collected to save")


if __name__ == "__main__":
    main()
