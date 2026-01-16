#!/usr/bin/env python
import subprocess
import sys


def run_command(command):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Ошибка в команде: {command}")
            print(result.stdout)
            print(result.stderr)
            return False
        return True
    except Exception as e:
        print(f"Исключение при выполнении {command}: {e}")
        return False


def main():
    print("🚀 Запуск линтинга...")

    commands = [
        "black --check src tests",
        "isort --check-only src tests",
        "flake8 src tests",
        "mypy src"
    ]

    all_passed = True
    for cmd in commands:
        print(f"\n▶️  Выполняю: {cmd}")
        if not run_command(cmd):
            all_passed = False

    if all_passed:
        print("\n✅ Все проверки пройдены!")
        sys.exit(0)
    else:
        print("\n❌ Найдены ошибки!")
        sys.exit(1)


if __name__ == "main":
    main()