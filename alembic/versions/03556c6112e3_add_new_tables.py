"""Add new tables

Revision ID: 03556c6112e3
Revises: 
Create Date: 2024-09-22 21:58:32.850484

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '03556c6112e3'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('tbl_corporations',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False, comment='법인 ID'),
    sa.Column('name', sa.String(length=100), nullable=False, comment='법인명'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('tbl_university_info',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False, comment='학교ID'),
    sa.Column('u_code', sa.Integer(), nullable=False, comment='학교코드'),
    sa.Column('u_type', sa.Enum('전문대학', '대학', '대학원', '대학원대학', name='school_type_enum'), nullable=False, comment='학교구분'),
    sa.Column('u_name', sa.String(length=100), nullable=False, comment='학교명'),
    sa.Column('main_branch', sa.Enum('본교', '분교', '제2캠퍼스', '제3캠퍼스', '제4캠퍼스', name='main_branch_enum'), nullable=False, comment='본분교'),
    sa.Column('academic_system', sa.String(length=100), nullable=True, comment='학제'),
    sa.Column('is_remote', sa.Boolean(), nullable=False, comment='원격대학'),
    sa.Column('region', sa.Enum('서울', '인천', '경기', '강원', '충북', '충남', '세종', '대전', '경북', '대구', '경남', '부산', '울산', '전북', '전남', '광주', '제주', name='region_enum'), nullable=False, comment='지역'),
    sa.Column('establishment_type', sa.Enum('공립', '국립', '사립', '국립대법인', '특별법국립', '특별법법인', '기타', name='establishment_type_enum'), nullable=False, comment='설립구분'),
    sa.Column('related_laws', sa.String(length=100), nullable=True, comment='관계법령'),
    sa.Column('corporation_id', sa.Integer(), nullable=True, comment='법인 ID'),
    sa.Column('u_status', sa.Enum('기존', '폐교', '신설', name='school_status_enum'), nullable=False, comment='학교상태'),
    sa.ForeignKeyConstraint(['corporation_id'], ['tbl_corporations.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('u_code')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('tbl_university_info')
    op.drop_table('tbl_corporations')
    # ### end Alembic commands ###