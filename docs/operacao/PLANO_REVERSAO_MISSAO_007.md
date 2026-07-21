# Plano de reversão — Missão 007 Home 2.0

## Reversão imediata

Definir no Render:

```text
HOME_2_ENABLED=false
```

Reiniciar o serviço. Nenhuma migração, limpeza de dados ou alteração adicional
é necessária. A Home publicada volta a ser renderizada pelo ramo preservado.

## Reversão de código

Se a remoção integral for necessária, reverter o único commit da Missão 007:

```text
git revert <hash-do-commit-da-missao-007>
```

## Checklist

1. Confirmar ausência de `.home-2-mission007` no `body`.
2. Confirmar presença de `.ux005c-first-fold`.
3. Validar Hero, busca, compartilhamento e Encontre Quem Resolve publicados.
4. Verificar 1440, 1024, 768, 390 e 320 px sem overflow.
5. Confirmar console limpo e seções posteriores preservadas.

## Evidência executada

Com a flag desligada, as cinco capturas foram idênticas às imagens de referência
anteriores à implementação: `0,0000%` de diferença de pixels.
