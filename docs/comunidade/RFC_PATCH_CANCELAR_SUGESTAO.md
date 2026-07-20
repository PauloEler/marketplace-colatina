# RFC - Cancelar envio de sugestao

## Problema real

Depois de abrir ou preencher o formulario Ouvir Colatina, a pessoa nao tinha uma saida clara junto das acoes finais. O unico retorno visivel ficava no topo da pagina.

## Objetivo

Oferecer uma acao secundaria, imediatamente abaixo do envio, que permita abandonar o formulario sem transmitir dados.

## Solucao

Adicionar o link **Cancelar e voltar** abaixo de **Enviar sugestao**, apontando para a Home. A acao usa navegacao HTML comum, nao submete o formulario e nao cria estado novo.

## Criterios

- ordem visual: enviar, cancelar, aviso de privacidade;
- area de toque minima de 44 px;
- foco visivel por teclado;
- desktop e mobile sem overflow;
- nenhuma alteracao no cadastro ou painel administrativo de sugestoes.
