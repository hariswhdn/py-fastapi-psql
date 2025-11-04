from sqlalchemy import (
    String,
    DateTime,
    ForeignKey,
    # Column,
    create_engine,
    # Table,
    text,
    Boolean,
    PrimaryKeyConstraint,
)
from sqlalchemy.orm import (
    relationship,
    DeclarativeBase,
    Mapped,
    mapped_column,
    sessionmaker,
    Session,
)
from datetime import datetime, UTC
from uuid import UUID, uuid4
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from typing import override
from pydantic import BaseModel, ConfigDict
from fastapi import FastAPI, Depends, HTTPException

DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    DATABASE_URL, echo=True, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


# user_course_association = Table(
#     "user_course_association",
#     Base.metadata,
#     Column("user_id", PG_UUID(as_uuid=True), ForeignKey("user.id"), primary_key=True),
#     Column(
#         "course_id", PG_UUID(as_uuid=True), ForeignKey("courses.id"), primary_key=True
#     ),
# )


class User(Base):
    __tablename__: str = "user"
    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, index=True, default=uuid4
    )
    username: Mapped[str] = mapped_column(String(50), unique=True)
    password: Mapped[str] = mapped_column(String(50))
    is_disabled: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now(UTC),
        onupdate=datetime.now(UTC),
        server_default=text("CURRENT_TIMESTAMP"),
    )

    # # relation with role
    # role_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("role.id"))
    # roles: Mapped["Role"] = relationship("Role", back_populates="users")
    # # relation with unit
    # unit_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("unit.id"))
    # units: Mapped["Unit"] = relationship("Unit", back_populates="users")
    # # relation with company
    # company_id: Mapped[UUID | None] = mapped_column(
    #     PG_UUID(as_uuid=True), ForeignKey("company.id")
    # )
    # company: Mapped["Company"] = relationship("Company", back_populates="users")
    # # relation with course
    # courses: Mapped[list["Course"]] = relationship(
    #     "Course", secondary=user_course_association, back_populates="students"
    # )
    # supervised_courses: Mapped[list["Course"]] = relationship(
    #     "Course", secondary=user_course_association, back_populates="supervisors"
    # )
    # created_courses: Mapped[list["Course"]] = relationship(
    #     "Course", back_populates="creator"
    # )
    @override
    def __repr__(self):
        return f"<User('username={self.username}', 'id={self.id}')>"


class Role(Base):
    __tablename__: str = "role"
    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, index=True, default=uuid4
    )
    name: Mapped[str] = mapped_column(String(50), unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now(UTC),
        onupdate=datetime.now(UTC),
        server_default=text("CURRENT_TIMESTAMP"),
    )
    # relation with role parent
    parent_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("role.id")
    )
    parent: Mapped["Role"] = relationship(
        "Role", remote_side=[id], back_populates="children", uselist=False
    )
    children: Mapped[list["Role"]] = relationship(
        "Role", back_populates="parent", lazy="dynamic"
    )

    @override
    def __repr__(self):
        return f"<Role('name={self.name}', 'id={self.id}')>"


class Unit(Base):
    __tablename__: str = "unit"
    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, index=True, default=uuid4
    )
    name: Mapped[str] = mapped_column(String(50))
    is_disabled: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now(UTC),
        onupdate=datetime.now(UTC),
        server_default=text("CURRENT_TIMESTAMP"),
    )
    # # relation with user
    # supervisors: Mapped[list["User"]] = relationship(
    #     "User", back_populates="supervised_units"
    # )
    # students: Mapped[list["User"]] = relationship("User", back_populates="units")
    # # relation with company
    # company_id: Mapped[UUID] = mapped_column(
    #     PG_UUID(as_uuid=True), ForeignKey("company.id")
    # )
    # company: Mapped["Company"] = relationship("Company", back_populates="units")

    @override
    def __repr__(self):
        return f"<Course('name={self.name}', 'id={self.id}')>"


class UserHasRole(Base):
    __tablename__: str = "user_has_role"
    __table_args__ = (PrimaryKeyConstraint("user_id", "role_id"),)
    # relation with user
    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("user.id"),
        # , ondelete="CASCADE"
    )
    user: Mapped["User"] = relationship("User", backref="roles")
    # relation with role
    role_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("role.id"),
        # , ondelete="CASCADE"
    )
    role: Mapped["Role"] = relationship("Role", backref="users")

    @override
    def __repr__(self):
        return f"<UserHasRole('user_id={self.user_id}', role_id='{self.role_id}'>"


