# Marco A: Base sólida jogável

## Contexto

O projeto implementa a versão básica de *Alien Invasion* do livro *Curso
Intensivo de Python*. O marco A preserva as regras atuais e cria a base para
perfis locais, retenção, áudio e distribuição no Windows.

## Objetivos

- Permitir criar e selecionar múltiplos perfis locais.
- Persistir recorde e maior nível alcançado por perfil.
- Aplicar uma interface de terminal arcade ao menu, HUD e fim da partida.
- Adicionar efeitos sonoros retrô, sintetizados e originais.
- Organizar o pacote Python e gerar uma distribuição portátil para Windows.
- Melhorar tipos, docstrings e documentação somente no código tocado.
- Manter commits pequenos e o worktree limpo ao concluir cada etapa.

## Fora do escopo

- Retomar uma partida interrompida.
- Começar uma partida em um nível desbloqueado.
- Excluir ou renomear perfis.
- Senhas, placar online, sincronização ou proteção contra fraude.
- Combos, power-ups, conquistas e novos inimigos.
- Instalador Inno Setup. Ele será criado após estabilizar gameplay e assets.
- Revisão completa de tipos e docstrings nos módulos não tocados.
- Testes automatizados neste marco.

## Experiência do jogador

### Seleção de perfil

Ao iniciar, o jogo mostra um terminal arcade operável pelo teclado. A tela
lista os perfis, recorde e maior nível. O jogador pode selecionar um perfil ou
criar outro. O último perfil usado aparece selecionado na próxima execução.

O nome possui entre 1 e 16 caracteres, não aceita caracteres de controle e é
único sem diferenciar maiúsculas de minúsculas.

### Partida

Toda nova partida começa no nível 1. As regras atuais de frota, tiro, vidas,
pontuação e aumento de dificuldade permanecem. O HUD escuro mostra piloto,
pontuação, recorde, nível e vidas.

Eventos produzem cinco sons: tiro, impacto em alienígena, dano à nave, nível
concluído e game over. Os arquivos WAV serão gerados para o projeto e
distribuídos com ele.

### Fim da partida

A tela final mostra pontuação, nível alcançado e indica novos recordes. `Enter`
inicia outra partida com o mesmo perfil. `Esc` retorna à seleção de perfis. `Q`
encerra o programa.

## Arquitetura

`main()` inicializa a aplicação e abre `ProfileMenu`. O menu recebe um
`ProfileStore`, cria ou seleciona o perfil e entrega o perfil ativo para
`AlienInvasion`.

`AlienInvasion` continua responsável pelo loop e pelas regras da partida. Ele
usa `ProfileStore` apenas nos eventos que alteram recorde ou maior nível e usa
`SoundManager` nos cinco eventos sonoros.

`ProfileStore` é o único módulo que conhece o formato JSON e o diretório de
dados. `SoundManager` é o único módulo que carrega e reproduz áudio. `Settings`
continua contendo balanceamento e tela, `GameStats` mantém o estado da partida
atual e `Scoreboard` continua responsável pela apresentação do HUD.

Não será criada uma máquina de cenas genérica. O fluxo possui somente seleção
de perfil, partida e resultado, integrados diretamente pelo controlador.

## Persistência

O arquivo será `%LOCALAPPDATA%\AlienInvasion\profiles.json`. Se
`LOCALAPPDATA` não estiver disponível, o diretório pessoal será usado como
fallback.

Formato inicial:

```json
{
  "version": 1,
  "active_profile": "André",
  "profiles": {
    "André": {
      "high_score": 12450,
      "highest_level": 8
    }
  }
}
```

O jogo salva ao criar ou trocar o perfil, superar o recorde ou alcançar novo
maior nível. A gravação ocorre em arquivo temporário no mesmo diretório e usa
substituição atômica.

Se o JSON for inválido, o arquivo original será preservado com sufixo
`.corrupt` e timestamp. O jogo abrirá uma base vazia e mostrará uma mensagem
recuperável. Erros de leitura e escrita serão apresentados sem encerrar a
partida atual.

## Áudio e assets

`assets.py` centralizará diretórios de imagens e sons. `SoundManager` tentará
inicializar o mixer e carregar todos os sons no início. Mixer indisponível ou
arquivo ausente desabilita somente o áudio afetado e registra um aviso; o jogo
continua funcional.

Os sons WAV serão curtos e sintetizados com biblioteca padrão, evitando
dependência de licença externa. O gerador não fará parte da execução normal do
jogo; somente os WAV gerados serão distribuídos.

## Organização do pacote

- Corrigir `alien_invaion.py` para `alien_invasion.py`.
- Converter imports internos para imports relativos.
- Expor `main()` em `alien_invasion.__init__`.
- Adicionar `alien_invasion.__main__` para `python -m alien_invasion`.
- Manter o comando de projeto `alien-invasion`.

## Distribuição Windows

PyInstaller produzirá um bundle `onedir` pelo Windows. Um arquivo `.spec`
versionado incluirá imagens e sons. O resultado será compactado em um `.zip`
portátil; Python e Pygame não serão exigidos na máquina do jogador.

O Inno Setup consumirá esse mesmo diretório em um marco posterior. O build não
usará `onefile` nesta etapa.

## Qualidade e documentação

Arquivos tocados receberão type hints úteis e docstrings que expliquem
responsabilidade ou comportamento não evidente. Não serão criadas abstrações
somente para satisfazer tipagem.

O README documentará requisitos para desenvolvimento, comandos de execução e
build, controles, localização dos perfis e conteúdo do pacote portátil.

## Verificação

Não serão escritos testes automatizados neste marco, por decisão do projeto.
A conclusão exige:

- Compilar todos os módulos Python sem erro.
- Executar o jogo pelo módulo e pelo comando do projeto.
- Criar dois perfis e validar isolamento de recorde e maior nível.
- Reiniciar o jogo e validar persistência e perfil ativo.
- Simular JSON inválido e validar preservação e recuperação.
- Validar o jogo com áudio disponível e indisponível.
- Gerar o bundle `onedir`, executá-lo fora do repositório e criar o `.zip`.
- Confirmar que imagens, sons e dados locais funcionam no executável.

## Versionamento

A versão funcional original está registrada como `v0.1.0`. O marco A será
lançado como `v0.2.0`, após commits separados para estrutura do pacote,
persistência, interface, áudio, documentação e distribuição. O instalador será
planejado após validar esse artefato portátil.
