"""
Main Application Entry Point
Runs the Computer Science Game Collection
"""

import tkinter as tk
from main_menu import GameCollectionUI

def main():
    """Main function to run the game collection"""
    print("🎮 Starting Computer Science Game Collection...")
    print("📦 Complete Collection with All 5 Games")
    print("📋 Available Games:")
    print("  • 🐍 Snake and Ladder")
    print("  • 🚦 Traffic Simulation") 
    print("  • 🗺️ Traveling Salesman")
    print("  • 🗼 Tower of Hanoi")
    print("  • ♕ Eight Queens")
    print()
    
    # Check dependencies
    try:
        import matplotlib
        import networkx
        print("✅ All dependencies are available!")
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please install required packages:")
        print("pip install matplotlib networkx")
        return
    
    # Create and run the game collection
    root = tk.Tk()
    app = GameCollectionUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()