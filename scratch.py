def get_prompt(query=query):
    return (
        f"""Based on the manual pages provided, answer the following question: {query}

Please provide your response in four parts:
1. Page Scan: Explain your reasoning process, including which pages you looked at and why. Please exhaustively check every page in the input, and talk about your thoughts about each set of 10 pages. Like, I will first look at 1-10. I see nothing related to my query here. I now processed 11-20, and so on for all of the input. There are {MAX_PAGES} pages in total, don't forget the ones on the end!
2. Extraction: For the given pages, extract the page contents. If the answer is in a table or diagram, extract the entire table / diagram, so that you can clearly see the data you want to extract.
3. Error Correction: If you made a mistake, or need to look at a different page, use this space to look at that page and extract data as needed. If no errors are detected, write "No errors detected", and list the final list of pages that you plan on returning. 
4. Final Answer: Give the precise answer to the question, as well as the pages referenced (it is possible that the answer is simply pages).

Format your response as follows:
1. Page Scan:
[your comprehensive page scan here]

2. Extraction:
[your detailed extraction here]

3. Error Correction:
[your detailed error correction here]

4. Final Answer
<final-answer>
[your precise prose answer here]
</final-answer>
<page-references>
[page numbers here, delimited by commas]
</page-references>

Here are two example outputs for your reference, please format your response accordingly:
<begin-examples>
{example_1}
{example_2}
</end-examples>
    """
        ""
    )
