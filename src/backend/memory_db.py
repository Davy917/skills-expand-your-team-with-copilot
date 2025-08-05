"""
In-memory database implementation for development/testing
"""
from argon2 import PasswordHasher
import copy


class InMemoryCollection:
    def __init__(self):
        self.data = {}
    
    def find_one(self, query):
        if "_id" in query:
            item_id = query["_id"]
            return self.data.get(item_id)
        
        # Simple query matching for other fields
        for item_id, item in self.data.items():
            match = True
            for key, value in query.items():
                if key not in item:
                    match = False
                    break
                
                # Handle MongoDB-style operators
                if isinstance(value, dict):
                    if "$in" in value:
                        if not isinstance(item[key], list):
                            match = False
                            break
                        if not any(v in item[key] for v in value["$in"]):
                            match = False
                            break
                    elif "$gte" in value:
                        if item[key] < value["$gte"]:
                            match = False
                            break
                    elif "$lte" in value:
                        if item[key] > value["$lte"]:
                            match = False
                            break
                else:
                    if item[key] != value:
                        match = False
                        break
            
            if match:
                result = {"_id": item_id, **item}
                return result
        
        return None
    
    def find(self, query=None):
        if query is None:
            query = {}
        
        results = []
        for item_id, item in self.data.items():
            match = True
            for key, value in query.items():
                if key not in item:
                    match = False
                    break
                
                # Handle MongoDB-style operators
                if isinstance(value, dict):
                    if "$in" in value:
                        if not isinstance(item[key], list):
                            # For nested fields like schedule_details.days
                            if "." in key:
                                nested_keys = key.split(".")
                                nested_item = item
                                for nested_key in nested_keys:
                                    if nested_key in nested_item:
                                        nested_item = nested_item[nested_key]
                                    else:
                                        nested_item = None
                                        break
                                
                                if nested_item is None:
                                    match = False
                                    break
                                
                                if not isinstance(nested_item, list):
                                    match = False
                                    break
                                
                                if not any(v in nested_item for v in value["$in"]):
                                    match = False
                                    break
                            else:
                                match = False
                                break
                        else:
                            if not any(v in item[key] for v in value["$in"]):
                                match = False
                                break
                    elif "$gte" in value:
                        # Handle nested field access
                        if "." in key:
                            nested_keys = key.split(".")
                            nested_item = item
                            for nested_key in nested_keys:
                                if nested_key in nested_item:
                                    nested_item = nested_item[nested_key]
                                else:
                                    nested_item = None
                                    break
                            
                            if nested_item is None or nested_item < value["$gte"]:
                                match = False
                                break
                        else:
                            if item[key] < value["$gte"]:
                                match = False
                                break
                    elif "$lte" in value:
                        # Handle nested field access
                        if "." in key:
                            nested_keys = key.split(".")
                            nested_item = item
                            for nested_key in nested_keys:
                                if nested_key in nested_item:
                                    nested_item = nested_item[nested_key]
                                else:
                                    nested_item = None
                                    break
                            
                            if nested_item is None or nested_item > value["$lte"]:
                                match = False
                                break
                        else:
                            if item[key] > value["$lte"]:
                                match = False
                                break
                else:
                    if item[key] != value:
                        match = False
                        break
            
            if match:
                result = {"_id": item_id, **item}
                results.append(result)
        
        return results
    
    def insert_one(self, data):
        item_id = data["_id"]
        item_data = {k: v for k, v in data.items() if k != "_id"}
        self.data[item_id] = item_data
        return {"inserted_id": item_id}
    
    def update_one(self, query, update):
        item = self.find_one(query)
        if not item:
            return {"modified_count": 0}
        
        item_id = item["_id"]
        if "$push" in update:
            for field, value in update["$push"].items():
                if field not in self.data[item_id]:
                    self.data[item_id][field] = []
                self.data[item_id][field].append(value)
        
        if "$pull" in update:
            for field, value in update["$pull"].items():
                if field in self.data[item_id] and isinstance(self.data[item_id][field], list):
                    self.data[item_id][field].remove(value)
        
        if "$set" in update:
            for field, value in update["$set"].items():
                self.data[item_id][field] = value
        
        return {"modified_count": 1}
    
    def count_documents(self, query):
        return len(self.find(query))
    
    def aggregate(self, pipeline):
        # Simple aggregation implementation for getting unique days
        if len(pipeline) == 3 and pipeline[0].get("$unwind") == "$schedule_details.days":
            days = set()
            for item in self.data.values():
                if "schedule_details" in item and "days" in item["schedule_details"]:
                    for day in item["schedule_details"]["days"]:
                        days.add(day)
            
            return [{"_id": day} for day in sorted(days)]
        
        return []


# Create collections
activities_collection = InMemoryCollection()
teachers_collection = InMemoryCollection()


def hash_password(password):
    """Hash password using Argon2"""
    ph = PasswordHasher()
    return ph.hash(password)


