# %%
import os
import openai
from openai import OpenAI

# def extract_using_prompt(pdf_type, expected_output=None, previous_output = None, previous_score = None):
#     """
#     Generate a prompt to extract structured data from noisy invoice/order documents.
    
#     Args:
#         pdf_type (str): The type of PDF document ("invoice" or "order")
        
#     Returns:
#         str: A well-structured prompt for extracting data
#     """
#     try:
#         # Initialize the client with your API key
#         # Set your API key as an environment variable: OPENAI_API_KEY
#         client = OpenAI(
#             api_key=os.getenv("OPENAI_API_KEY")
#         )
        
        
#         # Create a meta-prompt for generating a high-quality extraction prompt
#         meta_prompt = f"""
#         You are a professional prompt engineer specialized in document data extraction.
        
#         Task: Create a prompt that will be used to extract structured data from {pdf_type} documents.
        
#         The documents have these characteristics:
#         1. They contain background noise and irrelevant information
#         2. Some are poorly scanned and may have OCR errors
#         3. They might use different layouts and terminologies
#         4. They may be in different languages (primarily English and German)
        
#         The extracted data MUST follow exactly this JSON format. Here are some examples for the expected output {expected_output}. The previous prompt, if given is {previous_output} and the previous score is {previous_score}. Make sure to use the previous prompt and score to improve the current prompt.
    
#         Your prompt should:
#         1. Give clear instructions for handling noisy data
#         2. Specify how to identify and extract key information
#         3. Provide guidance on handling missing fields
#         4. Include instructions for handling currency and date formats based on the expected format
#         6. Include in your prompt to never summarize or group data, it should be displayed unchanged 
        
#         Create a prompt that would be given to an AI to extract the information from a document.
#         """
        
#         # Call the API to generate the prompt
#         response = client.chat.completions.create(
#             model="gpt-4o",
#             messages=[
#                 {"role": "system", "content": "You are a professional prompt engineer specializing in data extraction from documents."},
#                 {"role": "user", "content": meta_prompt} 
#             ],
#             temperature=0.0,
#             max_tokens=4000
#         )
#         # print(f"expected format:{expected_format}\nand \n expected output {expected_output}")
#         # Return the generated prompt
#                 # Return the generated prompt
#         output_prompt_path = 'prompts/main_prompt.txt'
#         with open(output_prompt_path, 'w') as file:
#             file.write(response.choices[0].message.content)
#         return response.choices[0].message.content
    
#     except Exception as e:
#         return f"Error: {str(e)}"

def extract_using_prompt(pdf_type, expected_output=None, previous_output=None, previous_prompt=None, previous_score=None):
    """
    Generate a prompt to extract structured data from noisy invoice/order documents, improving iteratively.
    
    Args:
        pdf_type (str): The type of PDF document ("invoice" or "order").
        expected_output (str, optional): The expected structured output for comparison.
        previous_output (str, optional): The previous prompt used for extraction.
        previous_score (float, optional): The similarity score of the previous output.
        
    Returns:
        str: A refined prompt for extracting data.
    """
    try:
        # Initialize the client with your API key
        client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Create a meta-prompt for generating a high-quality extraction prompt
        meta_prompt = f"""
        You are a professional prompt engineer specialized in document data extraction.
        
        Task: Create a refined prompt to extract structured data from {pdf_type} documents.
        
        The documents have these characteristics:
        1. They contain background noise and irrelevant information.
        2. Some are poorly scanned and may have OCR errors.
        3. They might use different layouts and terminologies.
        4. They may be in different languages (primarily English and German).
    
        
        Here is an example of the expected output which is randomly choosen: {expected_output}. Be exact in the format, specially the number of lines to expected output and the data type of each field. Do not extract information that is not complete or provided. 
        Make sure not to summarize or group data, it should be displayed unchanged.
        Make sure to use the previous prompt and score to improve the current prompt. While doing that, consider the following:
        1. The extracted data MUST follow exactly this JSON format.
        2. The previous prompt, if given, is: {previous_prompt}.
        3. The previous output, if given, is: {previous_output}.
        4. The previous similarity score, if available, is: {previous_score}.
        5. If the previous score was low (e.g., below 80), update the prompt to address potential issues. 
        6. names and addresses though they are both strings, should not be merged or grouped.
        7. The prompt should be clear and concise, providing specific instructions for handling noisy data by using "Explannation" as a guide. Note the things that are different from the previous output and expected output, and make sure to include them in the prompt.
        """
        
        # Call the API to generate the refined prompt
        response = client.chat.completions.create(
            # model="gpt-4o", 
            # use gpt3.5-turbo
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a professional prompt engineer specializing in data extraction from documents."},
                {"role": "user", "content": meta_prompt}
            ],
            temperature=0.0,
            max_tokens=4000
        )
        
        # Save the generated prompt for debugging or reuse
        output_prompt_path = 'prompts/main_prompt.txt'
        with open(output_prompt_path, 'w') as file:
            file.write(response.choices[0].message.content)
        
        # Return the generated prompt
        return response.choices[0].message.content
    
    except Exception as e:
        print(f"Error generating prompt: {e}")
        return None
