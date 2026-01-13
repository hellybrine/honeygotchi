# Honeygotchi Improvements

This document outlines the improvements made to transform Honeygotchi into a production-ready, single-executable application.

## 🎯 Key Improvements

### 1. **Configuration Management**
- **YAML Configuration Support**: Added comprehensive configuration file support (`config.yaml`)
- **Flexible Config Loading**: Automatically searches for config in multiple locations:
  - Current directory
  - `~/.honeygotchi/config.yaml`
  - `/etc/honeygotchi/config.yaml`
- **Command-line Override**: All config options can be overridden via command-line arguments
- **Deep Merging**: Config files merge intelligently with defaults

### 2. **State Persistence**
- **RL Agent State Saving**: The reinforcement learning agent now saves its learned behavior
- **Automatic Persistence**: State is saved periodically (configurable interval)
- **Backup System**: Automatic backup of state files for recovery
- **State Restoration**: Agent resumes learning from where it left off

### 3. **Health Check Endpoint**
- **HTTP Health Checks**: Simple HTTP server for health monitoring
- **Status Endpoint**: Detailed status information including uptime and statistics
- **Metrics Endpoint**: Quick access to key metrics
- **Lightweight**: Uses standard library only (no extra dependencies)

### 4. **Modular Architecture**
- **Separated Concerns**: Split code into logical modules:
  - `config_loader.py`: Configuration management
  - `state_manager.py`: State persistence
  - `health_check.py`: Health monitoring
- **Better Maintainability**: Easier to test and extend

### 5. **Single Executable Build**
- **PyInstaller Integration**: Complete build system for creating standalone executables
- **Cross-platform**: Build scripts for both Unix/Linux (`build.sh`) and Windows (`build.bat`)
- **Self-contained**: All dependencies bundled into single executable
- **Easy Deployment**: No Python installation required on target systems

### 6. **Enhanced Error Handling**
- **Graceful Degradation**: Falls back to defaults if config file missing
- **State Recovery**: Attempts to recover from corrupted state files
- **Better Logging**: More informative error messages

### 7. **Improved Logging**
- **Structured Configuration**: Logging settings in config file
- **JSON Format Support**: Optional JSON logging for better parsing
- **Log Rotation**: Configurable log rotation settings

## 📦 Building the Executable

### Prerequisites
```bash
pip install -r requirements.txt
```

### Build Process

#### Linux/macOS:
```bash
./build.sh
```

#### Windows:
```cmd
build.bat
```

### Manual Build:
```bash
pyinstaller honeygotchi.spec
```

The executable will be created in the `dist/` directory.

## 🚀 Usage

### As Executable:
```bash
./dist/honeygotchi --port 2222 --config config.yaml
```

### With Configuration File:
```bash
./dist/honeygotchi --config /path/to/config.yaml
```

### Command-line Options:
- `--config PATH`: Path to configuration file
- `--port PORT`: SSH port (overrides config)
- `--metrics-port PORT`: Prometheus metrics port
- `--log-dir PATH`: Log directory
- `--host-key PATH`: SSH host key file
- `--generate-key`: Force generate new SSH host key
- `--epsilon FLOAT`: RL exploration rate
- `--learning-rate FLOAT`: RL learning rate
- `--clear-state`: Clear saved RL state

## 📋 Configuration File Structure

See `config.yaml` for the complete configuration structure. Key sections:

- **ssh**: SSH server settings
- **reinforcement_learning**: RL agent parameters and state management
- **monitoring**: Metrics and health check configuration
- **logging**: Logging configuration
- **filesystem**: Fake filesystem settings
- **security**: Security-related settings

## 🔄 State Management

The RL agent automatically saves its state to `rl_state.json` (configurable). This includes:
- Action rewards learned over time
- Action counts (usage statistics)
- Epsilon value
- Total decision count

State is saved:
- Periodically (every N decisions, configurable)
- On graceful shutdown
- Can be manually cleared with `--clear-state`

## 🏥 Health Monitoring

If enabled in config, health check server runs on port 8080 (configurable):

- `GET /health`: Simple health check
- `GET /status`: Detailed status with statistics
- `GET /metrics`: Quick metrics overview

## 🎨 Architecture Improvements

### Before:
- Single monolithic file
- Hard-coded configuration
- No state persistence
- Manual dependency management

### After:
- Modular, maintainable codebase
- Flexible configuration system
- Persistent learning state
- Single executable deployment

## 🔒 Security Enhancements

- Configurable session timeouts
- Command timeout limits
- Failed attempt tracking
- Better isolation of fake filesystem

## 📊 Monitoring Improvements

- Health check endpoints
- Better Prometheus integration
- Structured logging for analysis
- State persistence tracking

## 🧪 Testing Recommendations

1. **Unit Tests**: Test individual modules (config_loader, state_manager)
2. **Integration Tests**: Test SSH server with mock connections
3. **State Persistence Tests**: Verify state save/load functionality
4. **Configuration Tests**: Test config loading and merging

## 🚧 Future Enhancements

Potential improvements for future versions:

1. **Web Dashboard**: Built-in web UI for monitoring
2. **Database Backend**: Store sessions and commands in database
3. **Advanced RL**: More sophisticated RL algorithms
4. **Multi-protocol**: Support for other protocols (FTP, Telnet, etc.)
5. **Distributed Mode**: Multiple honeypot instances sharing state
6. **Threat Intelligence**: Integration with threat intel feeds
7. **Alerting**: Integration with alerting systems (PagerDuty, Slack, etc.)

## 📝 Migration Guide

### From Old Version:

1. **Configuration**: Create `config.yaml` based on your previous command-line arguments
2. **State**: If you had any RL state, it will be automatically loaded from `rl_state.json`
3. **SSH Keys**: Existing SSH host keys will continue to work
4. **Logs**: Logs will be in the configured directory (default: `logs/`)

### Breaking Changes:

- Command-line argument format remains the same, but config file is now preferred
- State file format changed (old state files will be ignored)
- Health check server is new (can be disabled in config)

## 🐛 Troubleshooting

### Executable won't start:
- Check that all dependencies are installed before building
- Verify config file syntax (YAML)
- Check logs in the configured log directory

### State not persisting:
- Check file permissions on state file location
- Verify `save_interval` in config is reasonable
- Check disk space

### Health check not working:
- Verify port 8080 (or configured port) is available
- Check firewall settings
- Disable health check in config if not needed

## 📚 Additional Resources

- See `README.md` for general project information
- See `config.yaml` for configuration examples
- Check logs for detailed runtime information
