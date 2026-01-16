#!/usr/bin/env python
import subprocess


def main():
    print("🎨 Форматирование кода...")

    commands = [
        "black src tests",
        "isort src tests"
    ]

    for cmd in commands:
        print(f"\n▶️  Выполняю: {cmd}")
        subprocess.run(cmd, shell=True)

    print("\n✅ Форматирование завершено!")


if __name__ == "main":
    main()