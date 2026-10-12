# Windows 7 Legacy

O PT2VHF APRS Client mantém um build separado para **Windows 7 SP1 x64**.

## Arquitetura da edição Legacy

A edição moderna usa Python 3.12 e WebView2. O Windows 7 usa uma cadeia isolada, baseada em Python 3.8.10 e PyInstaller 5.13.2.

A partir da v1.14.27, a edição Legacy **não empacota pywebview/pythonnet**. Essa pilha foi removida após a v1.14.26 fechar imediatamente em Windows 7 real, embora o build passasse no runner do GitHub.

## Janela da aplicação

O backend Flask/Waitress continua rodando dentro do executável PT2VHF. Para apresentar a interface:

1. o cliente procura Google Chrome, Chromium ou Brave compatível;
2. quando encontra, abre o navegador em **modo app** (`--app=http://127.0.0.1:porta`), sem abas nem barra de endereço;
3. o processo principal do PT2VHF continua ativo na bandeja;
4. se nenhum navegador compatível for encontrado, abre o navegador padrão como fallback, mas **não encerra o backend**.

O fallback é diagnosticado e não é tratado como falha silenciosa.

## Runtime Legacy

- Python 3.8.10 x64;
- PyInstaller 5.13.2;
- Flask 3.0.3;
- Waitress 3.0.0;
- Pillow 10.4.0;
- psutil 6.1.1;
- sem pywebview/pythonnet no executável Legacy.

## Artefatos

- `PT2VHF_APRS_Client_Setup_Win7_Legacy_x64_v<versão>.exe`
- `PT2VHF_APRS_Client_Win7_Legacy_Portable_x64_v<versão>.exe`

## Atualização integrada

O build Legacy possui canal próprio:

- Portable procura apenas `PT2VHF_APRS_Client_Win7_Legacy_Portable_x64_vX.Y.Z.exe`;
- Setup procura apenas `PT2VHF_APRS_Client_Setup_Win7_Legacy_x64_vX.Y.Z.exe`;
- o Portable é substituído no mesmo caminho, com backup/rollback;
- nenhuma edição moderna de Windows é aplicada automaticamente ao Windows 7.

## Proteção contra versão antiga no Setup

A v1.14.27 adiciona três barreiras:

- o instalador encerra processos Legacy antigos, inclusive Portable versionado;
- o pipeline limpa todos os diretórios de build antes de recompilar;
- o Setup é instalado em pasta temporária no CI e o executável instalado precisa reportar a mesma versão da Release através de `--write-version`.

Isso impede que um executável residual de uma versão anterior seja incluído ou lançado por engano.

## Web LAN

- acesso LAN permanece opt-in;
- o cabeçalho exibe o IPv4 LAN utilizável e a porta efetiva;
- clicar no endereço abre o URL; copiar permanece em ação separada;
- regra de firewall do Windows só é criada após confirmação explícita e limitada ao perfil Privado;
- não há UPnP/port-forwarding automático.

## Requisitos

- mínimo: **Windows 7 SP1 x64**;
- Windows Vista e XP não são suportados;
- para a janela dedicada, recomenda-se um Chrome/Chromium/Brave ainda funcional no Windows 7;
- sem navegador compatível, o modo fallback usa o navegador padrão.

## Validação

O primeiro build Legacy sem dependência de APIs modernas foi validado em Windows 7 real. A v1.14.27 acrescenta validação automática de versão do Portable e do executável realmente instalado pelo Setup. A validação final de comportamento gráfico continua dependendo de teste em Windows 7 real.
