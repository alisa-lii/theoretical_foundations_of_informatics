# -*- coding: utf-8 -*-
"""Лабораторная работа №2"""

INPUT_FILE = "lab_02/participants.txt"
REPORT_FILE = "tournament_report.txt"


def parse_line(line, line_no, used_numbers):
    parts = line.strip().split(";")
    if len(parts) != 6:
        return None, f"Строка {line_no}: неверное количество полей."

    number_s, name, group, s1_s, s2_s, s3_s = parts
    number_s = number_s.strip()
    name = name.strip()
    group = group.strip()

    if not number_s.isdigit() or int(number_s) <= 0:
        return None, f"Строка {line_no}: номер участника должен быть положительным целым числом."
    number = int(number_s)

    if number in used_numbers:
        return None, f"Строка {line_no}: повторяющийся номер участника {number}."

    if name == "":
        return None, f"Строка {line_no}: имя участника не может быть пустым."
    if group == "":
        return None, f"Строка {line_no}: название группы не может быть пустым."

    scores = []
    for raw in (s1_s, s2_s, s3_s):
        raw = raw.strip()
        if not raw.lstrip("-").isdigit():
            return None, f"Строка {line_no}: балл должен быть целым числом."
        val = int(raw)
        if not (0 <= val <= 100):
            return None, f"Строка {line_no}: балл должен находиться в диапазоне от 0 до 100."
        scores.append(val)

    return {"number": number, "name": name, "group": group, "scores": scores}, None


def load_participants(filename):
    participants, errors, used_numbers = [], [], set()
    try:
        with open(filename, "r", encoding="utf-8") as f:
            for i, line in enumerate(f, start=1):
                if line.strip() == "":
                    continue
                p, err = parse_line(line, i, used_numbers)
                if err:
                    errors.append(err)
                else:
                    used_numbers.add(p["number"])
                    participants.append(p)
    except FileNotFoundError:
        print(f"Файл {filename} не найден!")
    return participants, errors


def total_score(p):
    return sum(p["scores"])


def average_score(p):
    return round(sum(p["scores"]) / 3, 2)


def category(p):
    t = total_score(p)
    if t >= 240:
        return "Отличный результат"
    if t >= 180:
        return "Хороший результат"
    if t >= 120:
        return "Удовлетворительный результат"
    return "Требуется подготовка"


def passed_selection(p):
    return total_score(p) >= 180 and all(s >= 50 for s in p["scores"])


def show_all(participants):
    if not participants:
        print("Нет данных.")
        return
    for p in participants:
        s = p["scores"]
        print(f"{p['number']}; {p['name']}; {p['group']}; "
              f"баллы {s[0]},{s[1]},{s[2]}; итог {total_score(p)}; "
              f"средний {average_score(p)}; {category(p)}")


def show_rating(participants):
    rating = sorted(participants, key=lambda p: (-total_score(p), p["name"]))
    for i, p in enumerate(rating, 1):
        print(f"{i}. {p['name']} ({p['group']}) — {total_score(p)}")


def find_by_group(participants):
    query = input("Введите группу: ").strip().lower()
    found = [p for p in participants if p["group"].lower() == query]
    if not found:
        print("Участников этой группы не найдено.")
        return
    for p in found:
        print(f"{p['number']}; {p['name']}; {p['group']}; {total_score(p)}")


def find_by_name(participants):
    query = input("Введите часть имени: ").strip().lower()
    found = [p for p in participants if query in p["name"].lower()]
    if not found:
        print("Никого не найдено.")
        return
    for p in found:
        print(f"{p['number']}; {p['name']}; {p['group']}; {total_score(p)}")


def show_passed(participants):
    found = [p for p in participants if passed_selection(p)]
    if not found:
        print("Никто не прошёл отбор.")
        return
    for p in found:
        print(f"{p['number']}; {p['name']}; {p['group']}; {total_score(p)}")


def unique_groups(participants):
    return sorted({p["group"] for p in participants})


