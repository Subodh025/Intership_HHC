import json


class Dress:
    def __init__(self, color, dress_type):
        self.color = color
        self.dress_type = dress_type


class Person:
    def __init__(self, face_embedding, body_embedding, dress):
        self.face_embedding = face_embedding
        self.body_embedding = body_embedding
        self.dress = dress


class TrackerLog:
    def __init__(self, person, entry_time, exit_time):
        self.person = person
        self.entry_time = entry_time
        self.exit_time = exit_time


# Storage
persons = []
tracker_logs = []


# Save data to JSON
def save_to_json():
    data = {
        "persons": [],
        "tracker_logs": []
    }

    for person in persons:
        data["persons"].append({
            "face_embedding": person.face_embedding,
            "body_embedding": person.body_embedding,
            "dress": {
                "color": person.dress.color,
                "dress_type": person.dress.dress_type
            }
        })

    for log in tracker_logs:
        data["tracker_logs"].append({
            "person_face_embedding": log.person.face_embedding,
            "entry_time": log.entry_time,
            "exit_time": log.exit_time
        })

    with open("tracker_data.json", "w") as file:
        json.dump(data, file, indent=4)


# Add Person
def add_person(person):
    persons.append(person)
    save_to_json()


# Edit Person
def edit_person(face_embedding, new_face=None, new_body=None):
    for person in persons:
        if person.face_embedding == face_embedding:
            if new_face:
                person.face_embedding = new_face
            if new_body:
                person.body_embedding = new_body

    save_to_json()


# Remove Person
def remove_person(face_embedding):
    for person in persons:
        if person.face_embedding == face_embedding:
            persons.remove(person)
            break

    save_to_json()


# Edit Dress
def edit_dress(face_embedding, color=None, dress_type=None):
    for person in persons:
        if person.face_embedding == face_embedding:
            if color:
                person.dress.color = color
            if dress_type:
                person.dress.dress_type = dress_type

    save_to_json()


# Add Tracker Log
def add_tracker_log(person, entry_time, exit_time):
    tracker_logs.append(
        TrackerLog(person, entry_time, exit_time)
    )

    save_to_json()


# Search Person
def search_person(face=None, body=None, color=None):
    for log in tracker_logs:
        person = log.person

        if ((face is None or person.face_embedding == face) and
            (body is None or person.body_embedding == body) and
            (color is None or person.dress.color == color)):

            print("Person Found")
            print("Face:", person.face_embedding)
            print("Body:", person.body_embedding)
            print("Dress Color:", person.dress.color)
            print("Dress Type:", person.dress.dress_type)
            print("Entry Time:", log.entry_time)
            print("Exit Time:", log.exit_time)
            return

    print("Person Not Found")


# -----------------------
# Example Usage
# -----------------------

dress1 = Dress("Blue", "Shirt")

person1 = Person(
    "face123",
    "body123",
    dress1
)

add_person(person1)

add_tracker_log(
    person1,
    "10:00 AM",
    "12:00 PM"
)

search_person(face="face123")