MAIN_PROMPT = """Based on the manual pages provided, answer the following question: {query}

Please provide your response into four parts:
1. Page Scan: Explain your reasoning process, including which pages you looked at and why. Please exhaustively check every page in the input, and talk about your thoughts about each set of 10 pages. Like, I will first look at 1-10. I see nothing related to my query here. I now processed 11-20, and so on for all of the input.
2. Extraction: For the given pages, extract the page contents. If the answer is in a table or diagram, extract the entire table / diagram, so that you can clearly see the data you want to extract.
3. Error Correction: If you made a mistake, or need to look at a different page, use this space to look at that page and extract data as needed. If no errors are detected, write "No errors detected", and list the final list of pages that you plan on returning. 
4. Final Answer: Give the precise answer to the question, as well as the pages referenced (it is possible that the answer is simply pages).

At the end, include the final answer within
<final-answer></final-answer> tags, and the page references in 
<page-references></page-references> tags. Only include pages that you used to answer the question, not pages that helped you find the most relevant pages.

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

2. Extraction
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
and it looks like 0.7 ± 0.4 Vol. % is the correct value. It looks like I only used page 44 for this, so I'll just return that.

4. Final Answer
<final-answer>
The idle CO content is 0.7 ± 0.4 Vol. %.
</final-answer>
<page-references>
44
</page-references>
</example-1>
"""


example_2 = """
<example-2>
Query: Where can I find information on the Sunroof?

1. Page Scan

It looks like there are 136 pages in total, so I'll sweep through them by 10s.

Pages 1-10: These pages are the cover, title page, copyright, table of contents, and foreword. No sunroof information.

Pages 11-20: The index on pages 9-18 and continuation on 20 doesn't list "sunroof" explicitly, but I'll keep an eye out for related terms like "roof" or "top."

Pages 21-30: These pages cover general information, engine identification and some specifications. No mention of the sunroof.

Pages 31-40: These pages continue with engine removal and installation procedures. No sunroof information here.

Pages 41-50: These pages continue covering engine-related procedures. No sunroof information.

Pages 51-60: These pages deal with air-cooled engine components. No sunroof information.

Pages 61-70: Still working through the air-cooled engine section and the diesel engine section. Nothing on the sunroof.

Pages 71-80: More on engine crankshaft and crankcase, now including water-cooled engines. Still no sunroof.

Pages 81-90: Still engine-related content, but nothing about the sunroof.

Pages 91-100: These pages continue on crankshaft/crankcase information. Nothing related to the sunroof is present.

Pages 101-110: These pages cover crankshaft/crankcase information, including replacing procedures. No sunroof details.

Pages 111-120: Cylinder head and valve drive information is covered in these pages.  Still no mention of the sunroof.

Pages 121-130: More information on cylinder heads and pushrod tubes. No sunroof information.

Pages 131-140: Final pages related to cylinder heads.  No sunroof information is present.
----

Pages 4-5 Table of Contents: It contains information on the body which contains an entry for Sunroof. This entry on Sunroof covers pages 62 to 63.

Pages 62-63: No information on the sunroof.

Pages 55-64: I'll examine this range more closely since the table of contents can be inaccurate due to the non-sequential page numbering. Pages 58 and 59 have information on the sunroof, labelled as "Sunroof."


2. Extraction 

Page 4 shows "Body" has a sub-section for "Sunroof" listed as pages 62-63.

Page 58 and 59: Show the title of Sunroof.

3. Error Correction

The table of contents referenced pages 62 and 63 for the sunroof, but this is incorrect based on the provided scans. After rechecking pages 50-60, I found information on the sunroof on pages 58 and 59, titled "Sunroof." Also, page 4 just shows the table of contents, so I won't include that in my final answer.

4. Final Answer
<final-answer>
Information on the sunroof can be found on pages 58 and 59 of the manual.
</final-answer>
<page-references>
58, 59
</page-references>
"""
