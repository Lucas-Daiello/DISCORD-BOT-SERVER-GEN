Gere apenas um JSON válido, sem explicações, sem comentários e sem texto fora do JSON.

O JSON deve representar a estrutura completa de um servidor robusto e prifssional do Discord sobre o tema: {TEMA}, seguindo exatamente este formato:

server_name: nome do servidor

roles: lista de cargos, cada um contendo:

name: nome do cargo

color: cor em hexadecimal

permissions: lista de permissões do Discord em snake_case

categories: lista de categorias, cada uma contendo:

name: nome da categoria

channels: lista de canais da categoria

name: nome do canal

type: "text" ou "voice"

overwrites: objeto onde a chave é o nome do cargo e o valor é uma lista de permissões permitidas naquele canal

Regras obrigatórias:

O JSON deve ser 100% válido

Não usar comentários

Não usar permissões inexistentes

Todos os canais devem estar dentro de uma categoria

Os nomes dos cargos usados em overwrites devem existir na lista de roles

Usar apenas strings, listas e objetos (nada de null)

Crie um exemplo completo de servidor organizado, realista e pronto para ser lido por um bot Discord em Python.

O servidor precisa ter no mínimo 40 canais de texto, 40 canais de voz e 25 cargos
O nome dos canais precisam ter um emoji de referencia antes para ficar mais bonito
Se quiser, divida a mensagem em 2 sem quebrar palavras ao meio
O servidor deve ser em português
