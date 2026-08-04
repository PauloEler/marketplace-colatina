import re


class ProfessionalServiceValidationError(ValueError):
    pass


def _whatsapp_digits(value):
    return re.sub(r"\D", "", value or "")


def validate_service(title, neighborhood, whatsapp):
    title = " ".join((title or "").split())
    neighborhood = " ".join((neighborhood or "").split())
    whatsapp = _whatsapp_digits(whatsapp)
    if len(title) < 4 or len(title) > 100:
        raise ProfessionalServiceValidationError(
            "Diga em poucas palavras qual serviço você oferece."
        )
    if len(neighborhood) < 2 or len(neighborhood) > 60:
        raise ProfessionalServiceValidationError("Informe seu bairro em Colatina.")
    if len(whatsapp) not in {10, 11}:
        raise ProfessionalServiceValidationError("Informe um WhatsApp com DDD.")
    return title, neighborhood, whatsapp


def publish_service(db, user_id, title, neighborhood, whatsapp):
    title, neighborhood, whatsapp = validate_service(title, neighborhood, whatsapp)
    existing = db.execute(
        "SELECT id FROM servicos_profissionais WHERE usuario_id=? AND ativo=1 "
        "ORDER BY criado_em DESC LIMIT 1",
        (user_id,),
    ).fetchone()
    if existing:
        db.execute(
            "UPDATE servicos_profissionais SET titulo=?, bairro=?, whatsapp=?, "
            "atualizado_em=CURRENT_TIMESTAMP WHERE id=?",
            (title, neighborhood, whatsapp, existing["id"]),
        )
        service_id = existing["id"]
    else:
        service_id = db.execute(
            "INSERT INTO servicos_profissionais "
            "(usuario_id, titulo, bairro, whatsapp) VALUES (?,?,?,?) RETURNING id",
            (user_id, title, neighborhood, whatsapp),
        ).fetchone()[0]
    db.commit()
    return service_id


def list_services(db):
    return db.execute(
        "SELECT s.id, s.titulo, s.bairro, s.whatsapp, s.criado_em, "
        "COALESCE(u.loja_nome, u.nome) AS profissional "
        "FROM servicos_profissionais s JOIN usuarios u ON u.id=s.usuario_id "
        "WHERE s.ativo=1 AND u.ativo=1 ORDER BY s.atualizado_em DESC, s.id DESC"
    ).fetchall()
