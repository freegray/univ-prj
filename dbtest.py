import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
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

# 비밀번호 URL 인코딩
encoded_password = quote_plus(DB_PASSWORD)

# DATABASE_URL 생성
DATABASE_URL = f'postgresql://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

# ---------------------------
# 4. 데이터베이스 연결 및 테이블 조회
# ---------------------------
def main():
    try:
        logger.info("데이터베이스 연결 시작")
        # SQLAlchemy 엔진 생성
        engine = create_engine(DATABASE_URL, echo=False)
        logger.info(f"데이터베이스에 연결 중: {DATABASE_URL}")

        # 데이터베이스 연결 테스트
        try:
            connection = engine.connect()
            logger.info("데이터베이스 연결 성공")
            connection.close()
        except Exception as e:
            logger.error(f"데이터베이스 연결 실패: {e}")
            return

        # 세션 생성
        Session = sessionmaker(bind=engine)
        session = Session()

        # 예제: tbl_corporations 테이블의 모든 데이터 조회
        try:
            corporations = session.query(Corporation).all()
            logger.info("tbl_corporations 테이블 데이터 조회 완료")
            for corp in corporations:
                print(corp)
        except Exception as e:
            logger.error(f"테이블 조회 중 오류 발생: {e}")
        finally:
            # 세션 종료
            session.close()
            logger.info("세션 종료")
    except Exception as e:
        logger.error(f"스크립트 실행 중 오류 발생: {e}")

if __name__ == "__main__":
    main()
