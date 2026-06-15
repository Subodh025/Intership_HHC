import json
from pathlib import Path
from pprint import pprint

class Dress:
    def __init__(self, color, dress_type):
        self.color = color
        self.dress_type = dress_type
    def serialize(self):
        return {
            "color": self.color,
            "dress_type": self.dress_type,
        }


class Person:
    def __init__(self, face_embedding, body_embedding, dress=None):
        self.face_embedding = face_embedding
        self.body_embedding = body_embedding
        self.dress = dress
    def serialize(self):
        return {
            "face_embedding": self.face_embedding,
            "body_embedding": self.body_embedding,
            "dress": self.dress.serialize() if self.dress else None,
        }


class TrackerLog:
    def __init__(self, person, entry_time, exit_time):
        self.person = person
        self.entry_time = entry_time
        self.exit_time = exit_time
    def serialize(self):
        return {
            "face_embedding": self.person.face_embedding,
            "body_embedding": self.person.body_embedding,
            "dress": self.person.dress.serialize() if self.person.dress else None,
            "entry_time": self.entry_time,
            "exit_time": self.exit_time,
        }
    
persons = []
tracker_logs = []
DATA_FILE = Path("tracker_data.json")

def find_person(face_embedding):
    for person in persons:
        if person.face_embedding == face_embedding:
            return person
    return None

def create_dress():
    color = input("Enter Dress Color: ")
    dress_type = input("Enter Dress Type: ")
    return Dress(color, dress_type)

def build_person(person_data):
    face_embedding = person_data["face_embedding"]
    body_embedding = person_data["body_embedding"]
    dress_data = person_data.get("dress")
    dress = Dress(dress_data["color"], dress_data["dress_type"]) if dress_data else None
    return Person(face_embedding, body_embedding, dress)

def build_tracker_log(log_data):
    person = build_person(log_data)
    entry_time = log_data["entry_time"]
    exit_time = log_data["exit_time"]
    return TrackerLog(person, entry_time, exit_time)

def load_data():
    if not DATA_FILE.exists():
        return

    with DATA_FILE.open("r") as file:
        data = json.load(file)

    for person_data in data.get("persons", []):
        persons.append(build_person(person_data))

    for log_data in data.get("tracker_logs", []):
        tracker_logs.append(build_tracker_log(log_data))

def save_data():
    data = {
        "persons": [person.serialize() for person in persons],
        "tracker_logs": [log.serialize() for log in tracker_logs]
    }

    with DATA_FILE.open("w") as file:
        json.dump(data, file, indent=4)

def add_person():
    face = input("Enter Face Embedding: ")
    body = input("Enter Body Embedding: ")
    dress = create_dress()

    persons.append(Person(face, body, dress))

    pprint("Person Added Successfully")
    save_data()

def edit_person():
    face = input("Enter Face Embedding of Person to Edit: ")
    person = find_person(face)

    if person is None:
        pprint("Person Not Found")
        return

    new_face = input(f"Enter New Face Embedding [{person.face_embedding}]: ")
    new_body = input(f"Enter New Body Embedding [{person.body_embedding}]: ")

    if new_face:
        person.face_embedding = new_face

    if new_body:
        person.body_embedding = new_body

    pprint("Person Updated Successfully")
    save_data()

def remove_person():
    face = input("Enter Face Embedding of Person to Remove: ")
    person = find_person(face)

    if person is None:
        pprint("Person Not Found")
        return

    persons.remove(person)
    tracker_logs[:] = [log for log in tracker_logs if log.person is not person]
    print("Person Removed Successfully")
    save_data()

def add_dress():
    face = input("Enter Face Embedding of Person: ")
    person = find_person(face)

    if person is None:
        print("Person Not Found")
        return

    person.dress = create_dress()
    print("Dress Added Successfully")
    save_data()

def edit_dress():
    face = input("Enter Face Embedding of Person: ")
    person = find_person(face)

    if person is None:
        print("Person Not Found")
        return

    if person.dress is None:
        print("No Dress Found. Adding New Dress.")
        person.dress = create_dress()
    else:
        new_color = input(f"Enter New Dress Color [{person.dress.color}]: ")
        new_type = input(f"Enter New Dress Type [{person.dress.dress_type}]: ")

        if new_color:
            person.dress.color = new_color

        if new_type:
            person.dress.dress_type = new_type

    print("Dress Updated Successfully")
    save_data()

def remove_dress():
    face = input("Enter Face Embedding of Person: ")
    person = find_person(face)

    if person is None:
        print("Person Not Found")
        return

    if person.dress is None:
        print("No Dress Found")
        return

    person.dress = None
    print("Dress Removed Successfully")
    save_data()

def add_tracker_log():
    face = input("Enter Face Embedding of Person: ")
    body = input("Enter Body Embedding of Person: ")
    color = input("Enter Dress Color of Person: ")
    dress_type = input("Enter Dress Type of Person: ")

    person = None

    for candidate in persons:
        if (
            candidate.face_embedding == face
            and candidate.body_embedding == body
            and candidate.dress is not None
            and candidate.dress.color == color
            and candidate.dress.dress_type == dress_type
        ):
            person = candidate
            break

    if person is None:
        pprint("Person Not Found")
        return

    entry = input("Enter Entry Time: ")
    exit_time = input("Enter Exit Time: ")

    tracker_logs.append(TrackerLog(person, entry, exit_time))

    print("Tracker Log Added")
    save_data()

def search_tracker_log():
    face = input("Enter Face Embedding to Search: ")
    body = input("Enter Body Embedding to Search: ")
    color = input("Enter Dress Color to Search: ")
    dress_type = input("Enter Dress Type to Search: ")

    found = False

    for log in tracker_logs:
        dress = log.person.dress

        if (
            log.person.face_embedding == face
            and log.person.body_embedding == body
            and dress is not None
            and dress.color == color
            and dress.dress_type == dress_type
        ):
            found = True
            print("\nPerson Found")
            print("Face:", log.person.face_embedding)
            print("Body:", log.person.body_embedding)
            print("Dress Color:", dress.color)
            print("Dress Type:", dress.dress_type)
            print("Entry Time:", log.entry_time)
            print("Exit Time:", log.exit_time)

    if not found:
        print("Person Not Found")

load_data()

while True:
    print("1. Add Person")
    print("2. Edit Person")
    print("3. Remove Person")
    print("4. Add Dress")
    print("5. Edit Dress")
    print("6. Remove Dress")
    print("7. Add Tracker Log")
    print("8. Search Tracker Log")
    print("9. Exit")

    choice = input("Enter Choice: ")

    if choice == "1":
        add_person()

    elif choice == "2":
        edit_person()

    elif choice == "3":
        remove_person()

    elif choice == "4":
        add_dress()

    elif choice == "5":
        edit_dress()

    elif choice == "6":
        remove_dress()

    elif choice == "7":
        add_tracker_log()

    elif choice == "8":
        search_tracker_log()

    elif choice == "9":
        print("Exiting...")
        break

    else:
        print("Invalid Choice")
