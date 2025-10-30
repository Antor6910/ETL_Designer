import pandas as pd
from typing import List, Tuple

class FunctionalDependencyChecker:
    def __init__(self, df: pd.DataFrame):
        self.df = df

    def check_fd(self, x_cols: List[str], y_cols: List[str]) -> bool:
        grouped = self.df.groupby(x_cols)[y_cols].nunique(dropna=False)
        return (grouped <= 1).all().all()

    def find_all_fds(self, max_lhs_size=2) -> List[Tuple[List[str], List[str]]]:
        from itertools import combinations
        fds = []
        columns = list(self.df.columns)
        for r in range(1, min(max_lhs_size, len(columns)) + 1):
            for x in combinations(columns, r):
                y_candidates = [col for col in columns if col not in x]
                for y in y_candidates:
                    if self.check_fd(list(x), [y]):
                        fds.append((list(x), [y]))
        return fds
