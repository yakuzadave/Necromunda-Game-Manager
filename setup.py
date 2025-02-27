import os
import shutil
import sys

def setup_project():
    """Set up the proper directory structure and fix any path issues"""
    print("Setting up Necromunda Game Manager project...")
    
    # Create necessary directories
    directories = [
        "views", 
        "utils", 
        "data",
        "data/gangs",
        "data/territories", 
        "data/battles", 
        "data/equipment",
        "logs",
        "backups",
        "static",
        "static/map_templates"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ Created {directory} directory")
    
    # Move files from pages/ to views/ if the pages folder exists
    if os.path.exists("pages"):
        for filename in os.listdir("pages"):
            if filename.endswith(".py"):
                src_path = os.path.join("pages", filename)
                dst_path = os.path.join("views", filename)
                if not os.path.exists(dst_path):
                    shutil.copy2(src_path, dst_path)
                    print(f"✓ Copied {filename} from pages/ to views/")
        
        print("\nWould you like to remove the old 'pages' directory? (y/n)")
        response = input().lower()
        if response == 'y':
            shutil.rmtree("pages")
            print("✓ Removed old 'pages' directory")
        else:
            print("Kept 'pages' directory")
    
    # Remove redundant app.py if it exists
    if os.path.exists("app.py"):
        os.remove("app.py")
        print("✓ Removed redundant app.py")
    
    print("\nSetup complete! Run 'streamlit run main.py' to start the application.")

if __name__ == "__main__":
    setup_project()
