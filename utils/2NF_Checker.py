import pandas as pd
from typing import List, Dict

def is_subset(subset, superset):
    return all(item in superset for item in subset)

class SecondNFChecker:
    def __init__(self, df: pd.DataFrame, primary_key: List[str], fds: List[tuple]):
        self.df = df
        self.primary_key = primary_key
        self.fds = fds

    def is_2nf(self) -> bool:
        prime_attrs = set(self.primary_key)
        all_attrs = set(self.df.columns)
        non_prime_attrs = all_attrs - prime_attrs

        for lhs, rhs in self.fds:
            lhs_set = set(lhs)
            rhs_set = set(rhs)
            if (not rhs_set.isdisjoint(non_prime_attrs)
                and is_subset(lhs_set, self.primary_key)
                and lhs_set != set(self.primary_key)):
                return False
        return True

    def get_violations(self) -> List[Dict]:
        violations = []
        prime_attrs = set(self.primary_key)
        all_attrs = set(self.df.columns)
        non_prime_attrs = all_attrs - prime_attrs

        for lhs, rhs in self.fds:
            lhs_set = set(lhs)
            rhs_set = set(rhs)
            if (not rhs_set.isdisjoint(non_prime_attrs)
                and is_subset(lhs_set, self.primary_key)
                and lhs_set != set(self.primary_key)):
                violations.append({
                    "lhs": lhs,
                    "rhs": rhs
                })
        return violations
