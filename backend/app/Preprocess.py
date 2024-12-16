import pandas as pd
import re
import openai
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Use OPENAI_API_KEY from the environment
openai.api_key = os.getenv("OPENAI_API_KEY")


def compute_and_save_embeddings(df, original_name_column, cleaned_name_column, output_file):
    """Compute embeddings for all rows and save them with relevant metadata."""
    # Ensure required columns exist
    if original_name_column not in df.columns or cleaned_name_column not in df.columns:
        raise ValueError(f"Columns '{original_name_column}' or '{cleaned_name_column}' not found in DataFrame.")

    # Drop rows with missing or invalid cleaned_name
    df = df[df[cleaned_name_column].notna() & (df[cleaned_name_column] != "")]
    
    # Extract text for embedding
    texts = df[cleaned_name_column].astype(str).tolist()
    
    # Batch API calls to handle large datasets
    batch_size = 100
    embeddings = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        response = openai.Embedding.create(model="text-embedding-ada-002", input=batch)
        embeddings.extend([data['embedding'] for data in response['data']])
    
    # Save embeddings along with metadata
    df['embedding'] = embeddings
    df[['original_name', 'cleaned_name', 'size', 'unit', 'manufacturer', 'embedding']].to_pickle(output_file)
    print(f"Embeddings saved to {output_file}")

def preprocess_data(df, name_column):
    """Preprocess product data."""
    # Save original product name
    df['original_name'] = df[name_column]
    
    # Lowercase and clean special characters
    df[name_column] = df[name_column].str.lower()
    df[name_column] = df[name_column].str.replace(r"[^\w\s./-]", "", regex=True).str.strip()
    
    # Expand abbreviations
    abbreviation_map = {
        "choc.": "chocolate",
        "strwbr.": "strawberry",
        "eng.": "energy",
        "pb": "peanut butter",
        "oz": "oz",
        "lb": "lb",
        "g": "g",
        "ml": "ml"
    }
    
    def expand_abbreviations(text):
        for abbr, full in abbreviation_map.items():
            text = re.sub(rf"\b{abbr}\b", full, text)
        return text
    
    df[name_column] = df[name_column].apply(expand_abbreviations)
    
    # Remove stop words
    stop_words = {'and', 'with', 'the'}
    df[name_column] = df[name_column].apply(lambda x: " ".join([word for word in x.split() if word not in stop_words]))
    
    # Correct unit extraction with case-insensitivity
    df['size'] = df[name_column].str.extract(r"(\d+(\.\d+)?)(?=\s?(oz|g|ml|lb)\b)", expand=False)[0].astype(float, errors='ignore')
    df['unit'] = df[name_column].str.extract(r"(?i)(\boz\b|\bg\b|\bml\b|\blb\b)", expand=False).fillna('')

    # Handle size and unit normalization
    df['size'] = df.apply(lambda row: row['size'] if pd.notna(row['size']) else 0, axis=1)

    # Extract manufacturer (first meaningful word)
    df['manufacturer'] = df[name_column].str.split().str[0].fillna('')

    # Tokenize for semantic matching
    df['cleaned_name'] = df[name_column].str.replace(r"(?i)\b(?:oz|g|ml|lb)\b", "", regex=True).str.strip()

    # Drop rows with missing product names
    df = df[df[name_column].notna()]
    
    return df

