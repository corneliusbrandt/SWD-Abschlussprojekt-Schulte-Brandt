import os
from tinydb import TinyDB, Query

class Mechanism:
    db_connector = TinyDB(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.json')).table('mechanisms')

    def __init__(self, name, table_points, table_links) -> None:
        """Create a new mechanism based on the given name"""
        self.name = name
        self.table_points = table_points
        self.table_links = table_links

    def store_data(self)-> None:
        """Save the mechanism to the database"""
        print("Storing data...")
        MechanismQuery = Query()
        result = self.db_connector.search(MechanismQuery.name == self.name)

        if result:
            result = self.db_connector.update(self.__dict__, doc_ids=[result[0].doc_id])
            print("Data updated.")
        else:
            self.db_connector.insert(self.__dict__)
            print("Data inserted.")

    def delete_data(self) -> None:
        """Delete the mechanism from the database"""
        print("Deleting data...")
        MechanismQuery = Query()
        result = self.db_connector.search(MechanismQuery.name == self.name)
        if result:
            self.db_connector.remove(doc_ids=[result[0].doc_id])
            print("Data deleted.")
        else:
            print("Data not found.")

    @classmethod
    def find_all(cls) -> list:
        """Find all mechanisms in the database"""
        # Load all data from the database and create instances of the Mechanism class
        mechanisms = []
        for mechanism_data in Mechanism.db_connector.all():
            mechanisms.append(Mechanism(mechanism_data['name'], mechanism_data['table_points'], mechanism_data['table_links']))
        return mechanisms
    
    @classmethod
    def find_by_attribute(cls, attribute, attribute_value, num_to_return=1) -> 'Mechanism':
        """Find a mechanism in the database by the given attribute"""
        # Load all data from the database and create instances of the Mechanism class
        MechanismQuery = Query()
        result = cls.db_connector.search(MechanismQuery[attribute] == attribute_value)
        if result:
            data = result[:num_to_return]
            mechanisms = [cls(d["name"], d["table_points"], d["table_links"]) for d in data]
            return mechanisms if num_to_return > 1 else mechanisms[0]
        else:
            return None



    


