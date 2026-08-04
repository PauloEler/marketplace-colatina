import re


class ProfessionalServiceValidationError(ValueError):
    pass


COMMON_SERVICES = (
    "Pedreiro",
    "Pintor",
    "Reformas em geral",
    "Eletricista",
    "Encanador",
    "Diarista",
    "Jardineiro",
    "Frete e mudança",
    "Montador de móveis",
    "Manutenção residencial",
)


def _whatsapp_digits(value):
    return re.sub(r"\D", "", value or "")


def validate_service(
    professional_name, services, other_service, details, neighborhood, whatsapp
):
    professional_name = " ".join((professional_name or "").split())
    selected = [item for item in services if item in COMMON_SERVICES]
    other_service = " ".join((other_service or "").split())
    if other_service:
        selected.append(other_service)
    selected = list(dict.fromkeys(selected))
    title = " · ".join(selected)
    details = " ".join((details or "").split())
    neighborhood = " ".join((neighborhood or "").split())
    whatsapp = _whatsapp_digits(whatsapp)
    if len(professional_name) < 3 or len(professional_name) > 80:
        raise ProfessionalServiceValidationError(
            "Informe o nome do profissional ou do negócio."
        )
    if not selected or len(title) > 180:
        raise ProfessionalServiceValidationError(
            "Selecione pelo menos um serviço que você oferece."
        )
    if len(other_service) > 80:
        raise ProfessionalServiceValidationError("O nome do serviço é muito longo.")
    if len(details) > 600:
        raise ProfessionalServiceValidationError(
            "O detalhamento deve ter no máximo 600 caracteres."
        )
    if len(neighborhood) < 2 or len(neighborhood) > 60:
        raise ProfessionalServiceValidationError("Informe seu bairro em Colatina.")
    if len(whatsapp) not in {10, 11}:
        raise ProfessionalServiceValidationError("Informe um WhatsApp com DDD.")
    return professional_name, title, details, neighborhood, whatsapp


def publish_service(
    db,
    user_id,
    professional_name,
    services,
    other_service,
    details,
    neighborhood,
    whatsapp,
):
    professional_name, title, details, neighborhood, whatsapp = validate_service(
        professional_name, services, other_service, details, neighborhood, whatsapp
    )
    existing = db.execute(
        "SELECT id FROM servicos_profissionais WHERE usuario_id=? AND ativo=1 "
        "ORDER BY criado_em DESC LIMIT 1",
        (user_id,),
    ).fetchone()
    if existing:
        db.execute(
            "UPDATE servicos_profissionais SET nome_profissional=?, titulo=?, "
            "detalhes=?, bairro=?, "
            "whatsapp=?, atualizado_em=CURRENT_TIMESTAMP WHERE id=?",
            (
                professional_name,
                title,
                details,
                neighborhood,
                whatsapp,
                existing["id"],
            ),
        )
        service_id = existing["id"]
    else:
        service_id = db.execute(
            "INSERT INTO servicos_profissionais "
            "(usuario_id, nome_profissional, titulo, detalhes, bairro, whatsapp) "
            "VALUES (?,?,?,?,?,?) RETURNING id",
            (user_id, professional_name, title, details, neighborhood, whatsapp),
        ).fetchone()[0]
    db.commit()
    return service_id


def list_services(db):
    return db.execute(
        "SELECT s.id, s.titulo, s.detalhes, s.bairro, s.whatsapp, s.criado_em, "
        "COALESCE(NULLIF(s.nome_profissional,''), u.loja_nome, u.nome) AS profissional "
        "FROM servicos_profissionais s JOIN usuarios u ON u.id=s.usuario_id "
        "WHERE s.ativo=1 AND u.ativo=1 ORDER BY s.atualizado_em DESC, s.id DESC"
    ).fetchall()
