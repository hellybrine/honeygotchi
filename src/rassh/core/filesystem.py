import pickle
import structlog
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

logger = structlog.get_logger()


@dataclass
class FileNode:
    name: str
    is_directory: bool = False
    content: str = ""
    permissions: str = "755"
    owner: str = "root"
    group: str = "root"
    size: int = 0
    children: Dict[str, 'FileNode'] = field(default_factory=dict)
    
    def __post_init__(self):
        if self.is_directory and not self.content:
            self.content = ""
        if not self.is_directory and self.size == 0:
            self.size = len(self.content.encode('utf-8'))


class VirtualFilesystem:
    """Virtual filesystem for the honeypot."""
    
    def __init__(self, filesystem_file: Path):
        self.filesystem_file = filesystem_file
        self.root = FileNode("/", is_directory=True)
        self._load_filesystem()
    
    def _load_filesystem(self):
        """Load filesystem from pickle file or create default."""
        if self.filesystem_file.exists():
            try:
                with open(self.filesystem_file, 'rb') as f:
                    self.root = pickle.load(f)
                logger.info("Loaded virtual filesystem", file=str(self.filesystem_file))
            except Exception as e:
                logger.error("Failed to load filesystem, creating default", error=str(e))
                self._create_default_filesystem()
        else:
            self._create_default_filesystem()
    
    def _create_default_filesystem(self):
        """Create a default Linux-like filesystem structure."""
        # Root directories
        directories = [
            "/bin", "/boot", "/dev", "/etc", "/home", "/lib", "/media",
            "/mnt", "/opt", "/proc", "/root", "/run", "/sbin", "/srv",
            "/sys", "/tmp", "/usr", "/var"
        ]
        
        for dir_path in directories:
            self._create_directory(dir_path)
        
        # Common subdirectories
        subdirs = [
            "/usr/bin", "/usr/lib", "/usr/local", "/usr/share",
            "/var/log", "/var/tmp", "/var/www", "/home/user",
            "/etc/ssh", "/etc/apache2"
        ]
        
        for dir_path in subdirs:
            self._create_directory(dir_path)
        
        # Common files
        files = {
            "/etc/passwd": "root:x:0:0:root:/root:/bin/bash\nuser:x:1000:1000:user:/home/user:/bin/bash\n",
            "/etc/shadow": "root:*:18000:0:99999:7:::\nuser:*:18000:0:99999:7:::\n",
            "/etc/hosts": "127.0.0.1 localhost\n127.0.1.1 honeypot\n",
            "/etc/hostname": "honeypot\n",
            "/proc/version": "Linux version 5.4.0-honeypot (gcc version 9.3.0) #1 SMP\n",
            "/proc/cpuinfo": "processor\t: 0\nvendor_id\t: GenuineIntel\nmodel name\t: Intel(R) Core(TM) i7-8700K\n",
            "/home/user/.bashrc": "# .bashrc\nexport PS1='\\u@\\h:\\w\\$ '\n",
            "/home/user/.bash_history": "ls\ncd /tmp\nwget http://example.com/script.sh\n"
        }
        
        for file_path, content in files.items():
            self._create_file(file_path, content)
        
        self._save_filesystem()
        logger.info("Created default virtual filesystem")
    
    def _create_directory(self, path: str):
        """Create a directory in the virtual filesystem."""
        parts = [p for p in path.split('/') if p]
        current = self.root
        
        for part in parts:
            if part not in current.children:
                current.children[part] = FileNode(part, is_directory=True)
            current = current.children[part]
    
    def _create_file(self, path: str, content: str = ""):
        """Create a file in the virtual filesystem."""
        parts = [p for p in path.split('/') if p]
        if not parts:
            return
        
        # Navigate to parent directory
        current = self.root
        for part in parts[:-1]:
            if part not in current.children:
                current.children[part] = FileNode(part, is_directory=True)
            current = current.children[part]
        
        # Create file
        filename = parts[-1]
        current.children[filename] = FileNode(
            filename, 
            is_directory=False, 
            content=content,
            size=len(content.encode('utf-8'))
        )
    
    def _save_filesystem(self):
        """Save filesystem to pickle file."""
        try:
            self.filesystem_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.filesystem_file, 'wb') as f:
                pickle.dump(self.root, f)
        except Exception as e:
            logger.error("Failed to save filesystem", error=str(e))
    
    def get_node(self, path: str) -> Optional[FileNode]:
        """Get a node from the filesystem."""
        if path == "/":
            return self.root
        
        parts = [p for p in path.split('/') if p]
        current = self.root
        
        for part in parts:
            if part not in current.children:
                return None
            current = current.children[part]
        
        return current
    
    def list_directory(self, path: str) -> List[str]:
        """List contents of a directory."""
        node = self.get_node(path)
        if not node or not node.is_directory:
            return []
        
        return list(node.children.keys())
    
    def read_file(self, path: str) -> Optional[str]:
        """Read content of a file."""
        node = self.get_node(path)
        if not node or node.is_directory:
            return None
        
        return node.content
    
    def file_exists(self, path: str) -> bool:
        """Check if file or directory exists."""
        return self.get_node(path) is not None
    
    def is_directory(self, path: str) -> bool:
        """Check if path is a directory."""
        node = self.get_node(path)
        return node is not None and node.is_directory
    
    def get_file_info(self, path: str) -> Optional[Dict[str, Any]]:
        """Get file information."""
        node = self.get_node(path)
        if not node:
            return None
        
        return {
            "name": node.name,
            "is_directory": node.is_directory,
            "size": node.size,
            "permissions": node.permissions,
            "owner": node.owner,
            "group": node.group
        }