def group_stats(participants):
    stats = {}
    for p in participants:
        stats.setdefault(p["group"], []).append(p)
    result = {}
    for g, plist in stats.items():
        totals = [total_score(p) for p in plist]
        mx = max(totals)
        best = [p["name"] for p in plist if total_score(p) == mx]
        result[g] = {
            "count": len(plist),
            "avg": round(sum(totals) / len(totals), 2),
            "max": mx,
            "best": best,
        }
    return result


def task_stats(participants):
    result = []
    for i in range(3):
        col = [p["scores"][i] for p in participants]
        result.append({
            "avg": round(sum(col) / len(col), 2) if col else 0,
            "min": min(col) if col else 0,
            "max": max(col) if col else 0,
        })
    return result


def show_statistics(participants):
    print("\n=== Уникальные группы ===")
    for g in unique_groups(participants):
        print(" ", g)
    print("\n=== Статистика по группам ===")
    for g, s in sorted(group_stats(participants).items()):
        print(f"{g}: участников {s['count']}, средний {s['avg']}, "
              f"максимум {s['max']}, лучшие: {', '.join(s['best'])}")
    print("\n=== Статистика по задачам ===")
    for i, s in enumerate(task_stats(participants), 1):
        print(f"Задача {i}: средний {s['avg']}, мин {s['min']}, макс {s['max']}")


def save_report(participants, errors):
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write("=== ОТЧЁТ ПО ТУРНИРУ ===\n\n")
        f.write(f"Корректных записей: {len(participants)}\n")
        f.write(f"Некорректных записей: {len(errors)}\n\n")
        f.write("Уникальные группы:\n")
        for g in unique_groups(participants):
            f.write(f"  {g}\n")
        f.write("\nОбщий рейтинг:\n")
        rating = sorted(participants, key=lambda p: (-total_score(p), p["name"]))
        for i, p in enumerate(rating, 1):
            f.write(f"  {i}. {p['name']} ({p['group']}) — {total_score(p)}\n")
        f.write("\nПрошли отбор:\n")
        for p in participants:
            if passed_selection(p):
                f.write(f"  {p['name']} ({p['group']}) — {total_score(p)}\n")
        f.write("\nСтатистика по группам:\n")
        for g, s in sorted(group_stats(participants).items()):
            f.write(f"  {g}: {s['count']} чел., средний {s['avg']}, "
                    f"макс {s['max']}, лучшие: {', '.join(s['best'])}\n")
        f.write("\nСтатистика по задачам:\n")
        for i, s in enumerate(task_stats(participants), 1):
            f.write(f"  Задача {i}: средний {s['avg']}, мин {s['min']}, макс {s['max']}\n")
        f.write("\nОшибки входных данных:\n")
        if not errors:
            f.write("  нет\n")
        else:
            for e in errors:
                f.write(f"  {e}\n")
    print(f"Отчёт сохранён в {REPORT_FILE}")


def menu():
    participants, errors = load_participants(INPUT_FILE)
    print(f"Загружено записей: {len(participants)}, ошибок: {len(errors)}")
    while True:
        print("\n1. Показать всех участников")
        print("2. Показать общий рейтинг")
        print("3. Найти участников по группе")
        print("4. Найти участников по части имени")
        print("5. Показать участников, прошедших отбор")
        print("6. Показать статистику")
        print("7. Сохранить отчёт")
        print("0. Завершить программу")
        choice = input("Ваш выбор: ").strip()
        if choice == "1":
            show_all(participants)
        elif choice == "2":
            show_rating(participants)
        elif choice == "3":
            find_by_group(participants)
        elif choice == "4":
            find_by_name(participants)
        elif choice == "5":
            show_passed(participants)
        elif choice == "6":
            show_statistics(participants)
        elif choice == "7":
            save_report(participants, errors)
        elif choice == "0":
            print("До свидания!")
            break
        else:
            print("Неизвестный пункт меню, попробуйте снова.")


if __name__ == "__main__":
    menu()
