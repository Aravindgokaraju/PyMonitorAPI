from typing import Any, Dict, Optional
from execution.mongo_service import MongoClient
from django.conf import settings

class MongoService:
    def __init__(self):
        # Initialize MongoDB connection
        self.mongo_client = MongoClient(settings.MONGO_DB_CONFIG["host"])
        self.db = self.mongo_client[settings.MONGO_DB_CONFIG["db_name"]]
        self.collection = self.db[settings.MONGO_DB_CONFIG["collection"]]


    def get_flow(self, query_filter: Dict[str, Any], remove_id: bool = True) -> Optional[Dict]:
        """
        Get a flow document by filter criteria.
        
        Args:
            query_filter: Dictionary specifying the MongoDB query filter
            remove_id: Whether to remove the '_id' field from the result
            
        Returns:
            The matching document as a dict, or None if not found/error
        """
        try:
            flow = self.collection.find_one(query_filter)
            if not flow:
                return None
                
            if remove_id:
                flow.pop('_id', None)
                
            return flow
            
        except Exception as e:
            print(f"Error fetching flow: {e}")
            return None

    def _get_websites_data(self) -> list[dict]:
        """Fetch website flow data from MongoDB using PyMongo."""
        try:
            # Get all documents in the collection
            flows = list(self.collection.find({}))
            
            # Optionally, remove MongoDB's _id if you don't need it
            for flow in flows:
                flow.pop("_id", None)
            
            return flows
        
        except Exception as e:
            print(f"Error fetching MongoDB data: {e}")
            return []
    
    def get_flow_by_name(self, name: str) -> Dict:
        """Get specific flow by name"""
        try:
            if doc := self.flows_collection.find_one({"name": name}):
                return self._convert_mongo_doc(doc)
            return {}
        except Exception as e:
            print(f"MongoDB lookup error: {e}")
            return {}

    @staticmethod
    def _convert_mongo_doc(doc: Dict) -> Dict:
        """Convert MongoDB document to clean dict"""
        doc["_id"] = str(doc["_id"])  # Convert ObjectId to string
        return doc