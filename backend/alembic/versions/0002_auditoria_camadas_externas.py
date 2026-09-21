"""auditoria em camadas_externas: a tabela recebe escrita pela API e faltava na trilha (RF-13)

Revision ID: 0002
Revises: 0001
Create Date: 2026-09-15

"""

from typing import Sequence, Union

from alembic import op

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Mesma função genérica da migração 0001 (SECURITY DEFINER): RF-13 pede
    # trilha de *toda* escrita, e `camadas_externas` é escrita por
    # POST/PATCH /api/camadas-externas.
    op.execute(
        """
        CREATE TRIGGER trg_auditoria_camadas_externas
            AFTER INSERT OR UPDATE OR DELETE ON camadas_externas
            FOR EACH ROW
            EXECUTE FUNCTION fn_auditoria()
        """
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_auditoria_camadas_externas ON camadas_externas")
