"""
Набор тест-кейсов для роутера задач (task router).
"""

test_cases_task_router_for_get_task = [
    (
        1,
        200,
        {
            "title": "testtask_1",
            "body": "testbody_1_for_testtask1",
            "status": "New",
            "user": 1,
        },
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
        {
            "title": "task_for_test",
            "body": "body for test task",
            "status": "New",
            "user": 1,
        },
        200,
        {
            "title": "task_for_test",
            "body": "body for test task",
            "status": "New",
            "user": 1,
            "id": 1,
        },
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
        {
            "title": "task_for_test",
            "body": "body for test task",
            "status": "Old",
            "user": 1,
        },
        422,
        None,
    ),
    (
        {
            "title": "task_for_test",
            "body": "body for test task",
            "status": "New",
            "user": "user",
        },
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
        {
            "id": 1,
            "title": "test add task",
            "body": "test body for test add",
            "status": "New",
            "user": 1,
        },
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
        200,
        {
            "id": 1,
            "title": "testtask_1",
            "body": "test body for test add",
            "status": "New",
            "user": 1,
        },
    ),
    (
        0,
        1,
        {"title": "test add task", "status": "New"},
        200,
        {
            "id": 1,
            "title": "test add task",
            "body": "testbody_1_for_testtask1",
            "status": "New",
            "user": 1,
        },
    ),
    (
        0,
        1,
        {"title": "test add task", "body": "test body for test add"},
        422,
        {
            "id": 1,
            "title": "test add task",
            "body": "test body for test add",
            "status": "New",
            "user": 1,
        },
    ),
]

test_cases_task_router_for_delete_task = [
    (
        0,
        1,
        204,
        "",
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
