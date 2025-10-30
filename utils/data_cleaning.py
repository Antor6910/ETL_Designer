import pandas as pd
import re
from collections import defaultdict

def clean_data(df, fillna_value=None, dropna=False):
    cleaning_info = {}

    original_columns = list(df.columns)
    new_columns = [col.strip().lower() for col in df.columns]
    df.columns = new_columns
    cleaning_info['original_columns'] = original_columns
    cleaning_info['cleaned_columns'] = new_columns

    root_map = defaultdict(list)
    pat = re.compile(r"^(.*?)(?:[._\s]*\d*)?$")
    for col in df.columns:
        root = pat.match(col).group(1).strip()
        root_map[root].append(col)

    merged_cols = []
    for root, cols in root_map.items():
        if len(cols) > 1:
            merged_cols.append(root)
            stacked = pd.concat([df[c].dropna().astype(str).str.strip() for c in cols], ignore_index=True)
            stacked = stacked[stacked != ""]
            df = df.drop(columns=cols)
            merged_df = pd.DataFrame({root: stacked})
            df = pd.concat([df, merged_df], axis=0, ignore_index=True)
    if merged_cols:
        cleaning_info['merged_column_groups'] = merged_cols

    str_cols = df.select_dtypes(include=['object', 'string']).columns
    for col in str_cols:
        df[col] = df[col].astype(str).str.strip()
    cleaning_info['stripped_string_columns'] = list(str_cols)

    before_dedup = len(df)
    df = df.drop_duplicates().reset_index(drop=True)
    after_dedup = len(df)
    cleaning_info['duplicates_removed'] = before_dedup - after_dedup

    na_before = df.isnull().sum().sum()
    if dropna:
        df = df.dropna()
        cleaning_info['rows_dropped_due_to_na'] = na_before
    elif fillna_value is not None:
        df = df.fillna(fillna_value)
        cleaning_info['na_filled_with'] = fillna_value
    cleaning_info['missing_values_before'] = int(na_before)
    cleaning_info['missing_values_after'] = int(df.isnull().sum().sum())

    df = df.reset_index(drop=True)
    return df, cleaning_info          
