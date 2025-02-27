import os
import shutil

def setup_project_directories():
    """Setup the correct directory structure for the project"""
    # Create necessary directories
    directories = [
        "views",
        "utils",
        "data",
        "data/gangs",
        "data/territories",
        "data/battles",
        "data/equipment",
        "logs"
    ]
    
    for directory in directories:
        os.makedirs(f"/workspaces/Necromunda-Game-Manager/{directory}", exist_ok=True)
    
    # Move files from pages to views if needed
    if os.path.exists("/workspaces/Necromunda-Game-Manager/pages"):
        page_files = os.listdir("/workspaces/Necromunda-Game-Manager/pages")
        for file in page_files:
            if file.endswith(".py"):
                src = f"/workspaces/Necromunda-Game-Manager/pages/{file}"
                dst = f"/workspaces/Necromunda-Game-Manager/views/{file}"
                
                # Only copy if destination doesn't exist or is older
                if not os.path.exists(dst) or os.path.getmtime(src) > os.path.getmtime(dst):
                    shutil.copy2(src, dst)
                    print(f"Moved {file} to views directory")

    # Delete redundant app.py if it exists
    if os.path.exists("/workspaces/Necromunda-Game-Manager/app.py"):
        os.remove("/workspaces/Necromunda-Game-Manager/app.py")
        print("Removed redundant app.py")

if __name__ == "__main__":
    setup_project_directories()
