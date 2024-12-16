import pandas as pd
import re
import openai
import numpy as np
import time
from sklearn.metrics.pairwise import cosine_similarity
from fuzzywuzzy import fuzz
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Use OPENAI_API_KEY from the environment
openai.api_key = os.getenv("OPENAI_API_KEY")

def rule_based_match(row1, row2):
    size1 = row1.get('size', None)
    unit1 = row1.get('unit', None)
    manufacturer1 = row1.get('manufacturer', None)
    cleaned_name1 = row1.get('cleaned_name', None)

    size2 = row2.get('size', None)
    unit2 = row2.get('unit', None)
    manufacturer2 = row2.get('manufacturer', None)
    cleaned_name2 = row2.get('cleaned_name', None)

    size_match = abs(size1 - size2) <= 0.1 if size1 and size2 else False
    manufacturer_match = (
        manufacturer1 == manufacturer2 
        if pd.notna(manufacturer1) and pd.notna(manufacturer2) 
        else True
    )
    product_name_match = fuzz.token_sort_ratio(cleaned_name1, cleaned_name2) >= 85

    return size_match and manufacturer_match and product_name_match


def semantic_similarity_match(external_embedding, internal_embeddings, threshold=0.8):
    similarities = cosine_similarity([external_embedding], internal_embeddings)[0]
    best_index = np.argmax(similarities)
    best_score = similarities[best_index]
    
    # Correct Return Logic
    if best_score >= threshold:
        return best_index, best_score
    else:
        return None, None
    
# GPT-4 Model Fallback

def openai_fallback(external_name, internal_name):
    #print("Checking External Name - " + external_name + " Internal Name - " + internal_name)
    prompt = f"""
    
    You are a product matching system. Use these rules strictly:
    1. If the external product does NOT have the size (weight), the answer is 'No'.
    2. The product manufacturer, size (within a tolerance of ±0.1 oz), and units of internal and external products MUST be the same.
    3. The flavor must match exactly.
    4. If any rule is violated, the answer is 'No'.
    5. Ignore abbreviations, formatting, and common shorthand if they do not affect the rules above.

    With that in Consideration here are the products - 
    
    External Product: {external_name}
    Internal Product: {internal_name}
    
    Respond with 'Yes' if they are the correct match and 'No' if they are the wrong match.
    """
    #print(prompt)
    
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response['choices'][0]['message']['content'].strip().lower() == 'yes'

# GPT-4-turbo Model Fallback


# def openai_fallback(external_name, internal_name):
#     prompt = f"""
#         You are a product matching system. Use these rules strictly:
#         1. If the external product does NOT have the size (weight), the answer is 'No'.
#         2. The product manufacturer, size (within a tolerance of ±0.1 oz), and units of internal and external products MUST be the same.
#         3. The flavor (it can be abbrivated for example VN for Vanilla) must match exactly.
#         4. If any rule is violated, the answer is 'No'.
#         5. Ignore abbreviations, formatting, and common shorthand if they do not affect the rules above.

#         With that in Consideration here are the products - 
        
#         External Product: {external_name}
#         Internal Product: {internal_name}
        
#         Respond with 'Yes' if they are the correct match and 'No' if they are the wrong match.
#         If it is a 'No' then give me the reason, only when it is no, give me a reason and the external product name
#     """

#     response = openai.ChatCompletion.create(
#         model="gpt-4-turbo",
#         messages=[
#             {"role": "system", "content": "You are a product matching system."},
#             {"role": "user", "content": prompt}
#         ],
#         temperature=0  # Ensure consistent results
#     )
#     if response['choices'][0]['message']['content'].strip().lower() == 'yes':
#         return 1
#     else:
#         print(response['choices'][0]['message']['content'])


# def openai_fallback(external_name, internal_name):
#     prompt = f"""
#         You are a product matching system that compares product names based on these strict rules:

#         1. If the external product does NOT have the size (weight), respond 'No.'
#         2. Consider the size a match if the difference is within ±0.1 oz.
#         3. The product manufacturer, size, and flavor must match, but allow:
#         - Common abbreviations like "xtra" → "extra," "bbq" → "barbecue."
#         - Reordering of words (e.g., "5 hour xtra grape" vs. "5 hour energy extra strength grape").
#         - Ignore punctuation, capitalization, and formatting differences.
#         4. If key product details are missing or different, respond 'No.'
#         5. If you are uncertain, respond 'No.'

#         ---

#         **Example Format:**
#         - External Product: {external_name}  
#         - Internal Product: {internal_name}  

#         Is this a correct match? Respond 'Yes' if they match, otherwise respond 'No.'
#     """

#     response = openai.ChatCompletion.create(
#         model="gpt-3.5-turbo",
#         messages=[
#             {"role": "system", "content": "You are a product matching system."},
#             {"role": "user", "content": prompt}
#         ],
#         temperature=0  # Ensure deterministic responses
#     )
    
#     # Extract the response and return True if 'Yes'
#     return response['choices'][0]['message']['content'].strip().lower() == 'yes'



def run_matching_pipeline(external, internal, threshold=0.8):
    matches = []
    internal_embeddings = np.stack(internal['embedding'].values)

    for _, row_external in external.iterrows():
        external_embedding = np.array(row_external['embedding'])
        matched = False
        fallback_data = {
            'Fallback_Internal': None,
            'Fallback_Semantic_Score': None
        }

        for _, row_internal in internal.iterrows():
            if rule_based_match(row_external, row_internal):
                matches.append({
                    'External': row_external['original_name'],
                    'Internal': row_internal['original_name'],
                    'Method': 'Rule-Based',
                    'Semantic Score': None,
                    **fallback_data
                })
                matched = True
                break

        if not matched:
            best_index, best_score = semantic_similarity_match(external_embedding, internal_embeddings, threshold)
            if best_index is not None:
                best_match = internal.iloc[best_index]
                if best_score <= 0.97:
                    is_match = openai_fallback(row_external['original_name'], best_match['original_name'])
                    fallback_data.update({
                        'Fallback_Internal': best_match['original_name'],
                        'Fallback_Semantic_Score': best_score
                    })
                    if is_match:
                        matches.append({
                            'External': row_external['original_name'],
                            'Internal': best_match['original_name'],
                            'Method': 'Semantic + Fallback',
                            'Semantic Score': best_score,
                            **fallback_data
                        })
                        matched = True
                else:
                    matches.append({
                        'External': row_external['original_name'],
                        'Internal': best_match['original_name'],
                        'Method': 'Semantic',
                        'Semantic Score': best_score,
                        **fallback_data
                    })
                    matched = True

        if not matched:
            # print(f"Unmatched: {row_external['original_name']}")
            _, best_score = semantic_similarity_match(external_embedding, internal_embeddings, 0.0)
            matches.append({
                'External': row_external['original_name'],
                'Internal': 'NULL',
                'Method': 'Unmatched',
                'Semantic Score': best_score if best_score else 'N/A',
                **fallback_data
            })

    return pd.DataFrame(matches)
