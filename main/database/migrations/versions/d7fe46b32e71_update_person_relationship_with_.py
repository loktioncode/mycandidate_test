"""add data_schemas to Config model v2

Revision ID: f4116ef84ae6
Revises: 8659d84acd70
Create Date: 2024-02-15 15:00:56.940592

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd7fe46b32e71'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('site_settings',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('title', sa.String(), nullable=True),
    sa.Column('title_short', sa.String(), nullable=True),
    sa.Column('favicon_logo', sa.String(), nullable=True),
    sa.Column('logo_colour', sa.String(), nullable=True),
    sa.Column('footer_colour', sa.String(), nullable=True),
    sa.Column('nav_bars_colour', sa.String(), nullable=True),
    sa.Column('body_foreground_colour', sa.String(), nullable=True),
    sa.Column('body_background_colour', sa.String(), nullable=True),
    sa.Column('find_candidates_button', sa.String(), nullable=True),
    sa.Column('candidate_names_colour', sa.String(), nullable=True),
    sa.Column('data_schemas', sa.String(), nullable=True),
    sa.Column('partner_name', sa.String(), nullable=True),
    sa.Column('partner_website', sa.String(), nullable=True),
    sa.Column('google_analytics_key', sa.String(), nullable=True),
    sa.Column('gtag_script', sa.String(), nullable=True),
    sa.Column('organization_name', sa.String(), nullable=True),
    sa.Column('organization_link', sa.String(), nullable=True),
    sa.Column('regional_explainer', sa.String(), nullable=True),
    sa.Column('provincial_explainer', sa.String(), nullable=True),
    sa.Column('national_explainer', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('site_settings')
