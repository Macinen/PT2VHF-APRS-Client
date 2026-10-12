# Windows 7 Legacy

O PT2VHF APRS Client mantém um build separado para **Windows 7 SP1 x64**.

## Por que existe um build separado

A edição moderna usa Python 3.12 e componentes recentes. O build Legacy preserva o mesmo código funcional do cliente, mas usa uma cadeia isolada compatível com Windows 7 e inicia em **janela desktop**, sem forçar o navegador externo.

## Runtime Legacy

- Python 3.8.10 x64.
- PyInstaller 5.13.2.
- Waitress 3.0.0.
- Pillow 10.4.0.
- psutil 6.1.1.
- pywebview 4.4.1.
- pythonnet 3.0.3.
- O modo `--browser` permanece disponível apenas para diagnóstico/uso explícito.

## Artefatos

- `PT2VHF_APRS_Client_Setup_Win7_Legacy_x64_v<versão>.exe`
- `PT2VHF_APRS_Client_Win7_Legacy_Portable_x64_v<versão>.exe`

O instalador Legacy usa identidade separada da instalação moderna, evitando substituição acidental.

## Atualizações

O build Legacy possui canal próprio. Setup e Portable procuram exclusivamente os assets Legacy correspondentes. O Portable substitui o executável no mesmo caminho, preserva backup para rollback e relança a nova versão. O Setup baixa e executa somente o instalador Legacy.

## Web LAN

- O acesso LAN continua opt-in.
- Quando habilitado, o servidor faz bind para a LAN e o cabeçalho exibe o IPv4 utilizável, nunca `0.0.0.0`.
- Clicar no endereço abre o URL no navegador padrão; há ação separada para copiar.
- No Windows, a Configuração oferece autorização explícita para criar uma regra TCP no Windows Firewall limitada ao perfil **Privado** e à porta efetiva.
- O aplicativo não desabilita firewall/antivírus e não configura UPnP/port-forwarding.

## Requisitos e limites

- Mínimo: **Windows 7 SP1 x64**.
- Windows 8/8.1 x64 podem utilizar o build Legacy quando necessário.
- Windows Vista e Windows XP não são suportados.
- A shell integrada depende de um renderer Web compatível disponível no sistema; falhas são diagnosticadas e o navegador externo não é aberto silenciosamente como comportamento padrão.

## Validação

O build Legacy original foi validado em máquina Windows 7 real. A v1.14.26 adiciona regressões específicas para janela desktop, updater Setup/Portable, seleção de assets Legacy e Web LAN.
