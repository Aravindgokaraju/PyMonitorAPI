

# from typing import Any, Dict, List

# class StandaloneScrapingService:
#     """
#     Stub version of StandaloneScrapingService for RQ worker routing.
#     Does nothing except accept request data and return empty results.
#     Useful for containers without Chrome.
#     """
#     def __init__(self, stealth_level='stable'):
#         # Stub attributes to satisfy code referencing these
#         self.interaction_service = None
#         self.interruption_handler = None
#         self.function_map = {}
#         self.command_stack = None
#         self.criteria_dict: Dict[str, Any] = {}
#         self.parent_pair: Dict[str, str] = {}
#         self.start_index = 0
#         self.website = ""

#     def scrape_websites(self, request_data: Dict[str, Any]) -> List[Dict[str, Any]]:
#         """Stub method returns empty list instead of scraping"""
#         # Optionally, log or print that this is a stub
#         print("Stub StandaloneScrapingService called; returning empty results.")
#         return []

#     @staticmethod
#     def steps_to_criteria_dict(steps: List[dict]) -> Dict[str, Any]:
#         """Stub - returns empty dict"""
#         return {}
