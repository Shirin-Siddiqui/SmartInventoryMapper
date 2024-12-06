import pandas as pd
import re
import openai
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv()

# Use the OpenAI API Key from the environment
openai.api_key = os.getenv("OPENAI_API_KEY")

# Preprocessing function
def preprocess_data(df, name_column):
    """Preprocess product data."""
    df[name_column] = df[name_column].str.lower()
    df[name_column] = df[name_column].str.replace(r"[^\w\s./-]", "", regex=True).str.strip()
    
    abbreviation_map = {
        "Choc.": "Chocolate",
        "Strwbr.": "Strawberry",
        "Eng.": "Energy",
        "PB": "Peanut Butter",
        "OZ": "oz"
    }
    
    def expand_abbreviations(text):
        for abbr, full in abbreviation_map.items():
            text = re.sub(rf"\b{abbr.lower()}\b", full.lower(), text)
        return text
    df[name_column] = df[name_column].apply(expand_abbreviations)
    
    stop_words = {'and', 'with', 'the'}
    df[name_column] = df[name_column].apply(lambda x: " ".join([word for word in x.split() if word not in stop_words]))
    
    df['size'] = df[name_column].str.extract(r"(\d+(\.\d+)?)(?:\s?(oz|g))?", expand=False)[0]
    df['unit'] = df[name_column].str.extract(r"(\b(?:oz|g)\b)", expand=False)
    df['manufacturer'] = df[name_column].str.split().str[0]
    
    df['cleaned_name'] = df[name_column].str.replace(r"\b(?:oz|g)\b", "", regex=True).str.strip()
    df = df[df[name_column].notna()]
    
    return df

def compute_and_save_embeddings(df, name_column, output_file):
    """Compute embeddings for all rows and save them."""
    df = df[df[name_column].notna() & (df[name_column] != "")]
    texts = df[name_column].astype(str).tolist()
    
    batch_size = 100
    embeddings = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        response = openai.Embedding.create(model="text-embedding-ada-002", input=batch)
        embeddings.extend([data['embedding'] for data in response['data']])
    
    df['embedding'] = embeddings
    df.to_pickle(output_file)
    print(f"Embeddings saved to {output_file}")

# Rule-Based Matching
def rule_based_match(row1, row2):
    """Checks for exact matches on size, manufacturer, and substring product name similarity."""
    size_match = (row1['size'] == row2['size']) and (row1['unit'] == row2['unit'])
    manufacturer_match = row1['manufacturer'] == row2['manufacturer']
    product_name_match = row1['cleaned_name'] in row2['cleaned_name'] or row2['cleaned_name'] in row1['cleaned_name']
    return size_match and manufacturer_match and product_name_match

# Semantic Matching
def semantic_similarity_match(external_embedding, internal_embeddings, threshold=0.9):
    """Match external embeddings to internal ones using cosine similarity."""
    similarities = cosine_similarity([external_embedding], internal_embeddings)[0]
    best_index = np.argmax(similarities)
    best_score = similarities[best_index]
    if best_score >= threshold:
        return best_index, best_score
    return None, None

# Fallback Matching
def openai_fallback(external_name, internal_name):
    """Ask OpenAI for match judgment."""
    prompt = f"""
    Examples:
    Correct Matches:
    External_Product_Name
    Internal_Product_Name
    DIET LIPTON GREEN TEA W/ CITRUS 20 OZ
    Lipton Diet Green Tea with Citrus (20oz)

    Wrong Matches:
    External_Product_Name
    Internal_Product_Name
    Hersheys Almond Milk Choco 1.6 oz
    Hersheys Milk Chocolate with Almonds (1.85oz)

    External Product: {external_name}
    Internal Product: {internal_name}

    Respond with 'Yes' if they are the same product and 'No' if they are not.
    """
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response['choices'][0]['message']['content'].strip().lower() == 'yes'

# Matching Pipeline
def run_matching_pipeline(external, internal, threshold=0.9):
    """Run the full matching pipeline."""
    matches = []
    internal_embeddings = np.stack(internal['embedding'].values)

    for _, row_external in external.iterrows():
        external_embedding = np.array(row_external['embedding'])

        matched = False
        for _, row_internal in internal.iterrows():
            if rule_based_match(row_external, row_internal):
                matches.append({
                    'External': row_external['PRODUCT_NAME'],
                    'Internal': row_internal['LONG_NAME']
                })
                matched = True
                break
        
        if not matched:
            best_index, best_score = semantic_similarity_match(external_embedding, internal_embeddings, threshold)
            if best_index is not None:
                best_match = internal.iloc[best_index]
                if best_score < 0.95:
                    is_match = openai_fallback(row_external['PRODUCT_NAME'], best_match['LONG_NAME'])
                    if is_match:
                        matches.append({
                            'External': row_external['PRODUCT_NAME'],
                            'Internal': best_match['LONG_NAME']
                        })
                        matched = True
                else:
                    matches.append({
                        'External': row_external['PRODUCT_NAME'],
                        'Internal': best_match['LONG_NAME']
                    })
                    matched = True
        
        if not matched:
            matches.append({
                'External': row_external['PRODUCT_NAME'],
                'Internal': None
            })

    return pd.DataFrame(matches)