def init_database():
    """Initialize database if empty"""
    
    # Initialize activities if empty
    if activities_collection.count_documents({}) == 0:
        for name, details in initial_activities.items():
            activities_collection.insert_one({"_id": name, **details})
            
    # Initialize teacher accounts if empty
    if teachers_collection.count_documents({}) == 0:
        for teacher in initial_teachers:
            teachers_collection.insert_one({"_id": teacher["username"], **teacher})


# Initial database if empty
initial_activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Mondays and Fridays, 3:15 PM - 4:45 PM",
        "schedule_details": {
            "days": ["Monday", "Friday"],
            "start_time": "15:15",
            "end_time": "16:45"
        },
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 7:00 AM - 8:00 AM",
        "schedule_details": {
            "days": ["Tuesday", "Thursday"],
            "start_time": "07:00",
            "end_time": "08:00"
        },
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Morning Fitness": {
        "description": "Early morning physical training and exercises",
        "schedule": "Mondays, Wednesdays, Fridays, 6:30 AM - 7:45 AM",
        "schedule_details": {
            "days": ["Monday", "Wednesday", "Friday"],
            "start_time": "06:30",
            "end_time": "07:45"
        },
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Soccer Team": {
        "description": "Join the school soccer team and compete in matches",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 5:30 PM",
        "schedule_details": {
            "days": ["Tuesday", "Thursday"],
            "start_time": "15:30",
            "end_time": "17:30"
        },
        "max_participants": 22,
        "participants": ["liam@mergington.edu", "noah@mergington.edu"]
    },
    "Basketball Team": {
        "description": "Practice and compete in basketball tournaments",
        "schedule": "Wednesdays and Fridays, 3:15 PM - 5:00 PM",
        "schedule_details": {
            "days": ["Wednesday", "Friday"],
            "start_time": "15:15",
            "end_time": "17:00"
        },
        "max_participants": 15,
        "participants": ["ava@mergington.edu", "mia@mergington.edu"]
    },
    "Art Club": {
        "description": "Explore various art techniques and create masterpieces",
        "schedule": "Thursdays, 3:15 PM - 5:00 PM",
        "schedule_details": {
            "days": ["Thursday"],
            "start_time": "15:15",
            "end_time": "17:00"
        },
        "max_participants": 15,
        "participants": ["amelia@mergington.edu", "harper@mergington.edu"]
    },
    "Drama Club": {
        "description": "Act, direct, and produce plays and performances",
        "schedule": "Mondays and Wednesdays, 3:30 PM - 5:30 PM",
        "schedule_details": {
            "days": ["Monday", "Wednesday"],
            "start_time": "15:30",
            "end_time": "17:30"
        },
        "max_participants": 20,
        "participants": ["ella@mergington.edu", "scarlett@mergington.edu"]
    },
    "Math Club": {
        "description": "Solve challenging problems and prepare for math competitions",
        "schedule": "Tuesdays, 7:15 AM - 8:00 AM",
        "schedule_details": {
            "days": ["Tuesday"],
            "start_time": "07:15",
            "end_time": "08:00"
        },
        "max_participants": 10,
        "participants": ["james@mergington.edu", "benjamin@mergington.edu"]
    },
    "Debate Team": {
        "description": "Develop public speaking and argumentation skills",
        "schedule": "Fridays, 3:30 PM - 5:30 PM",
        "schedule_details": {
            "days": ["Friday"],
            "start_time": "15:30",
            "end_time": "17:30"
        },
        "max_participants": 12,
        "participants": ["charlotte@mergington.edu", "amelia@mergington.edu"]
    },
    "Weekend Robotics Workshop": {
        "description": "Build and program robots in our state-of-the-art workshop",
        "schedule": "Saturdays, 10:00 AM - 2:00 PM",
        "schedule_details": {
            "days": ["Saturday"],
            "start_time": "10:00",
            "end_time": "14:00"
        },
        "max_participants": 15,
        "participants": ["ethan@mergington.edu", "oliver@mergington.edu"]
    },
    "Science Olympiad": {
        "description": "Weekend science competition preparation for regional and state events",
        "schedule": "Saturdays, 1:00 PM - 4:00 PM",
        "schedule_details": {
            "days": ["Saturday"],
            "start_time": "13:00",
            "end_time": "16:00"
        },
        "max_participants": 18,
        "participants": ["isabella@mergington.edu", "lucas@mergington.edu"]
    },
    "Sunday Chess Tournament": {
        "description": "Weekly tournament for serious chess players with rankings",
        "schedule": "Sundays, 2:00 PM - 5:00 PM",
        "schedule_details": {
            "days": ["Sunday"],
            "start_time": "14:00",
            "end_time": "17:00"
        },
        "max_participants": 16,
        "participants": ["william@mergington.edu", "jacob@mergington.edu"]
    }
}

initial_teachers = [
    {
        "username": "mrodriguez",
        "display_name": "Ms. Rodriguez",
        "password": hash_password("art123"),
        "role": "teacher"
     },
    {
        "username": "mchen",
        "display_name": "Mr. Chen",
        "password": hash_password("chess456"),
        "role": "teacher"
    },
    {
        "username": "principal",
        "display_name": "Principal Martinez",
        "password": hash_password("admin789"),
        "role": "admin"
    }
]