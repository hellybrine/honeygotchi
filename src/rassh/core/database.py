"""Modern database layer using SQLAlchemy."""
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql import func
from typing import Optional, List, Dict, Any
import structlog

from .config import DatabaseConfig

logger = structlog.get_logger()

Base = declarative_base()


class Session(Base):
    """Session table."""
    __tablename__ = 'sessions'
    
    id = Column(String(36), primary_key=True)
    start_time = Column(DateTime, default=func.now())
    end_time = Column(DateTime)
    client_ip = Column(String(45))
    client_version = Column(String(255))


class Command(Base):
    """Command table."""
    __tablename__ = 'commands'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(36))
    command = Column(Text)
    timestamp = Column(DateTime, default=func.now())
    action_taken = Column(Integer)
    reward = Column(Float)


class Case(Base):
    """RL training case table."""
    __tablename__ = 'cases'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    initial_cmd = Column(Text)
    action = Column(Integer)
    next_cmd = Column(Text)
    cmd_profile = Column(String(100))
    rl_params = Column(Text)
    timestamp = Column(DateTime, default=func.now())


class DatabaseManager:
    """Modern database manager."""
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.engine = None
        self.SessionLocal = None
        self._setup_database()
    
    def _setup_database(self):
        """Setup database connection."""
        connection_string = (
            f"mysql+pymysql://{self.config.username}:{self.config.password}"
            f"@{self.config.host}:{self.config.port}/{self.config.database}"
        )
        
        self.engine = create_engine(
            connection_string,
            pool_pre_ping=True,
            pool_recycle=3600,
            echo=False
        )
        
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
        
        # Create tables
        Base.metadata.create_all(bind=self.engine)
        logger.info("Database setup completed")
    
    def get_session(self) -> Session:
        """Get database session."""
        return self.SessionLocal()
    
    def save_case(self, case_data: Dict[str, Any]) -> bool:
        """Save RL training case."""
        try:
            with self.get_session() as session:
                case = Case(**case_data)
                session.add(case)
                session.commit()
                return True
        except Exception as e:
            logger.error("Failed to save case", error=str(e))
            return False
    
    def get_fake_command_output(self, command: str) -> str:
        """Get fake output for command."""
        # This would typically query a fake_commands table
        return f"Fake output for: {command}\n"
    
    def get_insult_message(self, location: str = "DEFAULT") -> str:
        """Get location-specific insult message."""
        # This would typically query a messages table
        return f"Access denied from {location}!\n"