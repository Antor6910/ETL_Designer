import pandas as pd

def to_first_nf(df):
    """
    Converts a DataFrame to 1NF by splitting multi-valued attributes.
    Returns the 1NF DataFrame and a summary string.
    """
    import re
    df1 = df.copy()
    summary = ""
    for col in df1.columns:
        # Detect lists/sets as comma or semicolon separated
        if df1[col].astype(str).str.contains(r"[;,]").any():
            summary += f"Splitting multi-valued column: {col}\n"
            df1 = df1.assign(**{
                col: df1[col].astype(str).str.split(r"[;,]")
            })
            df1 = df1.explode(col)
            df1[col] = df1[col].astype(str).str.strip()
    df1 = df1.reset_index(drop=True)
    return df1, summary
