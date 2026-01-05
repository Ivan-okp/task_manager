"""
Набор тест-кейсов для роутера задач (task router).

Этот модуль содержит параметризованные данные (test cases), которые используются в
юнит-/интеграционных тестах для проверки эндпоинтов, связанных с задачами.
Каждый элемент в списках — кортеж, описывающий входные данные и ожидаемое поведение
API при определённом сценарии.
"""

test_cases_task_router_for_get_task = [
    (
        1,
        200,
        {"title": f"testtask_1", "body": f"testbody_1_for_testtask1", "status": "New", "user": 1},
    ),
    (
        4,
        404,
        None,
    ),
    (
        True,
        422,
        None,
    ),
    (
        None,
        422,
        None,
    ),
]

test_cases_task_router_for_add_task = [
    (
        {"title": "task_for_test", "body": "body for test task", "status": "New", "user": 1},
        200,
        {"title": "task_for_test", "body": "body for test task", "status": "New", "user": 1, "id": 1},
    ),
    (
        {"body": "body for test task", "status": "New", "user": 1},
        422,
        None,
    ),
    (
        {"title": "task_for_test", "status": "New", "user": 1},
        422,
        None,
    ),
    (
        {"title": "task_for_test", "body": "body for test task", "user": 1},
        422,
        None,
    ),
    (
        {"title": "task_for_test", "body": "body for test task", "status": "New"},
        422,
        None,
    ),
    (
        {"title": 12345, "body": "body for test task", "status": "New", "user": 1},
        422,
        None,
    ),
    (
        {"title": "task_for_test", "body": 12345, "status": "New", "user": 1},
        422,
        None,
    ),
    (
        {"title": "task_for_test", "body": "body for test task", "status": "Old", "user": 1},
        422,
        None,
    ),
    (
        {"title": "task_for_test", "body": "body for test task", "status": "New", "user": "user"},
        422,
        None,
    ),
]

test_cases_task_router_for_update_task = [
    (
        0,
        1,
        {"title": "test add task", "body": "test body for test add", "status": "New"},
        200,
        {"id": 1, "title": "test add task", "body": "test body for test add", "status": "New", "user": 1},
    ),
    (
        0,
        None,
        {"title": "test add task", "body": "test body for test add", "status": "New"},
        422,
        None,
    ),
    (
        0,
        11,
        {"title": "test add task", "body": "test body for test add", "status": "New"},
        404,
        None,
    ),
    (
        0,
        False,
        {"title": "test add task", "body": "test body for test add", "status": "New"},
        422,
        None,
    ),
    (
        0,
        1,
        {"body": "test body for test add", "status": "New"},
        422,
        None,
    ),
    (
        0,
        1,
        {"title": "test add task", "status": "New"},
        422,
        None,
    ),
    (
        0,
        1,
        {"title": "test add task", "body": "test body for test add"},
        422,
        None,
    ),
]

test_cases_task_router_for_delete_task = [
    (
        0,
        1,
        200,
        {"message": "Task with ID 1 deleted successfully"},
    ),
    (
        0,
        None,
        422,
        None,
    ),
    (
        0,
        4,
        404,
        None,
    ),
    (
        0,
        False,
        422,
        None,
    ),
]
