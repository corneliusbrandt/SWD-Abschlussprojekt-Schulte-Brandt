import os
from tinydb import TinyDB, Query

class Mechanism:
    db_connector = TinyDB(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.json'))

    def __init__(self, name, table_points, table_links) -> None:
        """Create a new mechanism based on the given name"""
        self.name = name
        self.table_points = table_points
        self.table_links = table_links

    def store_data(self)-> None:
        """Save the mechanism to the database"""
        print("Storing data...")
        # Check if the mechanism already exists in the database
        MechanismQuery = Query()
        result = self.db_connector.search(MechanismQuery.name == self.name)

        if result:
            # Update the existing record with the current instance's data
            result = self.db_connector.update(self.__dict__, doc_ids=[result[0].doc_id])
            print("Data updated.")
        else:
            # If the mechanism doesn't exist, insert a new record
            self.db_connector.insert(self.__dict__)
            print("Data inserted.")

    


