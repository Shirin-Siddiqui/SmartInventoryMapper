import pandas as pd
from rapidfuzz import fuzz
import json

def preprocess(df):
    """Preprocess data by stripping, lowering, and filling NAs."""
    try:
        return df.iloc[:, :2].apply(lambda x: x.str.strip().str.lower().fillna("null"))
    except Exception as e:
        raise ValueError(f"Preprocessing error: {str(e)}")

def calculate_accuracy(actual_file, predicted_file, threshold=90):
    try:
        # Load CSV files with detailed logging
        try:
            actual_df = pd.read_csv(actual_file)
            predicted_df = pd.read_csv(predicted_file)
        except FileNotFoundError:
            return {"error": "One or both files were not found."}
        except pd.errors.EmptyDataError:
            return {"error": "One or both files are empty."}
        except Exception as e:
            return {"error": f"File loading error: {str(e)}"}

        if len(actual_df) != len(predicted_df):
            return {"error": "Files have different number of rows."}

        # Preprocess data
        try:
            actual_pairs = preprocess(actual_df)
            predicted_pairs = preprocess(predicted_df)
        except ValueError as e:
            return {"error": str(e)}

        # Matching logic
        def is_match(row1, row2):
            return (
                fuzz.ratio(row1[0], row2[0]) >= threshold and 
                fuzz.ratio(row1[1], row2[1]) >= threshold
            )

        matches = [is_match(a, p) for a, p in zip(actual_pairs.values, predicted_pairs.values)]
        correct_matches = actual_pairs[matches].reset_index(drop=True)
        wrong_matches = actual_pairs[~pd.Series(matches)].reset_index(drop=True)
        predicted_wrong = predicted_pairs[~pd.Series(matches)].reset_index(drop=True)

        total_entries = len(actual_df)
        accuracy = (len(correct_matches) / total_entries) * 100

        # Format the results for JSON response
        result_data = []
        for idx, row in wrong_matches.iterrows():
            result_data.append({
                "external": row[0],
                "predicted_internal": row[1],
                "actual_internal": predicted_wrong.iloc[idx, 1],
                "status": "Wrong"
            })

        for idx, row in correct_matches.iterrows():
            result_data.append({
                "external": row[0],
                "predicted_internal": row[1],
                "actual_internal": row[1],
                "status": "Correct"
            })

        response = {
            "accuracy": round(accuracy, 2),
            "results": result_data
        }

        return json.dumps(response, indent=4)

    except Exception as e:
        return {"error": f"Unexpected processing error: {str(e)}"}
