# thegamev2_solver.py
# Solver for The Game v2 challenge (TryHackMe)
# Author: mgledev

def solve_thegamev2():
    print("=== The Game v2 Solver ===\n")
    print("1. DOWNLOAD AND DECOMPILE THE FILE")
    print(" - The provided file is TetrixFinal.exe, a game made with the Godot Engine.")
    print(" - Use the gdre_tools.x86_64 tool to decompile it.")
    print(" - GitHub repository: https://github.com/bruvzg/gdsdecomp")
    print(" - Download precompiled binary from:")
    print("   https://github.com/bruvzg/gdsdecomp/releases\n")
    print(" - Example usage:")
    print("   ./gdre_tools.x86_64 TetrixFinal.exe")
    print(" - After decompilation, a folder named 'extract' will be created containing the project files.\n")

    print("2. FINDING THE FLAG IN THE IMAGE FILE")
    print(" - Inside the 'extract' folder, there is a file named sol.jpg.")
    print(" - Open sol.jpg with an image viewer or browser:")
    print("   xdg-open extract/sol.jpg")
    print(" - The image displays the real flag:")
    print("   THM{MEMORY_CAN_CHANGE_4R34L$-$}\n")

    print("3. OPTIONAL SCRIPT MODIFICATION")
    print(" - In the 'extract/scripts/' folder, there is a gui.gd script responsible for showing the flag when the score reaches 999999.")
    print(" - You can change the condition:")
    print("     if score >= 999999:")
    print("   to:")
    print("     if score >= 1:")
    print(" - This modification makes the flag appear immediately upon starting the game.\n")

    print("4. ADDITIONAL INFO")
    print(" - Searching the TetrixFinal.exe file with 'strings' reveals a fake flag: THM{GAME_MASTER_HACKER}.")
    print(" - The bg.jpg file, after steganographic analysis, does not contain the real flag.\n")

    print("=== END OF SOLVER ===")
    print("Flag to submit:")
    print("THM{MEMORY_CAN_CHANGE_4R34L$-$}")

if __name__ == "__main__":
    solve_thegamev2()
