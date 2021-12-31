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
This module contains Table definitions primarily used for the web UI
"""

import enum

from sqlalchemy import text
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import (
    Column,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
)
from sqlalchemy.sql.sqltypes import (
    Boolean,
    DateTime,
    Enum,
    Integer,
    String,
    Text,
)

from .sameta import Base


class ImageEnum(enum.Enum):
    JPEG = "image/jpeg"
    GIF = "image/gif"
    PNG = "image/png"


class DjangoCeleryResultsChordcounter(Base):
    __tablename__ = "django_celery_results_chordcounter"

    id = Column(Integer, primary_key=True)
    group_id = Column(String(255), nullable=False, unique=True)
    sub_tasks = Column(Text, nullable=False)
    count = Column(Integer, nullable=False)


class DjangoCeleryResultsGroupresult(Base):
    __tablename__ = "django_celery_results_groupresult"
    __table_args__ = (
        Index(
            "django_cele_date_cr_bd6c1d_idx",
            "date_created",
            unique=False,
        ),
        Index(
            "django_cele_date_do_caae0e_idx",
            "date_done",
            unique=False,
        ),
    )

    id = Column(Integer, primary_key=True)
    group_id = Column(String(255), nullable=False, unique=True)
    date_created = Column(DateTime(timezone=True), nullable=False)
    date_done = Column(DateTime(timezone=True), nullable=False)
    content_type = Column(String(128), nullable=False)
    content_encoding = Column(String(64), nullable=False)
    result = Column(Text)


class DjangoCeleryResultsTaskresult(Base):
    __tablename__ = "django_celery_results_taskresult"
    __table_args__ = (
        Index(
            "django_cele_task_na_08aec9_idx",
            "task_name",
            unique=False,
        ),
        Index(
            "django_cele_status_9b6201_idx",
            "status",
            unique=False,
        ),
        Index(
            "django_cele_worker_d54dd8_idx",
            "worker",
            unique=False,
        ),
        Index(
            "django_cele_date_cr_f04a50_idx",
            "date_created",
            unique=False,
        ),
        Index(
            "django_cele_date_do_f59aad_idx",
            "date_done",
            unique=False,
        ),
    )

    id = Column(Integer, primary_key=True)
    task_id = Column(String(255), nullable=False, unique=True)
    status = Column(String(50), nullable=False)
    content_type = Column(String(128), nullable=False)
    content_encoding = Column(String(64), nullable=False)
    result = Column(Text)
    date_done = Column(DateTime(timezone=True), nullable=False)
    traceback = Column(Text)
    meta = Column(Text)
    task_args = Column(Text)
    task_kwargs = Column(Text)
    task_name = Column(String(255))
    worker = Column(String(100))
    date_created = Column(DateTime(timezone=True), nullable=False)


class DjangoContentType(Base):
    __tablename__ = "django_content_type"
    __table_args__ = (
        Index(
            "django_content_type_app_label_model_76bd3d3b_uniq",
            "app_label",
            "model",
            unique=True,
        ),
    )

    id = Column(Integer, primary_key=True)
    app_label = Column(String(100), nullable=False)
    model = Column(String(100), nullable=False)


class DjangoMigration(Base):
    __tablename__ = "django_migrations"

    id = Column(Integer, primary_key=True)
    app = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    applied = Column(DateTime(timezone=True), nullable=False)


class DjangoSession(Base):
    __tablename__ = "django_session"
    __table_args__ = (
        Index(
            "django_session_expire_date_a5c62663", "expire_date", unique=False
        ),
    )

    session_key = Column(String(40), primary_key=True)
    session_data = Column(Text, nullable=False)
    expire_date = Column(DateTime(timezone=True), nullable=False)


class DjangoAdminLog(Base):
    __tablename__ = "django_admin_log"
    __table_args__ = (
        Index(
            "django_admin_log_content_type_id_c4bce8eb_fk_django_co",
            "content_type_id",
            unique=False,
        ),
        Index(
            "django_admin_log_user_id_c564eba6_fk_auth_user_id",
            "user_id",
            unique=False,
        ),
    )

    id = Column(Integer, primary_key=True)
    action_time = Column(DateTime(timezone=True), nullable=False)
    object_id = Column(Text)
    object_repr = Column(String(200), nullable=False)
    action_flag = Column(Integer, nullable=False)
    change_message = Column(Text, nullable=False)
    content_type_id = Column(ForeignKey("django_content_type.id"))
    user_id = Column(ForeignKey("auth_user.id"), nullable=False)

    content_type = relationship("DjangoContentType")
    user = relationship("AuthUser")


class RestFrameworkTrackingApirequestlog(Base):
    __tablename__ = "rest_framework_tracking_apirequestlog"
    __table_args__ = (
        Index(
            "rest_framework_tracking_apirequestlog_path_fe81f91b",
            "path",
            unique=False,
        ),
        Index(
            "rest_framework_tracking_apirequestlog_requested_at_b6f1c2f2",
            "requested_at",
            unique=False,
        ),
        Index(
            "rest_framework_tracking_apirequestlog_status_code_3c9e2003",
            "status_code",
            unique=False,
        ),
        Index(
            "rest_framework_track_user_id_671b70b7_fk_auth_user",
            "user_id",
            unique=False,
        ),
        Index(
            "rest_framework_tracking_apirequestlog_view_5bd1e407",
            "view",
            unique=False,
        ),
        Index(
            "rest_framework_tracking_apirequestlog_view_method_dd790881",
            "view_method",
            unique=False,
        ),
        ForeignKeyConstraint(
            ["user_id"],
            ["auth_user.id"],
            name="rest_framework_track_user_id_671b70b7_fk_auth_user",
        ),
    )

    id = Column(Integer, primary_key=True)
    requested_at = Column(DateTime(timezone=True), nullable=False)
    response_ms = Column(Integer, nullable=False)
    path = Column(String(200), nullable=False)
    remote_addr = Column(String(39), nullable=False)
    host = Column(String(200), nullable=False)
    method = Column(String(10), nullable=False)
    query_params = Column(Text)
    data = Column(Text)
    response = Column(Text)
    status_code = Column(Integer)
    user_id = Column(Integer)
    view = Column(String(200))
    view_method = Column(String(200))
    errors = Column(Text)
    username_persistent = Column(String(200))

    user = relationship("AuthUser")


class RenderPreset(Base):
    __tablename__ = "render_presets"
    __table_args__ = (Index("category", "category", "preset"),)

    id = Column(Integer, primary_key=True)
    category = Column(String(64), nullable=False)
    preset = Column(String(64), nullable=False)
    description = Column(String(255))
    hmax = Column(Integer, nullable=False)
    wmax = Column(Integer, nullable=False)
    placeholder = Column(String(64))
    noproportion = Column(Boolean)
    force_mime = Column(Enum(ImageEnum))
    crop = Column(
        String(8),
        nullable=False,
        server_default=text("'center'"),
    )
    placeholder_image = Column(String(255))


class ThumbnailKvstore(Base):
    __tablename__ = "thumbnail_kvstore"

    key = Column(String(200), primary_key=True)
    value = Column(Text, nullable=False)


class Shoutbox(Base):
    __tablename__ = "shoutbox"
    __table_args__ = (
        Index("when", "added", unique=False),
        Index("user_id", "user_id", unique=False),
        ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="shoutbox_ibfk_1",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
    )

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    message = Column(String(255), nullable=False)
    added = Column(DateTime(timezone=True), nullable=False)

    user = relationship("User")
