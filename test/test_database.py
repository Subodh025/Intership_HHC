
import unittest
from unittest.mock import patch
from task1usingoop import Dress, Person, TrackerLog, DataBaseManager

class TestModels(unittest.TestCase):

    def test_dress_to_dict(self):
        d = Dress("Blue", "Shirt")
        self.assertEqual(d.to_dict(), {
            "color": "Blue",
            "dress_type": "Shirt"
        })
        print("Dress to_dict test passed.")

    def test_dress_from_dict(self):
        d = Dress.from_dict({"color":"Red","dress_type":"Jacket"})
        self.assertEqual(d.color, "Red")
        self.assertEqual(d.dress_type, "Jacket")
        print("Dress from_dict test passed.")

    def test_person_to_dict(self):
        d = Dress("Black","Coat")
        p = Person("face1","body1",d)
        self.assertEqual(p.to_dict()["dress"]["color"], "Black")
        print("Person to_dict test passed.")

    def test_person_from_dict(self):
        p = Person.from_dict({
            "face_embedding":"f1",
            "body_embedding":"b1",
            "dress":{"color":"White","dress_type":"T-Shirt"}
        })
        self.assertEqual(p.face_embedding,"f1")
        self.assertEqual(p.dress.color,"White")
        print("Person from_dict test passed.")

    def test_trackerlog_to_dict(self):
        p = Person("f","b")
        log = TrackerLog(p,"09:00","17:00")
        self.assertEqual(log.to_dict()["entry_time"],"09:00")
        print("TrackerLog to_dict test passed.")


class TestDatabaseManager(unittest.TestCase):

    def setUp(self):
        self.db = DataBaseManager(":memory:")
        self.db.connect()
        self.db.create_tables()

    def tearDown(self):
        self.db.close()

    def test_create_person(self):
        pid = self.db.create_person("face1","body1")
        self.assertIsNotNone(self.db.get_person(pid))
        print("Create person test passed.")

    def test_get_person(self):
        pid = self.db.create_person("face2","body2")
        p = self.db.get_person(pid)
        self.assertEqual(p["face_embedding"],"face2")
        print("Get person test passed.")

    def test_get_person_by_face(self):
        self.db.create_person("face3","body3")
        self.assertEqual(
            self.db.get_person_by_face("face3")["body_embedding"],
            "body3"
        )
        print("Get person by face test passed.")

    def test_get_person_by_body(self):
        self.db.create_person("face4","body4")
        self.assertEqual(
            self.db.get_person_by_body("body4")["face_embedding"],
            "face4"
        )
        print("Get person by body test passed.")

    def test_get_all_persons(self):
        self.db.create_person("a","b")
        self.db.create_person("c","d")
        self.assertEqual(len(self.db.get_all_persons()),2)
        print("Get all persons test passed.")

    def test_update_person(self):
        pid=self.db.create_person("old","old")
        self.db.update_person(pid,face_embedding="new")
        self.assertEqual(self.db.get_person(pid)["face_embedding"],"new")
        print("Update person test passed.")

    def test_delete_person(self):
        pid=self.db.create_person("x","y")
        self.db.delete_person(pid)
        self.assertIsNone(self.db.get_person(pid))
        print("Delete person test passed.")

    def test_add_dress(self):
        pid=self.db.create_person("f","b")
        did=self.db.add_dress(pid,"Blue","Shirt")
        self.assertEqual(self.db.get_dress(did)["dress_color"],"Blue")
        print("Add dress test passed.")

    def test_get_dress(self):
        pid=self.db.create_person("f","b")
        did=self.db.add_dress(pid,"Red","Coat")
        self.assertEqual(self.db.get_dress(did)["dress_type"],"Coat")
        print("Get dress test passed.")

    def test_get_person_dresses(self):
        pid=self.db.create_person("f","b")
        self.db.add_dress(pid,"Blue","Shirt")
        self.db.add_dress(pid,"Black","Pant")
        self.assertEqual(len(self.db.get_person_dresses(pid)),2)
        print("Get person dresses test passed.")

    def test_update_dress(self):
        pid=self.db.create_person("f","b")
        did=self.db.add_dress(pid,"Blue","Shirt")
        self.db.update_dress(did,dress_color="Green")
        self.assertEqual(self.db.get_dress(did)["dress_color"],"Green")
        print("Update dress test passed.")

    def test_delete_dress(self):
        pid=self.db.create_person("f","b")
        did=self.db.add_dress(pid,"Blue","Shirt")
        self.db.delete_dress(did)
        self.assertIsNone(self.db.get_dress(did))
        print("Delete dress test passed.")

    def test_create_tracklog(self):
        pid=self.db.create_person("f","b")
        self.db.create_tracklog(pid,"09:00","17:00")
        self.assertEqual(self.db.get_tracklog(pid)["entry_time"],"09:00")
        print("Create tracklog test passed.")

    def test_get_tracklog(self):
        pid=self.db.create_person("f","b")
        self.db.create_tracklog(pid,"09","17")
        self.assertIsNotNone(self.db.get_tracklog(pid))
        print("Get tracklog test passed.")

    def test_update_tracklog(self):
        pid=self.db.create_person("f","b")
        self.db.create_tracklog(pid,"09","17")
        self.db.update_tracklog(pid,exit_time="18")
        self.assertEqual(self.db.get_tracklog(pid)["exit_time"],"18")
        print("Update tracklog test passed.")

    def test_delete_tracklog(self):
        pid=self.db.create_person("f","b")
        self.db.create_tracklog(pid,"09","17")
        self.db.delete_tracklog(pid)
        self.assertIsNone(self.db.get_tracklog(pid))
        print("Delete tracklog test passed.")

    def test_get_person_with_dresses(self):
        pid=self.db.create_person("f","b")
        self.db.add_dress(pid,"Blue","Shirt")
        person=self.db.get_person_with_dresses(pid)
        self.assertEqual(len(person["dresses"]),1)
        print("Get person with dresses test passed.")

    def test_get_person_full(self):
        pid=self.db.create_person("f","b")
        self.db.add_dress(pid,"Blue","Shirt")
        self.db.create_tracklog(pid,"09","17")
        person=self.db.get_person_full(pid)
        self.assertIn("dresses",person)
        self.assertIn("tracklog",person)
        print("Get person full test passed.")

print("All tests passed successfully!")
if __name__ == "__main__":
    unittest.main()