class UserHasUnit(Base):
    __tablename__: str = "user_has_unit"
    __table_args__ = (PrimaryKeyConstraint("user_id", "unit_id"),)
    # relation with user
    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("user.id"),
        # , ondelete="CASCADE"
    )
    user: Mapped["User"] = relationship("User", backref="units")
    # relation with unit
    unit_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("unit.id"),
        # , ondelete="CASCADE"
    )
    unit: Mapped["Unit"] = relationship("Unit", backref="users")

    @override
    def __repr__(self):
        return f"<UserHasUnit('user_id={self.user_id}', unit_id='{self.unit_id}'>"


# class Company(Base):
#     __tablename__: str = "company"
#     id: Mapped[UUID] = mapped_column(
#         PG_UUID(as_uuid=True), primary_key=True, index=True, default=uuid4
#     )
#     name: Mapped[str] = mapped_column(String(50), unique=True)
#     is_disabled: Mapped[bool] = mapped_column(Boolean, default=False)
#     created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(UTC))
#     updated_at: Mapped[datetime] = mapped_column(
#         DateTime,
#         default=datetime.now(UTC),
#         onupdate=datetime.now(UTC),
#         server_default=text("CURRENT_TIMESTAMP"),
#     )
#     # relation with user
#     users: Mapped[list["User"]] = relationship("User", back_populates="company")
#     courses: Mapped[list["Course"]] = relationship("Course", back_populates="company")

#     @override
#     def __repr__(self):
#         return f"<Company('name={self.name}', 'id={self.id}')>"

# class Course(Base):
#     __tablename__: str = "courses"
#     id: Mapped[UUID] = mapped_column(
#         PG_UUID(as_uuid=True), primary_key=True, index=True, default=uuid4
#     )
#     name: Mapped[str] = mapped_column(String(50))
#     description: Mapped[str] = mapped_column(String(100))
#     is_disabled: Mapped[bool] = mapped_column(Boolean, default=False)
#     created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(UTC))
#     updated_at: Mapped[datetime] = mapped_column(
#         DateTime,
#         default=datetime.now(UTC),
#         onupdate=datetime.now(UTC),
#         server_default=text("CURRENT_TIMESTAMP"),
#     )
#     # relation with user
#     creator_id: Mapped[UUID] = mapped_column(
#         PG_UUID(as_uuid=True), ForeignKey("user.id")
#     )
#     creator: Mapped["User"] = relationship("User", back_populates="created_courses")
#     supervisors: Mapped[list["User"]] = relationship(
#         "User", back_populates="supervised_courses"
#     )
#     students: Mapped[list["User"]] = relationship("User", back_populates="courses")
#     # relation with company
#     company_id: Mapped[UUID] = mapped_column(
#         PG_UUID(as_uuid=True), ForeignKey("company.id")
#     )
#     company: Mapped["Company"] = relationship("Company", back_populates="courses")

#     @override
#     def __repr__(self):
#         return f"<Course('name={self.name}', 'id={self.id}')>"

if __name__ == "__main__":
    engine = create_engine("sqlite:///example.db")
    print("SQLAlchemy models defined successfully. Base.metadata contains the schema.")


# -------------------------------------------------------------------
# Pydantic Schemas
# -------------------------------------------------------------------
class UserBase(BaseModel):
    username: str
    is_disabled: bool = False


class UserCreate(UserBase):
    password: str
    model_config = ConfigDict(from_attributes=True)


class UserRead(UserBase):
    id: str
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


# -------------------------------------------------------------------
# FastAPI setup
# -------------------------------------------------------------------
app = FastAPI(title="SQLite FastAPI Example")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"message": "SQLite + FastAPI demo running!"}


@app.post("/users/", response_model=UserRead)
def create_user(user: UserCreate, db: Session = Depends(get_db)):  # type: ignore[reportCallInDefaultInitializer]
    existing = db.query(User).filter(User.username == user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists!")
    new_user = User(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.get("/users/{user_id}", response_model=UserRead)
def get_user(user_id: str, db: Session = Depends(get_db)):  # type: ignore[reportCallInDefaultInitializer]
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found!")
    return user
