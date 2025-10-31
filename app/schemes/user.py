from sqlalchemy import Integer, String, DateTime, ForeignKey, Column, create_engine
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, UTC
import uuid
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

Base = declarative_base()

user_course_association = Table(
    "user_course_association",
    Base.metadata,
    Column("user_id", PG_UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True),
    Column(
        "course_id", PG_UUID(as_uuid=True), ForeignKey("courses.id"), primary_key=True
    ),
)


class Role(Base):
    __tablename__ = "roles"
    id = Column(PG_UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    name = Column(String(50), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.now(UTC))

    # users = relationship("User", back_populates="role")
    def __repr__(self):
        return f"<Role('id={self.id}', 'name={self.name}')>"


class User(Base):
    __tablename__ = "users"
    id = Column(PG_UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False)
    # email = Column(String(100), unique=True, nullable=False)
    # hashed_
    password = Column(String, nullable=False)
    # otp_secret = Column(String(32), nullable=False)
    company_id = Column(
        PG_UUID(as_uuid=True), ForeignKey("companies.id"), nullable=True
    )
    supervisor_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    # supervisor = relationship("User", remote_side=[id], backref="students")
    # courses = relationship("Course", secondary=user_course_association, backref="students")
    course_id = Column(PG_UUID(as_uuid=True), ForeignKey("course.id"), nullable=True)
    role_id = Column(PG_UUID(as_uuid=True), ForeignKey("roles.id"), nullable=True)
    # role = relationship("Role", back_populates="users")
    created_at = Column(DateTime, default=datetime.now(UTC))

    def __repr__(self):
        return f"<User('username={self.username}', role_id='{self.role_id}', supervisor_id='{self.supervisor_id}', company_id='{self.company_id}', course_id='{self.course_id}', 'id={self.id}')>"


class Company(Base):
    __tablename__ = "companies"
    id = Column(PG_UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    name = Column(String(50), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.now(UTC))

    def __repr__(self):
        return f"<User('id={self.id}', 'name={self.name}')>"


class Course(Base):
    __tablename__ = "courses"
    id = Column(PG_UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(100), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.now(UTC))

    company_id = Column(
        PG_UUID(as_uuid=True), ForeignKey("companies.id"), nullable=True
    )

    role = relationship("Role", back_populates="users")

    def __repr__(self):
        return f"<User('id={self.id}', 'name={self.name}')>"
