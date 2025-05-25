import re
import asyncio
import structlog
from typing import Dict, List, Optional, Callable, Any
from abc import ABC, abstractmethod

from ..core.database import DatabaseManager
from ..core.filesystem import VirtualFilesystem

logger = structlog.get_logger()


class BaseCommand(ABC):
    """Base class for command implementations."""
    
    def __init__(self, name: str, filesystem: VirtualFilesystem, db_manager: DatabaseManager):
        self.name = name
        self.filesystem = filesystem
        self.db_manager = db_manager
    
    @abstractmethod
    async def execute(self, args: List[str], current_dir: str) -> str:
        """Execute the command."""
        pass
    
    def _normalize_path(self, path: str, current_dir: str) -> str:
        """Normalize a path relative to current directory."""
        if path.startswith('/'):
            return path
        else:
            if current_dir.endswith('/'):
                return current_dir + path
            else:
                return current_dir + '/' + path


class LSCommand(BaseCommand):
    """List directory contents."""
    
    async def execute(self, args: List[str], current_dir: str) -> str:
        target_dir = current_dir
        show_all = False
        long_format = False
        
        # Parse arguments
        for arg in args:
            if arg.startswith('-'):
                if 'a' in arg:
                    show_all = True
                if 'l' in arg:
                    long_format = True
            else:
                target_dir = self._normalize_path(arg, current_dir)
        
        if not self.filesystem.is_directory(target_dir):
            return f"ls: cannot access '{target_dir}': No such file or directory\n"
        
        contents = self.filesystem.list_directory(target_dir)
        
        if not show_all:
            contents = [item for item in contents if not item.startswith('.')]
        
        if long_format:
            result = []
            for item in sorted(contents):
                item_path = f"{target_dir.rstrip('/')}/{item}"
                info = self.filesystem.get_file_info(item_path)
                if info:
                    file_type = 'd' if info['is_directory'] else '-'
                    result.append(
                        f"{file_type}{info['permissions']} 1 {info['owner']} {info['group']} "
                        f"{info['size']:>8} Jan  1 12:00 {item}"
                    )
            return '\n'.join(result) + '\n'
        else:
            return '  '.join(sorted(contents)) + '\n'


class CDCommand(BaseCommand):
    """Change directory."""
    
    async def execute(self, args: List[str], current_dir: str) -> str:
        if not args:
            return "/home/user"  # Return new directory
        
        target_dir = self._normalize_path(args[0], current_dir)
        
        if not self.filesystem.is_directory(target_dir):
            return f"cd: {target_dir}: No such file or directory\n"
        
        return target_dir  # Return new directory


class CatCommand(BaseCommand):
    """Display file contents."""
    
    async def execute(self, args: List[str], current_dir: str) -> str:
        if not args:
            return "cat: missing file operand\n"
        
        results = []
        for arg in args:
            file_path = self._normalize_path(arg, current_dir)
            content = self.filesystem.read_file(file_path)
            
            if content is None:
                if self.filesystem.is_directory(file_path):
                    results.append(f"cat: {arg}: Is a directory\n")
                else:
                    results.append(f"cat: {arg}: No such file or directory\n")
            else:
                results.append(content)
        
        return ''.join(results)


class PWDCommand(BaseCommand):
    """Print working directory."""
    
    async def execute(self, args: List[str], current_dir: str) -> str:
        return current_dir + '\n'


class WhoamiCommand(BaseCommand):
    """Print current user."""
    
    async def execute(self, args: List[str], current_dir: str) -> str:
        return "user\n"


class UnameCommand(BaseCommand):
    """System information."""
    
    async def execute(self, args: List[str], current_dir: str) -> str:
        if '-a' in args:
            return "Linux honeypot 5.4.0-honeypot #1 SMP x86_64 GNU/Linux\n"
        else:
            return "Linux\n"


class WgetCommand(BaseCommand):
    """Fake wget command."""
    
    async def execute(self, args: List[str], current_dir: str) -> str:
        if not args:
            return "wget: missing URL\n"
        
        url = args[-1]  # Last argument is usually the URL
        filename = url.split('/')[-1] or 'index.html'
        
        # Simulate download
        await asyncio.sleep(1)
        
        return f"--{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}--  {url}\n" \
               f"Resolving example.com... 93.184.216.34\n" \
               f"Connecting to example.com|93.184.216.34|:80... connected.\n" \
               f"HTTP request sent, awaiting response... 200 OK\n" \
               f"Length: 1024 (1.0K) [text/html]\n" \
               f"Saving to: '{filename}'\n\n" \
               f"{filename}              100%[===================>]   1.00K  --.-KB/s    in 0s\n\n" \
               f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (5.00 MB/s) - '{filename}' saved [1024/1024]\n"


class CurlCommand(BaseCommand):
    """Fake curl command."""
    
    async def execute(self, args: List[str], current_dir: str) -> str:
        if not args:
            return "curl: try 'curl --help' for more information\n"
        
        url = args[-1]
        
        # Simulate HTTP response
        await asyncio.sleep(0.5)
        
        return "<!DOCTYPE html>\n<html>\n<head>\n<title>Example</title>\n</head>\n" \
               "<body>\n<h1>Example Domain</h1>\n<p>This domain is for use in " \
               "illustrative examples.</p>\n</body>\n</html>\n"


class CommandProcessor:
    """Main command processor."""
    
    def __init__(self, db_manager: DatabaseManager, filesystem: VirtualFilesystem):
        self.db_manager = db_manager
        self.filesystem = filesystem
        self.current_directory = "/"
        
        # Register commands
        self.commands: Dict[str, BaseCommand] = {
            'ls': LSCommand('ls', filesystem, db_manager),
            'cd': CDCommand('cd', filesystem, db_manager),
            'cat': CatCommand('cat', filesystem, db_manager),
            'pwd': PWDCommand('pwd', filesystem, db_manager),
            'whoami': WhoamiCommand('whoami', filesystem, db_manager),
            'uname': UnameCommand('uname', filesystem, db_manager),
            'wget': WgetCommand('wget', filesystem, db_manager),
            'curl': CurlCommand('curl', filesystem, db_manager),
        }
    
    async def process_command(self, command_line: str, current_dir: str) -> str:
        """Process a command line."""
        if not command_line.strip():
            return ""
        
        # Parse command line
        parts = command_line.strip().split()
        command_name = parts[0]
        args = parts[1:] if len(parts) > 1 else []
        
        # Handle built-in commands
        if command_name in self.commands:
            try:
                result = await self.commands[command_name].execute(args, current_dir)
                
                # Special handling for cd command
                if command_name == 'cd' and not result.endswith('\n'):
                    self.current_directory = result
                    return ""  # cd doesn't output anything on success
                
                return result
            except Exception as e:
                logger.error("Command execution failed", command=command_name, error=str(e))
                return f"{command_name}: command failed\n"
        
        # Handle unknown commands
        return f"{command_name}: command not found\n"