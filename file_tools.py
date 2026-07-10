import os
import glob
import shutil
import subprocess

RUBIKS_DIR = os.path.dirname(os.path.abspath(__file__))

# All common user directories
USER_DIRS = [
    os.path.expanduser("~/Downloads"),
    os.path.expanduser("~/Desktop"),
    os.path.expanduser("~/Documents"),
    os.path.expanduser("~/Pictures"),
    os.path.expanduser("~/Videos"),
    os.path.expanduser("~/Music"),
    os.path.expanduser("~/AppData"),
    "C:\\",
    RUBIKS_DIR,
]

BINARY_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".ico", ".svg",
    ".mp4", ".avi", ".mkv", ".mov", ".wmv", ".mp3", ".wav", ".flac",
    ".pdf", ".docx", ".xlsx", ".pptx", ".zip", ".rar", ".7z", ".exe",
    ".msi", ".dll", ".iso",
}

def _resolve_path(file_path: str) -> str:
    """Resolves a filename or relative path to an absolute path by searching common directories."""
    if os.path.isabs(file_path) and os.path.exists(file_path):
        return file_path
    
    # Direct match in common dirs
    for folder in USER_DIRS:
        if not os.path.isdir(folder):
            continue
        candidate = os.path.join(folder, file_path)
        if os.path.exists(candidate):
            return candidate
    
    # Fuzzy search: find files whose name contains the search term
    search_term = os.path.basename(file_path).lower()
    for folder in USER_DIRS[:5]:  # Only search user folders, not C:\ root
        if not os.path.isdir(folder):
            continue
        try:
            for item in os.listdir(folder):
                if search_term in item.lower():
                    return os.path.join(folder, item)
        except PermissionError:
            continue
    
    return file_path  # Return as-is, let caller handle the error


def list_files(directory: str, file_type: str = "") -> str:
    """
    Lists files in a directory. If file_type is provided (e.g. '.pdf', '.jpg', 'images'), 
    filters by that extension. Returns file names, sizes, and modification dates.
    Use this when the user asks to find files, list documents, show downloads, etc.
    Accepts shortcuts like 'downloads', 'desktop', 'documents', 'pictures', 'system', or any absolute path.
    """
    try:
        if not directory:
            directory = os.path.expanduser("~/Downloads")
        
        # Handle shortcuts
        shortcut_map = {
            "downloads": "~/Downloads", "download": "~/Downloads",
            "desktop": "~/Desktop",
            "documents": "~/Documents", "docs": "~/Documents",
            "pictures": "~/Pictures", "photos": "~/Pictures", "images": "~/Pictures",
            "videos": "~/Videos", "video": "~/Videos",
            "music": "~/Music", "audio": "~/Music",
            "system": "C:\\Windows\\System32",
            "appdata": "~/AppData",
            "programs": "C:\\Program Files",
            "rubiks": RUBIKS_DIR,
            "home": "~",
            "c": "C:\\", "c:": "C:\\", "c:\\": "C:\\",
        }
        
        resolved = shortcut_map.get(directory.lower().strip())
        if resolved:
            directory = os.path.expanduser(resolved)
            
        if not os.path.isdir(directory):
            return f"Directory not found: {directory}"
        
        # Map common words to extensions
        type_map = {
            "images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"],
            "videos": [".mp4", ".avi", ".mkv", ".mov", ".wmv"],
            "documents": [".pdf", ".docx", ".doc", ".txt", ".xlsx", ".pptx"],
            "code": [".py", ".js", ".html", ".css", ".java", ".cpp"],
            "audio": [".mp3", ".wav", ".flac", ".aac", ".ogg"],
        }
        
        extensions = None
        if file_type:
            ft = file_type.lower().strip(".")
            if ft in type_map:
                extensions = type_map[ft]
            else:
                extensions = [f".{ft}" if not ft.startswith(".") else ft]
        
        entries = []
        try:
            for item in os.listdir(directory):
                full_path = os.path.join(directory, item)
                if os.path.isfile(full_path):
                    ext = os.path.splitext(item)[1].lower()
                    if extensions and ext not in extensions:
                        continue
                    size = os.path.getsize(full_path)
                    if size > 1_000_000:
                        size_str = f"{size / 1_000_000:.1f} MB"
                    elif size > 1_000:
                        size_str = f"{size / 1_000:.1f} KB"
                    else:
                        size_str = f"{size} B"
                    entries.append(f"  {item} ({size_str})")
                elif os.path.isdir(full_path):
                    entries.append(f"  [DIR] {item}/")
        except PermissionError:
            return f"Access denied to {directory}. Try running as administrator."
        
        if not entries:
            return f"No {'matching ' if extensions else ''}files found in {directory}."
        
        result = f"Files in {directory}:\n" + "\n".join(entries[:30])
        if len(entries) > 30:
            result += f"\n  ... and {len(entries) - 30} more."
        return result
    except Exception as e:
        return f"File listing failed: {str(e)}"


