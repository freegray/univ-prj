# 대학정보DB저장.py

import os
import pandas as pd
from openpyxl import load_workbook
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Enum as SAEnum, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from alembic.config import Config
from alembic import command
import enum
import logging
from urllib.parse import quote_plus

# ---------------------------
# 1. 로깅 설정
# ---------------------------
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ---------------------------
# 2. 데이터베이스 연결 정보
# ---------------------------
DB_USER = 'postgres'
DB_PASSWORD = 'outworld21'
DB_HOST = 'localhost'
DB_PORT = '5432'
DB_NAME = 'univ_info'

ALEMBIC_CFG_PATH = 'alembic.ini'  # Alembic 설정 파일 경로

# ---------------------------
# 3. ENUM 클래스 정의
# ---------------------------
def create_enum(name, members):
    return enum.Enum(name, {member: member for member in members})

SchoolTypeEnum = create_enum("SchoolTypeEnum", ["전문대학", "대학", "대학원", "대학원대학"])
MainBranchEnum = create_enum("MainBranchEnum", ["본교", "분교", "제2캠퍼스", "제3캠퍼스", "제4캠퍼스"])
RegionEnum = create_enum("RegionEnum", ["서울", "인천", "경기", "강원", "충북", "충남", "세종",
                                        "대전", "경북", "대구", "경남", "부산", "울산",
                                        "전북", "전남", "광주", "제주"])
EstablishmentTypeEnum = create_enum("EstablishmentTypeEnum", ["공립", "국립", "사립",
                                                              "국립대법인", "특별법국립",
                                                              "특별법법인", "기타"])
SchoolStatusEnum = create_enum("SchoolStatusEnum", ["기존", "폐교", "신설"])

# ---------------------------
# 4. ORM 클래스 정의
# ---------------------------
Base = declarative_base()

class Corporation(Base):
    __tablename__ = 'tbl_corporations'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='법인 ID')
    name = Column(String(100), unique=True, nullable=False, comment='법인명')

    # 관계 설정 (back_populates는 UniversityInfo의 'corporation'과 일치해야 함)
    universities = relationship("UniversityInfo", back_populates="corporation")

    def __repr__(self):
        return f"<Corporation(id={self.id}, name='{self.name}')>"

class UniversityInfo(Base):
    __tablename__ = 'tbl_university_info'
    id = Column(Integer, primary_key=True, autoincrement=True, comment='학교ID')
    u_code = Column(Integer, unique=True, nullable=False, comment='학교코드')
    u_type = Column(SAEnum(SchoolTypeEnum, name='school_type_enum'), nullable=False, comment='학교구분')
    u_name = Column(String(100), nullable=False, comment='학교명')
    main_branch = Column(SAEnum(MainBranchEnum, name='main_branch_enum'), nullable=False, comment='본분교')
    academic_system = Column(String(100), comment='학제')
    is_remote = Column(Boolean, nullable=False, default=False, comment='원격대학')
    region = Column(SAEnum(RegionEnum, name='region_enum'), nullable=False, comment='지역')
    establishment_type = Column(SAEnum(EstablishmentTypeEnum, name='establishment_type_enum'), nullable=False, comment='설립구분')
    related_laws = Column(String(100), comment='관계법령')
    corporation_id = Column(Integer, ForeignKey('tbl_corporations.id'), nullable=True, comment='법인 ID')
    u_status = Column(SAEnum(SchoolStatusEnum, name='school_status_enum'), nullable=False, comment='학교상태')

    # 관계 설정 (back_populates는 Corporation의 'universities'와 일치해야 함)
    corporation = relationship("Corporation", back_populates="universities")   

    def __repr__(self):
        return f"<UniversityInfo(id={self.id}, u_code='{self.u_code}', u_name='{self.u_name}')>"

# ---------------------------
# 5. Alembic 마이그레이션 함수
# ---------------------------
def run_alembic_migrations(alembic_cfg_path, database_url):
    """
    Alembic 마이그레이션을 실행하는 함수.
    """
    try:
        logger.info("Alembic 마이그레이션을 시작합니다.")
        alembic_cfg = Config(alembic_cfg_path)
        # Alembic 설정에 DATABASE_URL 주입
        alembic_cfg.set_main_option('sqlalchemy.url', database_url)
        command.upgrade(alembic_cfg, "head")
        logger.info("Alembic 마이그레이션이 성공적으로 적용되었습니다.")
    except Exception as e:
        logger.error(f"Alembic 마이그레이션 실패: {e}")
        raise

# ---------------------------
# 6. 엑셀 파일 읽기 함수
# ---------------------------
def read_excel_to_dataframe(excel_file_path, sheet_name=None):
    """
    엑셀 파일을 읽어 pandas DataFrame으로 변환하는 함수.
    """
    try:
        # openpyxl을 사용하여 엑셀 파일 로드
        wb = load_workbook(excel_file_path, data_only=True)
        
        # 특정 시트를 선택하거나 활성 시트 선택
        if sheet_name:
            sheet = wb[sheet_name]
        else:
            sheet = wb.active
        
        # 시트의 모든 데이터 읽기
        data = sheet.values
        
        # 첫 번째 행을 헤더로 사용
        columns = next(data)
        
        # 나머지 데이터를 리스트로 변환
        data = list(data)
        
        # pandas DataFrame으로 변환
        df = pd.DataFrame(data, columns=columns)
        
        logger.info(f"엑셀 파일 '{excel_file_path}'을 성공적으로 읽었습니다.")
        return df
    except FileNotFoundError as fnf_error:
        logger.error(f"엑셀 파일을 찾을 수 없습니다: {fnf_error}")
        raise
    except Exception as e:
        logger.error(f"엑셀 파일 읽기 중 오류 발생: {e}")
        raise

