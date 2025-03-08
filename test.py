from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# Test User Registration
def test_register():
    response = client.post("/register", json={"username": "testuser", "password": "testpass"})
    assert response.status_code == 201
    assert response.json()["username"] == "testuser"

# Test User Login
def test_login():
    response = client.post("/login", json={"username": "testuser", "password": "testpass"})
    assert response.status_code == 200
    assert "access_token" in response.json()
    return response.json()["access_token"]

# Helper function to get headers with token
def get_auth_headers():
    token = test_login()
    return {"Authorization": f"Bearer {token}"}

# Test Create Task
def test_create_task():
    headers = get_auth_headers()
    response = client.post("/tasks", json={"title": "Test Task", "description": "Test Description", "completed": False, "subtasks": []}, headers=headers)
    assert response.status_code == 201
    assert response.json()["title"] == "Test Task"
    return response.json()["id"], headers

# Test Update Task
def test_update_task():
    task_id, headers = test_create_task()
    response = client.put(f"/tasks/{task_id}", json={"title": "Updated Task", "description": "Updated Description", "completed": False, "subtasks": []}, headers=headers)
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Task"

# Test Create Subtask
def test_create_subtask():
    task_id, headers = test_create_task()
    response = client.post(f"/tasks/{task_id}/subtasks", json={"title": "Subtask 1", "completed": False}, headers=headers)
    assert response.status_code == 201
    assert response.json()["title"] == "Subtask 1"
    return task_id, response.json()["id"], headers

# Test Update Subtask
def test_update_subtask():
    task_id, subtask_id, headers = test_create_subtask()
    response = client.put(f"/tasks/{task_id}/subtasks/{subtask_id}", json={"title": "Updated Subtask", "completed": True}, headers=headers)
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Subtask"

# Test Mark Task as Completed
def test_mark_task_completed():
    task_id, headers = test_create_task()
    response = client.patch(f"/tasks/{task_id}/status", json={"completed": True}, headers=headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Task status updated"

# Test Mark Subtask as Completed
def test_mark_subtask_completed():
    task_id, subtask_id, headers = test_create_subtask()
    response = client.patch(f"/tasks/{task_id}/subtasks/{subtask_id}/status", json={"completed": True}, headers=headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Subtask status updated"

# Test Get Tasks
def test_get_tasks():
    headers = get_auth_headers()
    response = client.get("/tasks", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

# Test Get Subtasks
def test_get_subtasks():
    task_id, _, headers = test_create_subtask()
    response = client.get(f"/tasks/{task_id}/subtasks", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

# Test Delete Task
def test_delete_task():
    task_id, headers = test_create_task()
    response = client.delete(f"/tasks/{task_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Task deleted"
    