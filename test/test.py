import unittest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.orm import sessionmaker
from main import app
from db import get_session
from models import User, Expense
from utils.utils import get_password_hash, create_access_token

# Create a separate in-memory test database
TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=test_engine, class_=Session, expire_on_commit=False)

# Override FastAPI's get_session to use the test session
def override_get_session():
    with TestingSessionLocal() as session:
        yield session

app.dependency_overrides[get_session] = override_get_session

class TestExpenseAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        SQLModel.metadata.create_all(test_engine)  # Create tables in test DB

        cls.session = TestingSessionLocal()  # Use test session
        cls.test_user = User(username="testuser", password=get_password_hash("password"), budget=1000)
        cls.session.add(cls.test_user)
        cls.session.commit()
        cls.session.refresh(cls.test_user)

        cls.token = create_access_token({"sub": cls.test_user.username})
        cls.headers = {"Authorization": f"Bearer {cls.token}"}

    @classmethod
    def tearDownClass(cls):
        cls.session.close()
        SQLModel.metadata.drop_all(test_engine)  # Clean up DB

    def test_add_expense(self):
        response = self.client.post("/api/expense/", json={
            "amount": 100,
            "description": "Test expense"
        }, headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])

    def test_get_expenses(self):
        response = self.client.get("/api/expense/", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    def test_read_expense_by_id(self):
        expense = Expense(amount=50, description="Sample", user_id=self.test_user.id)
        self.session.add(expense)
        self.session.commit()
        self.session.refresh(expense)

        response = self.client.get(f"/api/expense/{expense.id}", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["amount"], 50)

    def test_update_expense(self):
        expense = Expense(amount=60, description="Old Description", user_id=self.test_user.id)
        self.session.add(expense)
        self.session.commit()
        self.session.refresh(expense)

        response = self.client.put(f"/api/expense/{expense.id}", json={
            "amount": 120,
            "description": "Updated expense"
        }, headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])

    def test_delete_expense(self):
        expense = Expense(amount=30, description="To be deleted", user_id=self.test_user.id)
        self.session.add(expense)
        self.session.commit()
        self.session.refresh(expense)

        response = self.client.delete(f"/api/expense/{expense.id}", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])

if __name__ == "__main__":
    unittest.main()
