from typing import Any, Dict, List, Optional
from bson.errors import InvalidId
from django.conf import settings
from pymongo.errors import PyMongoError  # For MongoDB-specific exceptions
from bson import ObjectId  # For handling MongoDB's ObjectId
from PyMonitor.mongo import db

class MongoService:
    def __init__(self, collection_name: str = "website_config"):
            """
            Initialize MongoDB service using the shared connection pool.
            
            Args:
                collection_name: Name of the collection to work with
            """
            
            self.collection = db[collection_name]  # Use the pre-connected database

    def url_exists(self, url: str) -> bool:
        """Check if a document with this URL already exists"""
        try:
            existing = self.collection.find_one({"url": url}, {"_id": 1})  # Only return _id for efficiency
            return existing is not None
        except PyMongoError as e:
            print(f"Error checking URL existence: {e}")
            return False  # Assume no duplicate on error

    # CREATE OPERATIONS
    def create_flow(self, flow_data: Dict[str, Any]) -> bool:
        """Inserts document only if URL doesn't exist, verifies persistence"""
        try:
            # 0. Validate input and check for existing URL
            if "url" not in flow_data:
                print("Error: Missing required 'url' field")
                return False
                
            url = flow_data["url"]
            
            if self.url_exists(url):
                print(f"Document with URL '{url}' already exists")
                return False
                
            # 1. Perform the insert
            result = self.collection.insert_one(flow_data)
            
            # 2. Verify the write was acknowledged
            if not result.acknowledged:
                print("Write not acknowledged by MongoDB")
                return False
            
            # 3. Verify the document actually exists
            inserted_doc = self.collection.find_one({"_id": result.inserted_id})
            if not inserted_doc:
                print("Insert verification failed - document not found")
                return False
            
            return True
            
        except PyMongoError as e:
            print(f"MongoDB Error: {e}")
            return False
    

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
            
            flow = self._convert_mongo_doc(flow)
            return flow
            
        except Exception as e:
            print(f"Error fetching flow: {e}")
            return None
        
    def get_flow_by_id(self, id_str: str) -> Dict:
        """Get flow by MongoDB _id (ObjectId)"""
        try:
            # Validate ID format first
            obj_id = ObjectId(id_str)
            if doc := self.collection.find_one({"_id": obj_id}):
                return self._convert_mongo_doc(doc)
            return {}  # Explicit "not found" case
        except InvalidId:
            print(f"Invalid ID format: {id_str}")
            return {}  # Or raise specific exception
        except Exception as e:
            print(f"DB query failed: {e}") 
            raise  # Re-raise for proper error handling

    def get_all_flows(self, filter_query: Optional[Dict] = None) -> List[Dict]:
        """
        Get all flows matching optional filter criteria.
        
        Args:
            filter_query: Optional MongoDB query filter
            
        Returns:
            List of flow documents
        """
        try:
            filter_query = filter_query or {}
            flows = list(self.collection.find(filter_query))
            return [self._convert_mongo_doc(flow) for flow in flows]
        except PyMongoError as e:
            print(f"Error fetching flows: {e}")
            return []
    
    def partial_update_flow(self, flow_id: str, update_data: Dict[str, Any]) -> bool:
        """
        Partially update specific fields of a flow.
        
        Args:
            flow_id: The ID of the flow to update
            update_data: Dictionary of fields to update
            
        Returns:
            True if update was successful, False otherwise
        """
        try:
            result = self.collection.update_one(
                {"_id": ObjectId(flow_id)},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except (PyMongoError, ValueError) as e:
            print(f"Error partially updating flow: {e}")
            return False
   
    @staticmethod
    def _convert_mongo_doc(doc: Dict) -> Dict:
        """Convert MongoDB document to clean dict"""
        doc["_id"] = str(doc["_id"])  # Convert ObjectId to string
        return doc