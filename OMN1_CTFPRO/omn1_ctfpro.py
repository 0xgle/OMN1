# omn1_ctfpro.py – Main CLI for OMN1 CTFPRO by mgledev

import sys
import os
import json
import inspect
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.task_manager import add_task, show_task, set_flag, load_task, list_tasks
from core.export import export_pdf
from solvers.passcode_solver import solve_passcode
from solvers.lesson_learned_solver import solve_lesson_learned
from solvers.thegamev2_solver import solve_thegamev2
from solvers.flagvault_solver import solve_flagvault
from solvers.flagvault_v2_solver import solve_flagvault_v2
from solvers.a_bucket_of_phish_solver import solve_a_bucket_of_phish
from solvers.pyrat_solver import solve_pyrat
from solvers.cheesy_solver import solve_cheesy_ctf



# Available solvers
SOLVERS = {
    "PassCode": solve_passcode,
    "Lesson_Learned": solve_lesson_learned,
    "The_Game_v2": solve_thegamev2,
    "FlagVault": solve_flagvault,
    "FlagVault_V2": solve_flagvault_v2,
    "A_Bucket_of_Phish": solve_a_bucket_of_phish,
    "Pyrat": solve_pyrat,
    "Cheesy": solve_cheesy_ctf
}

def menu():
    while True:
        os.system("clear")
        print(r"""
 ██████╗ ███╗   ███╗███╗   ██╗ ██╗
██╔═══██╗████╗ ████║████╗  ██║███║
██║   ██║██╔████╔██║██╔██╗ ██║╚██║
██║   ██║██║╚██╔╝██║██║╚██╗██║ ██║
╚██████╔╝██║ ╚═╝ ██║██║ ╚████║ ██║
 ╚═════╝ ╚═╝     ╚═╝╚═╝  ╚═══╝ ╚═╝  CTFPRO  by mgledev
""")
        print("1. Add new task")
        print("2. List tasks")
        print("3. Show task details")
        print("4. Select and run task")
        print("5. Exit\n")

        choice = input("👉 Select an option (1-5): ").strip()

        if choice == '1':
            name = input("Task name: ")
            difficulty = input("Difficulty (e.g., easy, medium, hard): ")
            ip = input("Target IP (optional): ")
            add_task(arg_obj(name=name, difficulty=difficulty, ip=ip))
            input("\n✅ Task added. Press Enter to continue...")
        elif choice == '2':
            list_tasks(None)
            input("\n📋 Press Enter to continue...")
        elif choice == '3':
            task = input("Enter task name: ")
            show_task(arg_obj(task=task))
            input("\n📌 Press Enter to continue...")
        elif choice == '4':
            choose_and_run_task()
            input("\n🏁 Press Enter after completion...")
        elif choice == '5':
            print("👋 Exiting. Goodbye!")
            break
        else:
            input("❌ Invalid selection. Press Enter to try again...")

def choose_and_run_task():
    try:
        with open("data/ctf_tasks.json", "r") as f:
            tasks = json.load(f)
    except FileNotFoundError:
        print("❌ Missing file: data/ctf_tasks.json.")
        return

    if not tasks:
        print("⚠️ No tasks available.")
        return

    print("\n📘 Available Tasks:")
    for i, task in enumerate(tasks, 1):
        print(f"{i}. {task['name']} [{task['difficulty']}]")
    print("\n↩️ Type `exit` to return to the main menu.")

    user_input = input("\n👉 Enter task number: ").strip()
    if user_input.lower() == 'exit':
        print("↩️ Returning to main menu...")
        return

    try:
        index = int(user_input) - 1
        if 0 <= index < len(tasks):
            task_name = tasks[index]['name']
            normalized = task_name.replace(" ", "_").replace("?", "")
            if normalized not in SOLVERS:
                print(f"❌ No solver available for: {task_name}")
                return

            solver = SOLVERS[normalized]
            sig = inspect.signature(solver)

            if len(sig.parameters) == 2:
                ip = input("🔗 Enter target IP (or type 'exit' to return): ").strip()
                if ip.lower() == 'exit':
                    print("↩️ Returning to main menu...")
                    return
                solver(task_name, ip)
            else:
                solver()
        else:
            print("❌ Invalid task number.")
    except ValueError:
        print("❌ Please enter a valid number.")

class arg_obj:
    def __init__(self, **entries):
        self.__dict__.update(entries)

if __name__ == '__main__':
    menu()
