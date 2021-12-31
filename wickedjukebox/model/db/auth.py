# type: ignore
# pylint: disable=no-member, attribute-defined-outside-init
# pylint: disable=too-few-public-methods, invalid-name
#
# SQLAlchemy mapped classes have their members injected by the Base metaclass.
# Pylint does not see those and causes false "no-member" messages. Which is why
# they are disabled in this module. The same goes for variable initialisation.
# Additionally, mapped classes don't necessarily have public methods.
# "invalid-name" is disabled because these variables don't really have the role
# of constants. Renaming them now would just produce even more unnecessary
# git-churn.


"""
This module contains DB definitions for user authentication & authorisation
"""
from base64 import b64encode
from datetime import datetime
from os import urandom  # TODO Use more secure function

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Table,
    Text,
    text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKeyConstraint

from .sameta import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        Index("group_id", "group_id", unique=False),
        Index("username", "username", unique=True),
        Index("cookie", "cookie", unique=True),
        Index("django_user_id_idx", "django_user_id", unique=True),
        ForeignKeyConstraint(
            ["group_id"],
            ["groups.id"],
            name="users_ibfk_1",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
    )
    id = Column(Integer, primary_key=True)
    username = Column(String(32), nullable=False)
    cookie = Column(String(32), nullable=False)
    password = Column(String(32), nullable=False)
    fullname = Column(String(64), nullable=False)
    email = Column(String(128), nullable=False)
    credits = Column(Integer, nullable=False)
    group_id = Column(Integer, nullable=False)
    downloads = Column(Integer, nullable=False, server_default=text("0"))
    votes = Column(Integer, nullable=False, server_default=text("0"))
    skips = Column(Integer, nullable=False, server_default=text("0"))
    selects = Column(Integer, nullable=False, server_default=text("0"))
    added = Column(DateTime, nullable=False, default=datetime.now)
    proof_of_life = Column(DateTime, nullable=False)
    proof_of_listening = Column(DateTime)
    IP = Column(String(32), nullable=False)
    picture = Column(String(255), nullable=False)
    lifetime = Column(BigInteger, nullable=False)
    channel_id = Column(Integer, nullable=False, server_default=text("1"))
    pinnedIp = Column(String(32))
    django_user_id = Column(Integer)

    group = relationship("Group", backref="users")

    def __init__(self, username, group, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.username = username
        self.cookie = ""
        self.password = b64encode(urandom(20)).decode("ascii")
        self.fullname = "default user"
        self.email = ""
        self.proof_of_life = datetime.now()
        self.proof_of_listening = None
        self.IP = ""
        self.credits = 0
        self.group = group
        self.picture = ""
        self.lifetime = 0

    def __repr__(self):
        return "<User %d %r>" % (self.id, self.username)


class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True)
    title = Column(String(32), nullable=False)
    admin = Column(Integer, nullable=False, server_default=text("0"))
    nocredits = Column(Integer, nullable=False, server_default=text("0"))
    queue_skip = Column(Integer, nullable=False, server_default=text("0"))
    queue_remove = Column(Integer, nullable=False, server_default=text("0"))
    queue_add = Column(Integer, nullable=False, server_default=text("0"))

    def __init__(self, title, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title = title

    def __repr__(self):
        return "<Group %d %r>" % (self.id, self.title)


class AuthGroup(Base):
    __tablename__ = "auth_group"

    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False, unique=True)


class AuthUser(Base):
    __tablename__ = "auth_user"

    id = Column(Integer, primary_key=True)
    password = Column(String(128), nullable=False)
    last_login = Column(DateTime(timezone=True))
    is_superuser = Column(Boolean, nullable=False)
    username = Column(String(150), nullable=False, unique=True)
    first_name = Column(String(150), nullable=False)
    last_name = Column(String(150), nullable=False)
    email = Column(String(254), nullable=False)
    is_staff = Column(Boolean, nullable=False)
    is_active = Column(Boolean, nullable=False)
    date_joined = Column(DateTime(timezone=True), nullable=False)


class AuthPermission(Base):
    __tablename__ = "auth_permission"
    __table_args__ = (
        Index(
            "auth_permission_content_type_id_codename_01ab375a_uniq",
            "content_type_id",
            "codename",
            unique=True,
        ),
    )

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    content_type_id = Column(
        ForeignKey("django_content_type.id"), nullable=False
    )
    codename = Column(String(100), nullable=False)

    content_type = relationship("DjangoContentType")


class AuthUserGroup(Base):
    __tablename__ = "auth_user_groups"
    __table_args__ = (
        Index(
            "auth_user_groups_group_id_97559544_fk_auth_group_id",
            "group_id",
            unique=False,
        ),
        Index(
            "auth_user_groups_user_id_group_id_94350c0c_uniq",
            "user_id",
            "group_id",
            unique=True,
        ),
    )

    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey("auth_user.id"), nullable=False)
    group_id = Column(ForeignKey("auth_group.id"), nullable=False)

    group = relationship("AuthGroup")
    user = relationship("AuthUser")


class AuthGroupPermission(Base):
    __tablename__ = "auth_group_permissions"
    __table_args__ = (
        Index(
            "auth_group_permissions_group_id_permission_id_0cd325b0_uniq",
            "group_id",
            "permission_id",
            unique=True,
        ),
    )

    id = Column(Integer, primary_key=True)
    group_id = Column(ForeignKey("auth_group.id"), nullable=False)
    permission_id = Column(ForeignKey("auth_permission.id"), nullable=False)

    group = relationship("AuthGroup")
    permission = relationship("AuthPermission")


class AuthUserUserPermission(Base):
    __tablename__ = "auth_user_user_permissions"
    __table_args__ = (
        Index(
            "auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm",
            "permission_id",
            unique=False,
        ),
        Index(
            "auth_user_user_permissions_user_id_permission_id_14a6b632_uniq",
            "user_id",
            "permission_id",
            unique=True,
        ),
    )

    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey("auth_user.id"), nullable=False)
    permission_id = Column(ForeignKey("auth_permission.id"), nullable=False)

    permission = relationship("AuthPermission")
    user = relationship("AuthUser")
