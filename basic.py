import google.generativeai as genai
from pdf2image import convert_from_path
import os

# Configure API key
google_api_key = os.getenv("GOOGLE_API_KEY")
if not google_api_key:
    print("Warning: GOOGLE_API_KEY not found in environment variables!")
else:
    print("Successfully loaded Google API key")

genai.configure(api_key=google_api_key)

# Define the main prompt template with example
MAIN_PROMPT = """Based on the manual pages provided, answer the following question: {query}

Please provide your response in two parts:
1. Page Scan: Explain your reasoning process, including which pages you looked at and why. Please exhaustively check every page in the input, and talk about your thoughts about each set of 10 pages. Like, I will first look at 1-10. I see nothing related to my query here. I now processed 11-20, and so on for all of the input.
2. Chain of Thought: For the given pages, extract the page contents. If the answer is in a table or diagram, extract the entire table / diagram, so that you can clearly see the data you want to extract.
3. Error Correction: If you made a mistake, or need to look at a different page, use this space to look at that page and extract data as needed. If no errors are detected, write "No errors detected".
4. Final Answer: Give the precise answer to the question, as well as the pages referenced (it is possible that the answer is simply pages).

Here is an example of chain of thought and a final answer for reference:
<example-1>
Query: What is the CO content at idle?

1. Page Scan

It looks like there are 136 pages in total, so I'll sweep through them by 10s.

Pages 1-10: These pages contain the cover, title page, copyright information, table of contents, and foreword. Nothing related to the CO content at idle.

Pages 11-20: These pages contain the index and general vehicle information like model identification and VIN locations.  Nothing related to the CO content at idle.

Pages 21-30: These pages continue with general information and begin engine specifications. Page 30 contains idle speed and ignition settings for the air-cooled engine with AFC (Automatic Fuel Control), but no CO content.

Pages 31-40: These pages continue with engine specifications. Page 31 contains idle speed and ignition settings for the California air-cooled engine with AFC, but no CO content. Page 32 has similar information for the water-cooled Digifant engine.

Pages 41-50: These pages cover engine assembly/removal procedures. No information on CO content.

Pages 51-60:  These pages cover engine - crankshaft/crankcase disassembly/assembly for the air-cooled engine. No CO content mentioned.

Pages 61-70: More engine-crankshaft/crankcase information for air-cooled and diesel engines.  Still no CO information.

Pages 71-80: Still on engine - crankshaft/crankcase information, covering both Diesel and water-cooled engines.  No CO content.

Pages 81-90:  More of engine - crankshaft/crankcase. No CO content.

Pages 91-100: More engine crankshaft and crankcase information, but nothing related to CO content at idle.

Pages 101-110: More engine crankshaft and crankcase information. Page 110 shows the procedure for adjusting hydraulic valve lifters on the air-cooled engine. No information on CO content.

Pages 111-120: Continue with cylinder head and valve drive information. Still no information about CO content.

Pages 121-130: Continue with engine cylinder head information, including checking compression. Still no CO information.

Pages 131-136: There seems to be nothing related to my query in this range either.
----

2. Chain of Thought
After looking through all pages, the idle CO content looks to be on page 44. It looks like this data appears in a table, so I'll extract the table first.

| **Technical Data/Specified Values** | **Details**                                      |
|-------------------------------------|--------------------------------------------------|
| **Engine Code**                     | MV                                               |
| **Type**                            | 2.1 liter 70 kW 90 SAE net HP                    |
| **Introduction**                    | October 1985                                     |
| **Part No.** (Control unit)         | 025 906 222                                      |
|-------------------------------------|--------------------------------------------------|
| **Ignition Timing Checking Spec.**  | 3-7° before TDC                                  |
| **Ignition Timing Adjusting Spec.** | 5 ± 1° before TDC                                |
| **Test and adjustment conditions**  | 1 and 9                                          |
|-------------------------------------|--------------------------------------------------|
| **Idle Adjustment idle rpm**        | 880 ± 50 rpm                                     |
| **Idle Adjustment CO content**      | 0.7 ± 0.4 Vol. %                                 |
|-------------------------------------|--------------------------------------------------|
| **Test and Adjustment Conditions**  | 1 to 6, 7, 8                                     |

With the table extracted, I can see that the idle CO content is 0.7 ± 0.4 Vol. %.

3. Error Correction
I'll double check the pages that could be relevant, but it looks like this should be the correct answer. I just double checked the values in the table,
and it looks like 0.7 ± 0.4 Vol. % is the correct value.

4. Final Answer
The idle CO content is 0.7 ± 0.4 Vol. %.
<page-references>
44
</page-references>
</example-1>
"""

# Convert PDF to images
print("Converting PDF to images...")
pdf_path = "./data/manual_130_numbered.pdf"
pages = convert_from_path(pdf_path)
print(f"Successfully converted {len(pages)} pages")

# Upload files to Gemini
print("Uploading files to Gemini...")
uploaded_files = []
for i, page in enumerate(pages):
    # Add page number text
    page_num = i + 1
    uploaded_files.append(f"START OF ACTUAL PAGE NUMBER: {page_num}")
    # Save and upload the image
    image_path = f"temp_page_{i + 1}.jpg"
    page.save(image_path, "JPEG")
    uploaded_file = genai.upload_file(image_path)
    uploaded_files.append(genai.get_file(uploaded_file.name))
    uploaded_files.append(f"END OF ACTUAL PAGE NUMBER: {page_num}\nBREAK\n")
    os.remove(image_path)  # Clean up temp file

# Initialize model
model = genai.GenerativeModel(model_name="gemini-1.5-pro-002")

# File preamble for context
file_preamble = """
Please answer questions with respect to the "ACTUAL_PAGE_NUMBER" indices, rather than the page numbers in the manual itself.
Please provide the actual page numbers where the answer occurs in your response.
"""

# Question 1: Towing information
print("\nProcessing question about towing information...")
prompt = MAIN_PROMPT.format(query="Where can I find information on towing?")
response = model.generate_content(contents=[file_preamble] + uploaded_files + [prompt])
if response:
    print("\nResponse:")
    print(response.text)
    print("-" * 80)

# Question 2: Hydraulic valve lifters
print("\nProcessing question about hydraulic valve lifters...")
prompt = MAIN_PROMPT.format(
    query="What are the steps to adjusting the hydraulic valve lifters?"
)
response = model.generate_content(contents=[file_preamble] + uploaded_files + [prompt])
if response:
    print("\nResponse:")
    print(response.text)
    print("-" * 80)

# Question 3: Drive belt cover schematic
print("\nProcessing question about drive belt cover schematic...")
prompt = MAIN_PROMPT.format(
    query="Show me the exploded schematic for the drive belt cover."
)
response = model.generate_content(contents=[file_preamble] + uploaded_files + [prompt])
if response:
    print("\nResponse:")
    print(response.text)
    print("-" * 80)

# Question 4: Valve adjusting disc
print("\nProcessing question about valve adjusting disc...")
prompt = MAIN_PROMPT.format(
    query="What is the part number for a valve adjusting disc with thickness 3.40?"
)
response = model.generate_content(contents=[file_preamble] + uploaded_files + [prompt])
if response:
    print("\nResponse:")
    print(response.text)
    print("-" * 80)