# ---------------------------
# 7. 데이터 업로드 함수
# ---------------------------
def upload_data(session, df):
    """
    DataFrame을 tbl_university_info 테이블에 데이터를 업로드하는 함수.
    """
    try:
        # 필요한 컬럼이 모두 있는지 확인
        required_columns = ['학교구분', '학교코드', '학교명', '본분교', '학제', '원격대학', '지역', '설립구분', '관련법령', '법인명','학교상태']
        for col in required_columns:
            if col not in df.columns:
                logger.error(f"필수 컬럼 '{col}'이(가) DataFrame에 존재하지 않습니다.")
                return
        
        # 필요한 컬럼만 선택
        df = df[required_columns]
        
        # 데이터 삽입
        for index, row in df.iterrows():
            try:
                # 법인명 처리: 먼저 Corporation 테이블에 존재하는지 확인
                corporation_name = row.get('법인명')
                corporation = None
                if corporation_name:
                    corporation = session.query(Corporation).filter_by(name=corporation_name).first()
                    if not corporation:
                        # 새 법인 추가
                        corporation = Corporation(name=corporation_name)
                        session.add(corporation)
                        session.commit()  # 법인 ID를 얻기 위해 커밋
                        logger.info(f"새로운 법인 '{corporation_name}'이 추가되었습니다.")

                # UniversityInfo 인스턴스 생성
                university = UniversityInfo(
                    u_type=SchoolTypeEnum(row['학교구분']),
                    u_code=row['학교코드'],
                    u_name=row['학교명'],
                    main_branch=MainBranchEnum(row['본분교']),
                    academic_system=row.get('학제'),
                    is_remote=row.get('원격대학', False),
                    region=RegionEnum(row['지역']),
                    establishment_type=EstablishmentTypeEnum(row['설립구분']),
                    related_laws=row.get('관련법령'),
                    corporation_id=corporation.id if corporation else None,
                    u_status=SchoolStatusEnum(row['학교상태'])
                )
                session.add(university)

                # 큰 데이터셋일 경우 일정량씩 커밋
                if index % 100 == 0:
                    session.commit()
                    logger.info(f"{index} rows inserted.")
            except Exception as e:
                session.rollback()
                logger.error(f"Error inserting row {index}: {e}")

        # 최종 커밋
        session.commit()
        logger.info("데이터 삽입 완료.")
    except Exception as e:
        logger.error(f"데이터 업로드 실패: {e}")
        raise

# ---------------------------
# 8. 메인 함수
# ---------------------------
def main():
    try:
        # 비밀번호 URL 인코딩
        encoded_password = quote_plus(DB_PASSWORD)  # 비밀번호 URL 인코딩
        
        # DATABASE_URL 생성
        DATABASE_URL = f'postgresql://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
        logger.info(f"데이터베이스 URL: {DATABASE_URL}")
        
        # SQLAlchemy 엔진 생성
        engine = create_engine(DATABASE_URL)
        logger.info("SQLAlchemy 엔진 생성 완료.")
        
        # 데이터베이스 연결 테스트
        try:
            with engine.connect() as connection:
                logger.info("데이터베이스 연결 성공.")
        except Exception as e:
            logger.error(f"데이터베이스 연결 실패: {e}")
            return

        # 세션 생성
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()

        try:
            logger.info("Alembic 마이그레이션 실행 중...")
            # Alembic 마이그레이션 실행
            run_alembic_migrations(ALEMBIC_CFG_PATH, DATABASE_URL)
            
            logger.info("Alembic 마이그레이션 완료 후 다음 단계로 진행합니다.")

            # 엑셀 파일 경로 설정 (절대 경로 사용 권장)
            current_dir = os.path.dirname(os.path.abspath(__file__))
            excel_folder = os.path.join(current_dir, 'information')
            excel_file_name = '학교개황(20240305기준).xlsx'
            excel_file_path = os.path.join(excel_folder, excel_file_name)

            # 파일 존재 여부 확인
            if not os.path.isfile(excel_file_path):
                logger.error(f"엑셀 파일을 찾을 수 없습니다: {excel_file_path}")
                return

            logger.info(f"엑셀 파일을 읽는 중: {excel_file_path}")
            print(f"엑셀 파일을 읽는 중: {excel_file_path}")
            # 엑셀 파일 읽기
            df = read_excel_to_dataframe(excel_file_path, sheet_name=None)

            logger.info("데이터 업로드를 시작합니다.")
            # 데이터 업로드
            upload_data(session, df)
        except Exception as e:
            logger.error(f"마이그레이션 또는 데이터 업로드 중 오류 발생: {e}")
        finally:
            # 세션 종료
            session.close()
            logger.info("세션이 종료되었습니다.")
            print ("세션이 종료되었습니다.")
        
        logger.info("스크립트가 정상적으로 완료되었습니다.")
    except Exception as e:
        logger.error(f"스크립트 실행 중 오류 발생: {e}")

if __name__ == "__main__":
    main()
