# Processo de Decisão

## Fluxo obrigatório

`Problema → Discussão → RFC → ADR → Sprint → Desenvolvimento → Testes → Documentação → PR → Merge → Deploy → Medição → Lições Aprendidas`

## Portões

| Etapa | Saída necessária | Autoriza a próxima? |
|---|---|---|
| Problema | público, contexto e impacto | não, apenas descoberta |
| Discussão | alternativas, riscos e dúvidas | autoriza redigir RFC |
| RFC | proposta, escopo e critérios | depende de aprovação |
| ADR | decisão e consequências | orienta a execução |
| Sprint | Ordem de Serviço autorizada | autoriza implementar o escopo |
| Desenvolvimento | mudança rastreável | exige testes |
| Testes | evidências proporcionais ao risco | permite revisão |
| Documentação | operação e limites registrados | completa a entrega |
| PR | revisão e CI | merge só com autorização |
| Merge | integração confirmada | deploy conforme autorização |
| Deploy | produção saudável | inicia medição |
| Medição | resultado comparado ao esperado | gera lições |
| Lições | decisão de manter, corrigir ou encerrar | alimenta backlog e roadmap |

## Regra de decisão

Decisões devem registrar responsável, data, evidência, alternativas e consequência. Ausência de dados deve aparecer como incerteza, nunca como certeza implícita.

## Urgências

Incidentes podem abreviar a discussão, mas não eliminam testes, registro, revisão posterior ou autorização compatível com o risco.
