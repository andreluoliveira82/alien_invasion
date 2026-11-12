# Invasão Alienígena

## Descrição

Jogo arcade de defesa espacial feito com Pygame. Você controla uma nave na parte inferior da tela, dispara contra frotas alienígenas e tenta sobreviver por três vidas. Cada frota destruída abre um nível mais rápido.

## Recursos atuais

- Partidas em tela cheia, com pontuação, nível e vidas no painel.
- Seleção e criação de pilotos, com recorde e maior nível separados por perfil.
- Tela de fim de jogo com nova tentativa ou retorno à seleção de pilotos.
- Cinco efeitos sonoros para disparo, acerto, dano, avanço de nível e fim de jogo.
- Áudio opcional: se o dispositivo ou um efeito estiver indisponível, o jogo continua e mostra um aviso.

## Controles

| Tecla | Ação |
| --- | --- |
| Setas esquerda e direita | Mover a nave durante a partida. |
| Setas para cima e para baixo | Escolher um piloto ou a opção de criar piloto no menu. |
| Espaço | Disparar durante a partida. |
| Enter | Selecionar um piloto, iniciar a criação, confirmar o nome ou tentar novamente após o fim de jogo. |
| Esc | Cancelar a digitação do nome, sair do menu ou voltar à seleção de pilotos após o fim de jogo. |
| Q | Sair do menu ou do jogo; durante a digitação, entra como parte do nome. |

No menu, também é possível selecionar uma linha com o mouse e clicar novamente para ativá-la.

## Perfis e dados salvos

Cada piloto guarda seu recorde e maior nível alcançado. Uma nova partida reinicia pontos, nível e vidas da sessão, preservando o progresso salvo. O último piloto selecionado fica marcado para a próxima abertura.

Os nomes devem ter entre 1 e 16 caracteres. Nomes iguais, mesmo com diferenças entre maiúsculas e minúsculas, não podem ser repetidos.

No Windows, os dados ficam em:

```text
%LOCALAPPDATA%\AlienInvasion\profiles.json
```

O jogo salva o progresso quando o recorde ou o maior nível aumenta. Se encontrar um arquivo inválido, tenta preservá-lo em um arquivo com data e extensão `.corrupt.json` e exibe um aviso. Falhas de leitura ou gravação também são informadas sem sobrescrever dados que não puderam ser preservados.

Remover a pasta portátil não apaga os perfis em LocalAppData. Para apagar o progresso, remova esse arquivo separadamente com o jogo fechado.

## Desenvolvimento

Requisitos: Windows para gerar a versão portátil, Python 3.13 ou superior e [uv](https://docs.astral.sh/uv/).

Na raiz do projeto, instale as dependências e execute:

```powershell
uv sync
uv run python -m alien_invasion
```

O comando instalado pelo pacote também está disponível:

```powershell
uv run alien-invasion
```

Os efeitos WAV originais podem ser regenerados com `uv run python scripts/generate_sounds.py`.

## Gerar a versão portátil para Windows

Na raiz do projeto, execute:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/build.ps1
```

O script usa a configuração versionada `alien-invasion.spec` e o PyInstaller instalado pelo uv. Ele recria a pasta `dist\AlienInvasion` e substitui o arquivo `dist\AlienInvasion-win64.zip`. Não guarde arquivos próprios nessa pasta.

## Usar a versão portátil

Extraia todo o conteúdo de `dist\AlienInvasion-win64.zip` para uma pasta e abra `AlienInvasion.exe`. Mantenha o executável junto da pasta `_internal`, que contém o runtime Python, o Pygame, suas bibliotecas e os diretórios `alien_invasion\images` e `alien_invasion\sounds`.

O jogador não precisa instalar Python nem Pygame. Distribua o ZIP inteiro; copiar somente o executável não basta. Os perfis continuam em `%LOCALAPPDATA%\AlienInvasion\profiles.json`, fora da pasta portátil, e permanecem lá mesmo depois de remover a pasta do jogo.

## Instalador

O instalador com Inno Setup fica adiado até os recursos visuais e a jogabilidade estabilizarem. Por enquanto, a distribuição é portátil, em formato de pasta e ZIP.

## Origem dos recursos e licença

Este é um projeto de aprendizado baseado no jogo Invasão Alienígena do livro *Curso Intensivo de Python*. Os efeitos WAV são originais, gerados pelo script `scripts/generate_sounds.py`.

As imagens existentes são recursos usados no projeto de estudo. Este repositório não declara direitos sobre os recursos do livro; consulte a origem e os termos de cada recurso antes de redistribuí-los. Não há uma licença geral declarada neste repositório.
