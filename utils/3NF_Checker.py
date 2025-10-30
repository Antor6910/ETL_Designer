import pandas as pd
import re
from collections import defaultdict
from tabulate import tabulate

class Semantic3NFPrefixDecomposer:
    def __init__(self, df: pd.DataFrame):
        self.original_df = df.copy()
        self.columns = list(df.columns)
        self.col_map = self._normalize_and_combine_columns()
        self.df = pd.DataFrame(self.col_map)
        self.groups = self._group_by_prefix()
        self.tables = []

    def _normalize_and_combine_columns(self):
        col_map = {}
        processed = set()
        for col in self.columns:
            norm = re.sub(r'[\d_]+$', '', col.lower())
            if norm in processed:
                continue
            similar = [c for c in self.columns if re.sub(r'[\d_]+$', '', c.lower()) == norm]
            combined_series = pd.concat(
                [self.original_df[c].dropna() for c in similar],
                ignore_index=True
            )
            combined_series = combined_series.astype(str).str.strip()
            combined_series = combined_series[combined_series.str.lower() != 'nan']
            col_map[norm] = combined_series.reset_index(drop=True)
            processed.add(norm)
            processed.update(similar)

        max_len = max(len(series) for series in col_map.values())
        for k in col_map:
            col_map[k] = col_map[k].reindex(range(max_len))
        return col_map

    def _group_by_prefix(self):
        groups = defaultdict(list)
        for col in self.df.columns:
            prefix = re.split(r'[_\-\s\.]+', col.lower())[0]
            groups[prefix].append(col)
        return [grp for grp in groups.values()]

    def decompose_3nf(self):
        used_cols = set()
        for group_cols in self.groups:
            table_df = self.df[group_cols].drop_duplicates().reset_index(drop=True)
            pk = [col for col in group_cols if 'id' in col.lower()]
            if not pk:
                pk = [group_cols[0]]
            used_cols.update(group_cols)
            self.tables.append({
                'table_name': f"{group_cols[0].split('_')[0]}_table",
                'columns': group_cols.copy(),
                'primary_key': pk,
                'df': table_df,
                'foreign_keys': []
            })

        remaining_cols = [col for col in self.df.columns if col not in used_cols]
        if remaining_cols:
            table_df = self.df[remaining_cols].drop_duplicates().reset_index(drop=True)
            pk = [col for col in remaining_cols if 'id' in col.lower()] or [remaining_cols[0]]
            self.tables.append({
                'table_name': "other_table",
                'columns': remaining_cols.copy(),
                'primary_key': pk,
                'df': table_df,
                'foreign_keys': []
            })

        self._assign_primary_as_foreign_keys()

    def _assign_primary_as_foreign_keys(self):
        if not self.tables:
            return
        base_table = self.tables[0]
        base_pk = base_table['primary_key'][0]
        base_values = base_table['df'][base_pk].dropna().astype(str).unique()

        for i, target_table in enumerate(self.tables[1:], start=1):
            if base_pk not in target_table['df'].columns:
                repeated_values = pd.Series(base_values).sample(
                    n=len(target_table['df']),
                    replace=True
                ).reset_index(drop=True)
                target_table['df'][base_pk] = repeated_values
                target_table['columns'].append(base_pk)
            target_table['foreign_keys'].append({
                'ref_table': base_table['table_name'],
                'column': base_pk,
                'ref_column': base_pk
            })

    def get_tables_tabular_html(self):
        html = ""
        for t in self.tables:
            table_html = tabulate(t['df'], headers='keys', tablefmt='html', showindex=False)
            html += f"<h4>{t['table_name']}</h4>"
            html += f"<div><b>Columns:</b> {', '.join(t['columns'])}<br>"
            html += f"<b>Primary Key:</b> {', '.join(t['primary_key'])}<br>"
            if t['foreign_keys']:
                html += "<b>Foreign Keys:</b><ul>"
                for fk in t['foreign_keys']:
                    html += f"<li>{fk['column']} → {fk['ref_table']}.{fk['ref_column']}</li>"
                html += "</ul>"
            else:
                html += "<b>Foreign Keys:</b> None<br>"
            html += "</div>"
            html += f"<div class='etl-table-wrapper'>{table_html}</div>"
        return html
