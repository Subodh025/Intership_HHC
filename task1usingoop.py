import json
from pathlib import Path


class Dress:
    def __init__(self, color, dress_type):
        self.color = color
        self.dress_type = dress_type

    def to_dict(self):
        return {
            "color": self.color,
            "dress_type": self.dress_type
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data["color"],
            data["dress_type"]
        )


class Person:
    def __init__(self, face_embedding, body_embedding, dress=None):
        self.face_embedding = face_embedding
        self.body_embedding = body_embedding
        self.dress = dress

    def to_dict(self):
        return {
            "face_embedding": self.face_embedding,
            "body_embedding": self.body_embedding,
            "dress": self.dress.to_dict() if self.dress else None
        }

    @classmethod
    def from_dict(cls, data):
        dress = None

        if data.get("dress"):
            dress = Dress.from_dict(data["dress"])

        return cls(
            data["face_embedding"],
            data["body_embedding"],
            dress
        )


class TrackerLog:
    def __init__(self, person, entry_time, exit_time):
        self.person = person
        self.entry_time = entry_time
        self.exit_time = exit_time

    def to_dict(self):
        return {
            "person_face": self.person.face_embedding,
            "entry_time": self.entry_time,
            "exit_time": self.exit_time
        }


class TrackerSystem:
    DATA_FILE = Path("tracker_data.json")
# To be done in sqlite 
    def __init__(self):
        self.persons = []
        self.logs = []
        self.load()

    def find_person(self, face_embedding):
        for person in self.persons:
            if person.face_embedding == face_embedding:
                return person
        return None

    def add_person(self):
        face = input("Enter Face Embedding: ")
        body = input("Enter Body Embedding: ")
        color = input("Enter Dress Color: ")
        dress_type = input("Enter Dress Type: ")

        dress = Dress(color, dress_type)
        person = Person(face, body, dress)

        self.persons.append(person)

        self.save()
        print("Person Added Successfully")

    def remove_person(self):
        face = input("Enter Face Embedding to Remove: ")

        person = self.find_person(face)

        if not person:
            print("Person Not Found")
            return

        self.persons.remove(person)

        self.logs = [
            log for log in self.logs
            if log.person != person
        ]

        self.save()
        print("Person Removed Successfully")

    def add_tracker_log(self):
        face = input("Enter Face Embedding: ")

        person = self.find_person(face)

        if not person:
            print("Person Not Found")
            return

        entry_time = input("Enter Entry Time: ")
        exit_time = input("Enter Exit Time: ")

        log = TrackerLog(
            person,
            entry_time,
            exit_time
        )

        self.logs.append(log)

        print("Tracker Log Added")

    def show_persons(self):
        if not self.persons:
            print("No Persons Found")
            return

        print("\n--- Persons ---")

        for person in self.persons:
            print(f"Face : {person.face_embedding}")
            print(f"Body : {person.body_embedding}")

            if person.dress:
                print(f"Dress Color : {person.dress.color}")
                print(f"Dress Type  : {person.dress.dress_type}")

            print("-" * 30)

    def show_logs(self):
        if not self.logs:
            print("No Tracker Logs Found")
            return

        print("\n--- Tracker Logs ---")

        for log in self.logs:
            print(
                f"Person Face : {log.person.face_embedding}"
            )
            print(f"Entry Time  : {log.entry_time}")
            print(f"Exit Time   : {log.exit_time}")
            print("-" * 30)

    def save(self):
        data = {
            "persons": [
                person.to_dict()
                for person in self.persons
            ]
        }

        with self.DATA_FILE.open("w") as file:
            json.dump(data, file, indent=4)

    def load(self):
        if not self.DATA_FILE.exists():
            return

        with self.DATA_FILE.open("r") as file:
            data = json.load(file)

        self.persons = [
            Person.from_dict(person)
            for person in data.get("persons", [])
        ]

    def run(self):
        while True:
            print("\n===== TRACKER SYSTEM =====")
            print("1. Add Person")
            print("2. Remove Person")
            print("3. Add Tracker Log")
            print("4. View Persons")
            print("5. View Tracker Logs")
            print("6. Exit")

            choice = input("Enter Choice: ")

            if choice == "1":
                self.add_person()

            elif choice == "2":
                self.remove_person()

            elif choice == "3":
                self.add_tracker_log()

            elif choice == "4":
                self.show_persons()

            elif choice == "5":
                self.show_logs()

            elif choice == "6":
                print("Exiting...")
                break

            else:
                print("Invalid Choice")


if __name__ == "__main__":
    system = TrackerSystem()
    system.run()