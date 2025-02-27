import os
import sys
import shutil
import importlib.util

# First ensure utils directory exists
os.makedirs("utils", exist_ok=True)

# Check if setup_directories.py exists
setup_dir_path = os.path.join("utils", "setup_directories.py")
if os.path.exists(setup_dir_path):
    # Import and run setup_directories
    spec = importlib.util.spec_from_file_location("setup_directories", setup_dir_path)
    setup_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(setup_module)
    setup_module.setup_project_directories()
    print("✓ Directory setup completed")
else:
    print(f"✗ Could not find {setup_dir_path}")

# Remove app.py if it exists
if os.path.exists("app.py"):
    os.remove("app.py")
    print("✓ Removed redundant app.py")

# Ensure all necessary directories exist
directories = [
    "views",
    "utils",
    "data",
    "data/gangs",
    "data/territories",
    "data/battles",
    "data/equipment",
    "logs",
    "backups"
]

for directory in directories:
    os.makedirs(directory, exist_ok=True)
    print(f"✓ Created {directory} directory")

# Copy any files from pages/ to views/ if they exist
if os.path.exists("pages"):
    for filename in os.listdir("pages"):
        if filename.endswith(".py"):
            src_path = os.path.join("pages", filename)
            dest_path = os.path.join("views", filename)
            shutil.copy2(src_path, dest_path)
            print(f"✓ Copied {src_path} to {dest_path}")
    
    # Ask if we want to remove the pages directory
    print("\nSetup complete! The 'pages' directory can now be safely removed.")
    print("Run the application with 'streamlit run main.py'")

print("\nSetup complete!")
