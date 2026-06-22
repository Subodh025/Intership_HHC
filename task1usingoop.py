import sqlite3

from task1usingoop import DataBaseManager


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
    def __init__(self):
        self.db_manager = DataBaseManager("tracker_system.db")
        self.db_manager.connect()
        self.db_manager.create_tables()

    def add_person(self):
        face = input("Enter Face Embedding: ")
        body = input("Enter Body Embedding: ")
        color = input("Enter Dress Color: ")
        dress_type = input("Enter Dress Type: ")

        person_id = self.db_manager.create_person(face, body)

        self.db_manager.add_dress(
            person_id,
            color,
            dress_type
        )

        print("Person Added Successfully")

    def remove_person(self):
        face = input("Enter Face Embedding to Remove: ")

        person = self.db_manager.get_person_by_face(face)

        if not person:
            print("Person Not Found")
            return

        self.db_manager.delete_person(person["id"])

        print("Person Removed Successfully")

    def add_tracker_log(self):
        face = input("Enter Face Embedding: ")

        person = self.db_manager.get_person_by_face(face)

        if not person:
            print("Person Not Found")
            return

        entry_time = input("Enter Entry Time: ")
        exit_time = input("Enter Exit Time: ")

        # Update existing log if present
        if self.db_manager.get_tracklog(person["id"]):
            self.db_manager.update_tracklog(
                person["id"],
                entry_time,
                exit_time
            )
        else:
            self.db_manager.create_tracklog(
                person["id"],
                entry_time,
                exit_time
            )

        print("Tracker Log Added")

    def show_persons(self):
        persons = self.db_manager.get_all_persons()

        if not persons:
            print("No Persons Found")
            return

        print("\n--- Persons ---")

        for person in persons:
            dresses = self.db_manager.get_person_dresses(person["id"])

            print(f"Face : {person['face_embedding']}")
            print(f"Body : {person['body_embedding']}")

            for dress in dresses:
                print(f"Dress Color : {dress['dress_color']}")
                print(f"Dress Type  : {dress['dress_type']}")

            print("-" * 30)

    def show_logs(self):
        print("\n--- Tracker Logs ---")

        persons = self.db_manager.get_all_persons()

        found = False

        for person in persons:
            log = self.db_manager.get_tracklog(person["id"])

            if log:
                found = True

                print(f"Person Face : {person['face_embedding']}")
                print(f"Entry Time  : {log['entry_time']}")
                print(f"Exit Time   : {log['exit_time']}")
                print("-" * 30)

        if not found:
            print("No Tracker Logs Found")

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
                self.db_manager.create_person()

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
                self.db_manager.close()
                break

            else:
                print("Invalid Choice")

import sqlite3
from typing import List, Optional


