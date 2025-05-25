"""Main application entry point with proper async handling."""
import asyncio
import signal
import structlog
from pathlib import Path
import sys

from rassh.core.config import get_config
from rassh.core.honeypot import HoneypotServer

logger = structlog.get_logger()


class HoneypotApplication:
    """Main honeypot application."""
    
    def __init__(self):
        self.config = get_config()
        self.server = None
        self.running = False
    
    async def start(self):
        """Start the honeypot application."""
        # Setup logging
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
        
        logger.info("Starting RASSH Honeypot", version="2.0.0")
        
        # Create necessary directories
        Path(self.config.honeypot.log_path).mkdir(parents=True, exist_ok=True)
        Path(self.config.honeypot.data_path).mkdir(parents=True, exist_ok=True)
        
        # Initialize and start server
        self.server = HoneypotServer(self.config)
        await self.server.start()
        
        self.running = True
        logger.info("Honeypot started successfully")
    
    async def stop(self):
        """Stop the honeypot application."""
        if self.server:
            await self.server.stop()
        self.running = False
        logger.info("Honeypot stopped")
    
    async def run(self):
        """Run the honeypot until stopped."""
        await self.start()
        
        # Setup signal handlers
        def signal_handler():
            logger.info("Received shutdown signal")
            asyncio.create_task(self.stop())
        
        if sys.platform != 'win32':
            loop = asyncio.get_running_loop()
            loop.add_signal_handler(signal.SIGTERM, signal_handler)
            loop.add_signal_handler(signal.SIGINT, signal_handler)
        
        # Keep running until stopped
        try:
            while self.running:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received")
        finally:
            await self.stop()


async def main():
    """Main entry point."""
    app = HoneypotApplication()
    await app.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutdown complete")