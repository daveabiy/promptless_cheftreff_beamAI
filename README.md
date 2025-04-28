# promptless_cheftreff_beamAI
This is the work done as team "Promptless" during the cheftreff hackathon, Apr 2025, Hamburg. The task is to create an AI agent that can generate prompt given the output.

# command for running:
## converting the pdf to text file using pytesseract
<b><i>python parser.py data/Testdata_Hackathon.csv</i></b>

## extracting required information using a generated prompt
<b><i>python parser.py data/Testdata_Hackathon.csv</i></b>

## Progress Update

---
### What We Have Accomplished:

1. **Meta Prompt Development**:
   - Created a universal meta prompt capable of generating custom extraction prompts for both invoice and order request use cases.
   - Optimized the meta prompt to handle edge cases and ensure high accuracy in data extraction.

2. **Parsing & Extraction Workflow**:
   - Developed an automated workflow to parse PDFs, extract required data fields, and output results in the specified JSON format.
   - Integrated the workflow with Airtable API for seamless data retrieval and submission.

3. **Accuracy Testing**:
   - Benchmarked the extracted data against the provided ground truth datasets.
   - Achieved high precision and consistency in data extraction for both use cases.

4. **Automation**:
   - Automated the entire pipeline, ensuring scalability and adaptability to new document formats without manual intervention.

5. **Submission**:
   - Uploaded extracted data to Airtable for evaluation.
   - Verified the uploaded data through the provided Airtable links.

---

### Next Steps:

- Further optimize the meta prompt for additional edge cases.
- Conduct additional testing to improve accuracy metrics.
- Prepare the final accuracy report for submission.