class DataBaseManager:
    """Manage SQLite database connection and provide CRUD operations.

    This class is a lightweight, explicit database manager that handles
    connecting to an SQLite database, creating schema tables, and performing
    CRUD operations for persons, dresses, and tracker logs. Methods return
    plain Python dictionaries for rows and raise no exceptions; callers
    should ensure `connect()` has been called before use.
    """

    def __init__(self, db_path: str):
        """Initialize the manager with a database path.

        Args:
            db_path: Filesystem path to the SQLite database file. The file
                will be created automatically by SQLite when a connection
                is opened if it does not already exist.

        Side effects:
            Initializes `self.connection` to None. Call `connect()` to open
            the database connection before executing queries.
        """
        self.db_path = db_path
        self.connection = None

    def connect(self):
        """Open a connection to the SQLite database.

        This method sets `self.connection` to an active sqlite3.Connection
        instance and configures the `row_factory` so query results are
        returned as mapping-like rows (sqlite3.Row). Call `close()` when
        finished to release resources.
        """

        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row

    def close(self):
        """Close the current database connection if one is open.

        This is safe to call repeatedly; if no connection exists the method
        does nothing.
        """

        if self.connection:
            self.connection.close()

    def create_tables(self):
        """Create the required database tables if they do not exist.

        The schema created is minimal and intended for the tracker system:
        - `persons` stores a unique integer id and embeddings for face and body.
        - `dresses` stores zero-or-more dresses per person and references
          `persons(id)` with ON DELETE CASCADE so dresses are removed when a
          person is deleted.
        - `tracker_logs` stores a one-to-one tracking record per person (the
          table enforces `person_id` uniqueness) with entry and optional
          exit timestamps. It also cascades on person deletion.

        Preconditions:
            `connect()` must have been called and `self.connection` must be
            a valid sqlite3.Connection.
        """

        cursor = self.connection.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS persons(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            face_embedding TEXT NOT NULL,
            body_embedding TEXT NOT NULL
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS dresses(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            person_id INTEGER NOT NULL,
            dress_color TEXT,
            dress_type TEXT,
            FOREIGN KEY(person_id) REFERENCES persons(id) ON DELETE CASCADE
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tracker_logs(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            person_id INTEGER UNIQUE NOT NULL,
            entry_time TEXT NOT NULL,
            exit_time TEXT,
            FOREIGN KEY(person_id) REFERENCES persons(id) ON DELETE CASCADE
        )
        """)

        self.connection.commit()

    # ======================================================
    # PERSON CRUD
    # ======================================================
    def create_person(self, face_embedding: str, body_embedding: str) -> int:
        """Insert a new person record into the database.

        Args:
            face_embedding: A string representation of the face embedding.
            body_embedding: A string representation of the body embedding.

        Returns:
            The integer `id` of the newly created person record.

        Preconditions:
            `connect()` must have been called and `self.connection` must be
            valid.
        """

        cursor = self.connection.cursor()
        cursor.execute(
            """
            INSERT INTO persons(face_embedding, body_embedding)
            VALUES (?, ?)
            """,
            (face_embedding, body_embedding)
        )
        self.connection.commit()
        return cursor.lastrowid

    def get_person(self, person_id: int) -> Optional[dict]:
        """Retrieve a single person by their integer id.

        Args:
            person_id: The integer primary key of the person.

        Returns:
            A dict mapping column names to values if found, otherwise None.
        """

        cursor = self.connection.cursor()
        cursor.execute(
            "SELECT * FROM persons WHERE id=?",
            (person_id,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_person_by_face(self, face_embedding: str) -> Optional[dict]:
        """Retrieve a single person by their face embedding.

        Args:
            face_embedding: The string representation of the person's face embedding.

        Returns:
            A dict mapping column names to values if found, otherwise None.
        """

        cursor = self.connection.cursor()
        cursor.execute(
            "SELECT * FROM persons WHERE face_embedding=?",
            (face_embedding,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_person_by_body(self, body_embedding: str) -> Optional[dict]:
        """Retrieve a single person by their body embedding.

        Args:
            body_embedding: The string representation of the person's body embedding.

        Returns:
            A dict mapping column names to values if found, otherwise None.
        """

        cursor = self.connection.cursor()
        cursor.execute(
            "SELECT * FROM persons WHERE body_embedding=?",
            (body_embedding,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_all_persons(self) -> List[dict]:
        """Return a list of all person records in the database.

        Returns:
            A list of dicts, each representing a row from the `persons`
            table. If no persons exist an empty list is returned.
        """

        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM persons")
        return [dict(row) for row in cursor.fetchall()]

    def update_person(
        self,
        person_id: int,
        face_embedding=None,
        body_embedding=None
    ):
        """Update fields for a person record.

        Only non-None arguments are applied. This method is safe to call with
        both `face_embedding` and `body_embedding` set to None (it will be a
        no-op in that case).

        Args:
            person_id: The integer id of the person to update.
            face_embedding: New face embedding string, or None to leave unchanged.
            body_embedding: New body embedding string, or None to leave unchanged.

        Side effects:
            Commits the transaction if an update is performed.
        """

        cursor = self.connection.cursor()

        fields = []
        values = []

        if face_embedding is not None:
            fields.append("face_embedding=?")
            values.append(face_embedding)

        if body_embedding is not None:
            fields.append("body_embedding=?")
            values.append(body_embedding)

        if not fields:
            return

        values.append(person_id)

        cursor.execute(
            f"""
            UPDATE persons
            SET {', '.join(fields)}
            WHERE id=?
            """,
            values
        )
        self.connection.commit()

    def delete_person(self, person_id: int):
        """Delete a person and cascade-delete related dresses and logs.

        Args:
            person_id: The integer id of the person to remove.

        Side effects:
            Commits the deletion. If the person does not exist nothing is
            raised by SQLite and the method simply commits with no rows
            affected.
        """

        cursor = self.connection.cursor()
        cursor.execute(
            "DELETE FROM persons WHERE id=?",
            (person_id,)
        )
        self.connection.commit()

    # ======================================================
    # DRESS CRUD (One Person -> Many Dresses)
    # ======================================================
    def add_dress(
        self,
        person_id: int,
        dress_color: str,
        dress_type: str
    ) -> int:
        """Add a dress record associated with a person.

        Args:
            person_id: The integer id of the person who wears the dress.
            dress_color: Textual color description.
            dress_type: Textual type/description of the dress.

        Returns:
            The integer id of the newly inserted dress record.
        """

        cursor = self.connection.cursor()

        cursor.execute(
            """
            INSERT INTO dresses(person_id, dress_color, dress_type)
            VALUES (?, ?, ?)
            """,
            (person_id, dress_color, dress_type)
        )

        self.connection.commit()
        return cursor.lastrowid

    def get_dress(self, dress_id: int):
        """Retrieve a dress record by its id.

        Args:
            dress_id: Integer primary key of the dress.

        Returns:
            A dict representing the dress row, or None if not found.
        """

        cursor = self.connection.cursor()
        cursor.execute(
            "SELECT * FROM dresses WHERE id=?",
            (dress_id,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_person_dresses(self, person_id: int):
        """Return all dresses associated with a given person.

        Args:
            person_id: Integer id of the person.

        Returns:
            A list of dicts for each dress row; empty list if none exist.
        """

        cursor = self.connection.cursor()
        cursor.execute(
            "SELECT * FROM dresses WHERE person_id=?",
            (person_id,)
        )
        return [dict(r) for r in cursor.fetchall()]

    def update_dress(
        self,
        dress_id: int,
        dress_color=None,
        dress_type=None
    ):
        """Update fields on a dress record.

        Only non-None values are applied. If both are None the method does
        nothing.

        Args:
            dress_id: Integer id of the dress to update.
            dress_color: New color string or None.
            dress_type: New type string or None.
        """

        fields = []
        values = []

        if dress_color is not None:
            fields.append("dress_color=?")
            values.append(dress_color)

        if dress_type is not None:
            fields.append("dress_type=?")
            values.append(dress_type)

        if not fields:
            return

        values.append(dress_id)

        cursor = self.connection.cursor()
        cursor.execute(
            f"""
            UPDATE dresses
            SET {', '.join(fields)}
            WHERE id=?
            """,
            values
        )

        self.connection.commit()

    def delete_dress(self, dress_id: int):
        """Remove a dress record by id.

        Args:
            dress_id: Integer id of the dress to delete.
        """

        cursor = self.connection.cursor()
        cursor.execute(
            "DELETE FROM dresses WHERE id=?",
            (dress_id,)
        )
        self.connection.commit()

    # ======================================================
    # TRACKLOG CRUD (One-To-One)
    # ======================================================
    def create_tracklog(
        self,
        person_id: int,
        entry_time: str,
        exit_time: str = None
    ) -> int:
        """Create or insert a tracker log for a person.

        Args:
            person_id: Integer id of the person being tracked. The
                `tracker_logs` table enforces uniqueness of `person_id` so a
                second insert for the same person will fail with an
                IntegrityError unless the existing row is removed or updated.
            entry_time: Textual timestamp for entry (any string format).
            exit_time: Optional textual timestamp for exit.

        Returns:
            The integer id of the newly created tracker_logs row.
        """

        cursor = self.connection.cursor()

        cursor.execute(
            """
            INSERT INTO tracker_logs(person_id, entry_time, exit_time)
            VALUES (?, ?, ?)
            """,
            (person_id, entry_time, exit_time)
        )

        self.connection.commit()
        return cursor.lastrowid

    def get_tracklog(self, person_id: int):
        """Retrieve the tracker log for a given person.

        Args:
            person_id: Integer id of the person whose tracklog to fetch.

        Returns:
            A dict of the tracker_logs row if present, otherwise None.
        """

        cursor = self.connection.cursor()
        cursor.execute(
            """
            SELECT * FROM tracker_logs
            WHERE person_id=?
            """,
            (person_id,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None

    def update_tracklog(
        self,
        person_id: int,
        entry_time=None,
        exit_time=None
    ):
        """Update fields on a person's tracker log.

        Only non-None arguments are applied. If neither `entry_time` nor
        `exit_time` are provided the method performs no action.

        Args:
            person_id: Integer id of the person whose log will be updated.
            entry_time: New entry time string or None.
            exit_time: New exit time string or None.
        """

        fields = []
        values = []

        if entry_time is not None:
            fields.append("entry_time=?")
            values.append(entry_time)

        if exit_time is not None:
            fields.append("exit_time=?")
            values.append(exit_time)

        if not fields:
            return

        values.append(person_id)

        cursor = self.connection.cursor()
        cursor.execute(
            f"""
            UPDATE tracker_logs
            SET {', '.join(fields)}
            WHERE person_id=?
            """,
            values
        )

        self.connection.commit()

    def delete_tracklog(self, person_id: int):
        """Delete the tracker log for a given person id.

        Args:
            person_id: Integer id of the person whose tracklog will be removed.
        """

        cursor = self.connection.cursor()
        cursor.execute(
            """
            DELETE FROM tracker_logs
            WHERE person_id=?
            """,
            (person_id,)
        )
        self.connection.commit()

    # ======================================================
    # ORM-like relationship methods
    # ======================================================
    def get_person_with_dresses(self, person_id: int):
        """Return a person record augmented with their dresses.

        Args:
            person_id: Integer id of the person to fetch.

        Returns:
            A dict with the person row and a `dresses` key containing a list
            of dresses. If the person does not exist, returns None.
        """

        person = self.get_person(person_id)
        if person:
            person["dresses"] = self.get_person_dresses(person_id)
        return person

    def get_person_full(self, person_id: int):
        """Return a person record with dresses and their tracker log.

        This is a convenience method that composes `get_person`,
        `get_person_dresses`, and `get_tracklog` to produce a single
        dictionary representing the person and their related data.

        Args:
            person_id: Integer id of the person to fetch.

        Returns:
            A dict with keys `dresses` and `tracklog` added when the person
            exists; otherwise returns None.
        """

        person = self.get_person(person_id)

        if person:
            person["dresses"] = self.get_person_dresses(person_id)
            person["tracklog"] = self.get_tracklog(person_id)

        return person
if __name__ == "__main__":
    system = TrackerSystem()
    system.run()