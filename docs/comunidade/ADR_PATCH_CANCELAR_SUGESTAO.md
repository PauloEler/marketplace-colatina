# ADR - Saida secundaria no formulario Ouvir Colatina

## Decisao

Usar um link HTML para a Home com o texto **Cancelar e voltar**, abaixo do botao de envio.

## Motivo

Cancelar e uma navegacao, nao uma submissao. Um link evita JavaScript, nao aciona validacao, nao envia dados e mantem o comportamento previsivel.

## Alternativas rejeitadas

- botao `reset`: apagaria os campos, mas manteria a pessoa na mesma tela;
- `history.back()`: teria destino imprevisivel quando a pagina fosse aberta diretamente;
- segundo botao de formulario: aumentaria o risco de submissao acidental.

## Consequencias

A pessoa retorna diretamente para a Home. Nenhum rascunho e persistido ou transmitido.