def read_file(file_path: str) -> str:
    """
    Reads and returns the content of a file. For text files, returns the text.
    For binary files (images, PDFs, etc.), opens them in the default app.
    Use this when the user asks to read, view, open, or show a file.
    """
    try:
        file_path = _resolve_path(file_path)
        
        if not os.path.isfile(file_path):
            return f"File not found: {file_path}. Try using list_files or find_recent_files to locate it first."
        
        ext = os.path.splitext(file_path)[1].lower()
        
        # Binary files: just open them in the default app
        if ext in BINARY_EXTENSIONS:
            os.startfile(file_path)
            size = os.path.getsize(file_path)
            size_str = f"{size / 1_000_000:.1f} MB" if size > 1_000_000 else f"{size / 1_000:.1f} KB"
            return f"Opened {os.path.basename(file_path)} ({size_str}) in default application."
        
        # Text files: read and return content
        size = os.path.getsize(file_path)
        if size > 500_000:
            os.startfile(file_path)
            return f"File is large ({size / 1_000_000:.1f} MB). Opened in default application instead."
        
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        
        if len(content) > 5000:
            content = content[:5000] + "\n\n[... truncated, file continues ...]"
        
        return f"Contents of {os.path.basename(file_path)} ({file_path}):\n{content}"
    except Exception as e:
        return f"Failed to read file: {str(e)}"


def write_file(file_path: str, content: str) -> str:
    """
    Writes content to a file. Creates the file and directories if they don't exist.
    Use this when the user asks to create, write, or save a file.
    """
    try:
        if not os.path.isabs(file_path):
            file_path = os.path.join(os.path.expanduser("~/Desktop"), file_path)
        
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        return f"File written: {file_path}"
    except Exception as e:
        return f"Failed to write file: {str(e)}"


def find_recent_files(file_type: str = "", count: int = 5) -> str:
    """
    Finds the most recently modified files across Downloads, Desktop, Documents, and Pictures.
    Use this when the user says 'recent files', 'latest download', 'what did I just download', 'show me that file', etc.
    """
    try:
        dirs_to_scan = [
            os.path.expanduser("~/Downloads"),
            os.path.expanduser("~/Desktop"),
            os.path.expanduser("~/Documents"),
            os.path.expanduser("~/Pictures"),
        ]
        
        type_map = {
            "images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"],
            "videos": [".mp4", ".avi", ".mkv", ".mov", ".wmv"],
            "documents": [".pdf", ".docx", ".doc", ".txt", ".xlsx", ".pptx"],
        }
        
        extensions = None
        if file_type:
            ft = file_type.lower().strip(".")
            if ft in type_map:
                extensions = type_map[ft]
            else:
                extensions = [f".{ft}" if not ft.startswith(".") else ft]
        
        all_files = []
        for d in dirs_to_scan:
            if not os.path.isdir(d):
                continue
            try:
                for item in os.listdir(d):
                    full = os.path.join(d, item)
                    if os.path.isfile(full):
                        ext = os.path.splitext(item)[1].lower()
                        if extensions and ext not in extensions:
                            continue
                        all_files.append((full, os.path.getmtime(full)))
            except PermissionError:
                continue
        
        all_files.sort(key=lambda x: x[1], reverse=True)
        
        if not all_files:
            return "No recent files found."
        
        import datetime
        count = int(count)
        result = "Recent files:\n"
        for path, mtime in all_files[:count]:
            dt = datetime.datetime.fromtimestamp(mtime)
            size = os.path.getsize(path)
            size_str = f"{size / 1_000_000:.1f} MB" if size > 1_000_000 else f"{size / 1_000:.1f} KB"
            result += f"  {os.path.basename(path)} ({size_str}) - {dt.strftime('%b %d, %I:%M %p')} - {path}\n"
        
        return result.strip()
    except Exception as e:
        return f"Failed to find recent files: {str(e)}"


def open_file(file_path: str) -> str:
    """
    Opens any file in its default Windows application.
    Use this when the user says 'open that file', 'show me that', 'open it', etc.
    """
    try:
        # --- PRONOUN RESOLUTION FAILSAFE ---
        if file_path.lower().strip() in ["it", "that", "this", "the file", "the image", "the photo", "the document"]:
            try:
                recent_data = find_recent_files(count=1)
                file_path = recent_data.strip().split(" - ")[-1]
            except Exception:
                pass
                
        file_path = _resolve_path(file_path)
        
        if not os.path.exists(file_path):
            return f"File not found: {file_path}"
        
        os.startfile(file_path)
        return f"Opened: {os.path.basename(file_path)}"
    except Exception as e:
        return f"Failed to open file: {str(e)}"


def search_files(query: str, directory: str = "") -> str:
    """
    Searches for files matching a query string across all user directories.
    Use this when the user says 'find file', 'where is', 'search for file', etc.
    """
    try:
        search_dirs = [os.path.expanduser(d) for d in ["~/Downloads", "~/Desktop", "~/Documents", "~/Pictures"]]
        if directory:
            resolved = os.path.expanduser(directory) if directory.startswith("~") else directory
            if os.path.isdir(resolved):
                search_dirs = [resolved]
        
        query_lower = query.lower()
        matches = []
        
        for d in search_dirs:
            if not os.path.isdir(d):
                continue
            try:
                for root, dirs, files in os.walk(d):
                    # Limit depth to 3 levels
                    depth = root.replace(d, '').count(os.sep)
                    if depth > 3:
                        dirs.clear()
                        continue
                    for f in files:
                        if query_lower in f.lower():
                            full = os.path.join(root, f)
                            matches.append(full)
                            if len(matches) >= 15:
                                break
                    if len(matches) >= 15:
                        break
            except PermissionError:
                continue
            if len(matches) >= 15:
                break
        
        if not matches:
            return f"No files matching '{query}' found."
        
        result = f"Found {len(matches)} file(s) matching '{query}':\n"
        for m in matches:
            result += f"  {os.path.basename(m)} - {m}\n"
        return result.strip()
    except Exception as e:
        return f"File search failed: {str(e)}"
