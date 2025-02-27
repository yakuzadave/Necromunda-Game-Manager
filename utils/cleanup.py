import os
import re

def fix_path_references():
    """
    Scan all Python files in the views directory and fix path references
    from pages/ to views/
    """
    views_dir = "/workspaces/Necromunda-Game-Manager/views"
    
    if not os.path.exists(views_dir):
        print("Views directory not found")
        return
    
    # Count of files and references fixed
    files_processed = 0
    references_fixed = 0
    
    # Pattern to match page references
    pattern = r'st\.switch_page\(\s*"pages/([^"]+)"\s*\)'
    replacement = r'st.switch_page("views/\1")'
    
    # Iterate through all Python files in views directory
    for filename in os.listdir(views_dir):
        if filename.endswith(".py"):
            filepath = os.path.join(views_dir, filename)
            
            # Read file content
            with open(filepath, 'r') as f:
                content = f.read()
            
            # Replace path references
            new_content, count = re.subn(pattern, replacement, content)
            
            # If changes were made, write back to file
            if count > 0:
                with open(filepath, 'w') as f:
                    f.write(new_content)
                
                references_fixed += count
                print(f"Fixed {count} references in {filepath}")
            
            files_processed += 1
    
    print(f"Processed {files_processed} files and fixed {references_fixed} path references")

if __name__ == "__main__":
    fix_path_references()
    
    # Remove app.py if it exists
    if os.path.exists("/workspaces/Necromunda-Game-Manager/app.py"):
        os.remove("/workspaces/Necromunda-Game-Manager/app.py")
        print("Removed redundant app.py file")
