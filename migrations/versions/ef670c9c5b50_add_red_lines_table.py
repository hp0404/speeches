# -*- coding: utf-8 -*-
"""Add red lines table

Revision ID: ef670c9c5b50
Revises: 5a648740efbe
Create Date: 2023-01-30 09:55:36.412603

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision = "ef670c9c5b50"
down_revision = "5a648740efbe"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "red_lines",
        sa.Column("id", sa.Integer(), nullable=True),
        sa.Column("sentence_id", sa.Integer(), nullable=True),
        sa.Column("model_language", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("model_name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("model_type", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("model_version", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("model_performance", sa.Float(), nullable=True),
        sa.Column("prediction", sa.Float(), nullable=False),
        sa.Column("predicted_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["sentence_id"],
            ["sentences.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("red_lines")
    # ### end Alembic commands ###
