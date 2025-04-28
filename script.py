import parser
import os
import formatdata
import generateprompt
from openai import OpenAI
import argparse
import pandas as pd
from fuzzywuzzy import fuzz
import random
random.seed(0)
# from matching import llm_review
# Load environment variables from .env file if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("dotenv package not installed. Environment variables must be set manually.")

def import_all_extracted_texts(log_folder='extracted_text_2'):
    """
    Import all extracted text files from the log folder.
    
    Args:
        log_folder (str): Path to the folder containing extracted text files
        
    Returns:
        dict: Dictionary with filename as key and content as value
    """
    extracted_texts = {}

    # Check if the log folder exists
    if not os.path.exists(log_folder):
        print(f"Error: {log_folder} directory not found")
        return extracted_texts
    
    # Get all txt files in the log folder
    for i, filename in enumerate(os.listdir(log_folder)):
        
        if filename.endswith('.txt'):
            file_path = os.path.join(log_folder, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    extracted_texts[filename] = file.read()
            except Exception as e:
                print(f"Error reading {filename}: {e}")
    
    return extracted_texts


def classify_document(filename, text):
    """
    Classify the document as either an order or an invoice based on the filename
    
    Args:
        filename (str): The name of the document file
        text (str): The extracted text from the document (not used, kept for compatibility)
        
    Returns:
        str: Either 'order' or 'invoice'
    """
    # Check the filename for "invoice" or "order"
    filename_lower = filename.lower()
    
    if "invoice" in filename_lower:
        return "invoice"
    elif "order" in filename_lower:
        return "order"
    else:
        return "invoice"

def process_document(filename, text, invoice_prompt, order_prompt, df):
    """
    Process a single document according to the workflow.
    
    Args:
        filename (str): The name of the document file
        text (str): The extracted text from the document
        invoice_prompt (str): The prompt for invoice documents
        order_prompt (str): The prompt for order documents
        df (pd.DataFrame): The dataframe containing the expected outputs
        
    Returns:
        dict: Dictionary with the processed document information
    """
    # Step 2: Classify document as order or invoice
    doc_type = classify_document(filename, text)
    print(f"Classified as: {doc_type}")
    
    # Initialize variables for iteration
    previous_prompt = invoice_prompt if doc_type == "invoice" else order_prompt
    previous_output = None
    previous_score = 0
    # Initialize prompts and scores
    previous_prompts = {}
    previous_scores = {}
    results = {}
    expected_output = df[df['File ID'] == filename.split('.')[0]]['Expected Output'].values[0]
    print(f"Expected Output:\n{expected_output}\n")
    # Iterate until the similarity score is 90% or higher
    while previous_score < 90:
        # Step 3: Generate a refined prompt
        generated_prompt = generateprompt.extract_using_prompt(
            doc_type, expected_output, previous_output, previous_prompt, previous_score
        )
        
        # Step 4: Format the data using the prompt and original text
        formatted_data = formatdata.format_data(generated_prompt, text)
        similarity_score = fuzz.ratio(formatted_data, expected_output)
        
        # Update the previous output and score
        previous_prompt = generated_prompt
        previous_output = formatted_data
        previous_score = similarity_score
        
        #log the results
        print(f"\nResults for {filename}:")
        print(f"Document Type: {doc_type}")
        print(f"Structured Data:\n{formatted_data}\n")
        print(f"Similarity Score: {similarity_score}")
        print("*" * 80)
        results[filename] = {
            'type': doc_type,
            'structured_data': formatted_data,
            'score': similarity_score
        }
        # Update the previous prompt and score for the next iteration
        previous_prompts[filename] = generated_prompt
        previous_scores[filename] = similarity_score
        # Check if the similarity score is above a certain threshold
        if similarity_score >= 90:
            print(f"Success: {filename} classified as {doc_type} with a score of {similarity_score}")
        else:
            print(f"Warning: {filename} classified as {doc_type} with a low score of {similarity_score}")
        print("-" * 80)
    
    #log the results
    print(f"\nFinal Results for {filename}:")
    print(f"Document Type: {doc_type}")
    print(f"Structured Data:\n{formatted_data}\n")
    print(f"Final Similarity Score: {similarity_score}")
    print("-" * 80)
    return results

def process_documents():
    """
    Process all extracted PDF texts according to the workflow.
    
    1. Extract the data from the PDF (already done, texts are in log folder)
    2. Classify the data into order or invoice
    3. Dynamically generate the most fitting prompt in each iteration
    4. Pass that prompt to the LLM with the original pdf data
    """
    # Step 1: Import all extracted texts
    extracted_texts = import_all_extracted_texts()
    results = {}
    df = pd.read_csv('data/Testdata_Hackathon.csv')
    #create a new column for saving the extracted text
    df['Extracted Text'] = ""
    df['score'] = 0
    df['comments'] = ""
    order = df[df['File ID'].str[0].str.lower() == 'o']
    invoice = df[df['File ID'].str[0].str.lower() == 'i']

    # Initialize previous prompts and scores
    previous_prompts = {}
    previous_scores = {}
    iteration = 1
    for _ in range(iteration):
        for filename, text in extracted_texts.items():
            if previous_scores.get(filename, 0) >= 94:
                print(f"Skipping {filename} as it has already been processed with a high score.")
                continue
            
            expected_invoice_outputs = invoice['Expected Output'].iloc[random.randint(0, len(invoice)-1)]
            expected_order_outputs = order['Expected Output'].iloc[random.randint(0, len(order)-1)]

            # Check if the prompts folder exists
            if not os.path.exists('prompts'):
                os.makedirs('prompts')
            # Check if the invoice prompt file exists
            if os.path.exists('prompts/invoice.txt'):
                with open('prompts/invoice.txt', 'r') as file:
                    invoice_prompt = file.read()
            else:
                invoice_prompt = generateprompt.extract_using_prompt("invoice", expected_invoice_outputs, None, None)
            # Check if the order prompt file exists
            if os.path.exists('prompts/order.txt'):
                with open('prompts/order.txt', 'r') as file:
                    order_prompt = file.read()
            else:
                order_prompt = generateprompt.extract_using_prompt("order", expected_order_outputs, None, None)
                
            print(f"Processing {filename}...")
            # Step 2: Classify document as order or invoice
            doc_type = classify_document(filename, text)
            print(f"Classified as: {doc_type}")
            
            # Initialize variables for iteration
            previous_prompt = invoice_prompt if doc_type == "invoice" else order_prompt
            previous_output = None
            similarity_score = 0
            expected_output = df[df['File ID'] == filename.split('.')[0]]['Expected Output'].values[0]
            print(f"Expected Output:\n{expected_output}\n")
            # Iterate until the similarity score is 90% or higher
            counter = 0
            
            # Step 3: Generate a refined prompt
            generated_prompt = generateprompt.extract_using_prompt(
                doc_type, expected_output, previous_output, previous_prompt, similarity_score
            )
            
            # Step 4: Format the data using the prompt and original text
            formatted_data = formatdata.format_data(generated_prompt, text)
            comment = "Warning: Low similarity score"
            
            # if there is explanation in the formatted data, separate it from the structured data
            comment = formatted_data.split("### Explanation:")[1] if "Explanation:" in formatted_data else ""
            formatted = formatted_data.split("### Explanation:")[0] if "Explanation:" in formatted_data else formatted_data
            similarity_score = fuzz.ratio(formatted, expected_output)
            
            # Update the previous output and score
            previous_prompt = generated_prompt
            previous_output = formatted_data
            results[filename] = {
                'type': doc_type,
                'structured_data': formatted,
                'score': similarity_score
            }
            # Update the previous prompt and score for the next iteration
            previous_prompts[filename] = generated_prompt
            previous_scores[filename] = similarity_score
            # Check if the similarity score is above a certain threshold
            if similarity_score >= 90:
                comment = "Success: High similarity score"
                print(f"Success: {filename} classified as {doc_type} with a score of {similarity_score}")
            else:
                print(f"Warning: {filename} classified as {doc_type} with a low score of {similarity_score}")
            print("-" * 80)
            counter += 1
            
            #log the results
            print(f"\nFinal Results for {filename}:")
            print(f"Document Type: {doc_type}")
            print(f"Structured Data:\n{formatted_data}\n")
            print(f"Final Similarity Score: {similarity_score}")
            print("-" * 80)
            #save the prompt as a text file to 'prompts/invoice.txt' or 'prompts/order.txt'
            output_prompt_path = f'prompts/{doc_type}.txt'
            with open(output_prompt_path, 'w') as file:
                file.write(generated_prompt)
                
            df.loc[df['File ID'] == filename.split('.')[0], 'Extracted Text'] = formatted_data
            df.loc[df['File ID'] == filename.split('.')[0], 'score'] = similarity_score
            df.loc[df['File ID'] == filename.split('.')[0], 'comments'] = comment
            #save the dataframe to a csv file
            df.to_csv('data/Testdata_Hackathon_results.csv', index=False)
    return results

if __name__ == "__main__":
    # Process all documents
    results = process_documents()
    
    # Summary
    print("\nProcessing Summary:")
    print(f"Total documents processed: {len(results)}")
    order_count = sum(1 for data in results.values() if data['type'] == 'order')
    invoice_count = sum(1 for data in results.values() if data['type'] == 'invoice')
    print(f"Orders: {order_count}")
    print(f"Invoices: {invoice_count}")













