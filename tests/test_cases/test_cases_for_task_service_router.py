"""
Набор параметризованных тест-кейсов для service-роутера задач (service/task-related endpoints).

Этот модуль содержит данные (test cases), которые используются в интеграционных/сервисных
тестах для проверки защищённых (требующих авторизации) эндпоинтов, связанных с задачами.
"""

test_cases_service_task_router_for_get_task = [
    (
        0,
        {"token": "00000000"},
        200,
        [
            {"title": "testtask_1", "body": "testbody_1_for_testtask1", "status": "New", "user": 1, "id": 1},
            {"title": "testtask_2", "body": "testbody_2_for_testtask2", "status": "New", "user": 1, "id": 2},
            {"title": "testtask_3", "body": "testbody_3_for_testtask3", "status": "New", "user": 1, "id": 3},
        ]
    ),
    (
        1,
        {"token": "00000000"},
        401,
        None,
    )
]

test_cases_service_task_router_for_get_specific_task = [
    (
        0,
        {"token": "00000000"},
        1,
        "testtask_1",
        200,
        {"title": "testtask_1", "body": "testbody_1_for_testtask1", "status": "New", "user": 1, "id": 1},
    ),
    (
        0,
        {"token": "00000000"},
        4,
        "testtask_4",
        404,
        None,
    ),
    (
        0,
        {"token": "00000000"},
        False,
        12345,
        404,
        None,
    ),
    (
        0,
        {"token": "00000000"},
        None,
        None,
        404,
        None,
    ),
    (
        1,
        {"token": "00000000"},
        1,
        "testtask_1",
        401,
        None,
    ),
]

test_cases_service_task_router_for_create_task = [
    (
        1,
        {"token": "00000000"},
        {"title": "test add task", "body": "test body for test add", "status": "New", "user": 1},
        200,
        {"title": "test add task", "body": "test body for test add", "status": "New", "user": 1, "id": 1},
    ),
    (
        0,
        {"token": "00000000"},
        {"title": "test add task", "body": "test body for test add", "status": "New", "user": 1},
        401,
        None,
    ),
    (
        1,
        {"token": "00000000"},
        {"body": "test body for test add", "status": "New", "user": 1},
        422,
        None,
    ),
    (
        1,
        {"token": "00000000"},
        {"title": "test add task", "status": "New", "user": 1},
        422,
        None,
    ),
    (
        1,
        {"token": "00000000"},
        {"title": "test add task", "body": "test body for test add", "user": 1},
        422,
        None,
    ),
]

test_cases_service_task_router_for_update_task = [
    (
        1,
        1,
        {"token": "00000000"},
        {"title": "test update task", "body": "test body for test update", "status": "New"},
        1,
        "testtask_2",
        200,
        {"title": "test update task", "body": "test body for test update", "status": "New", "user": 1},
    ),
    (
        0,
        1,
        {"token": "00000000"},
        {"title": "test update task", "body": "test body for test update", "status": "New"},
        1,
        "testtask_2",
        401,
        None,
    ),
    (
        1,
        0,
        {"token": "00000000"},
        {"title": "test update task", "body": "test body for test update", "status": "New"},
        4,
        "testtask_4",
        404,
        None,
    ),
    (
        1,
        1,
        {"token": "00000000"},
        {"body": "test body for test update", "status": "New"},
        1,
        "testtask_2",
        422,
        None,
    ),
    (
        1,
        1,
        {"token": "00000000"},
        {"title": "test update task", "status": "New"},
        1,
        "testtask_2",
        422,
        None,
    ),
    (
        1,
        1,
        {"token": "00000000"},
        {"title": "test update task", "body": "test body for test update"},
        1,
        "testtask_2",
        422,
        None,
    ),
]

test_cases_service_task_router_for_delete_task = [
    (
        1,
        1,
        {"token": "00000000"},
        1,
        "testtask_2",
        200,
        {"message": "Task with ID '1' was deleted"},
        {"message": f"Task with title 'testtask_2' was deleted"}
    ),
    (
        0,
        1,
        {"token": "00000000"},
        1,
        "testtask_2",
        401,
        None,
        None,
    ),
    (
        1,
        0,
        {"token": "00000000"},
        4,
        "testtask_4",
        404,
        None,
        None,
    ),
]
