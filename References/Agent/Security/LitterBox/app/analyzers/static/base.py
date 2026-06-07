# app/analyzers/static/base.py
from ..base import BaseAnalyzer

class StaticAnalyzer(BaseAnalyzer):
    def cleanup(self):
        """Most static analyzers don't need cleanup"""
        pass