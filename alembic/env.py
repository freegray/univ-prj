# alembic/env.py

from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import sys
import os
import logging

# ---------------------------
# 1. 로깅 설정
# ---------------------------
if context.config.config_file_name is not None:
    fileConfig(context.config.config_file_name)

logger = logging.getLogger('alembic.env')

# ---------------------------
# 2. 모델 임포트 및 메타데이터 설정
# ---------------------------
# 부모 디렉토리를 sys.path에 추가하여 모듈 임포트를 가능하게 함
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from 대학정보DB저장 import Base  # ORM 클래스가 정의된 파일을 임포트
    logger.info("ORM 모델이 성공적으로 임포트되었습니다.")
except ImportError as e:
    logger.error(f"ORM 모델 임포트 실패: {e}")
    raise

target_metadata = Base.metadata

# ---------------------------
# 3. Alembic 마이그레이션 함수
# ---------------------------
def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = context.get_x_argument(as_dictionary=True).get('sqlalchemy.url') or context.config.get_main_option("sqlalchemy.url")
    logger.info(f"Offline 모드에서 마이그레이션을 실행합니다. URL: {url}")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()
    logger.info("Offline 마이그레이션 완료.")

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    logger.info("온라인 모드에서 마이그레이션을 실행합니다.")
    connectable = engine_from_config(
        context.config.get_section(context.config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        logger.info("데이터베이스 연결 성공. 마이그레이션을 시작합니다.")
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()
        logger.info("온라인 마이그레이션 완료.")

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
