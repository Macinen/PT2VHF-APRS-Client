# Windows 7 Legacy

O PT2VHF APRS Client mantém um build separado para **Windows 7 SP1 x64**.

## Por que existe um build separado

A edição moderna usa Python 3.12 e Microsoft Edge WebView2, componentes que não são adequados ao Windows 7. O build Legacy preserva o mesmo código funcional do cliente, mas usa uma cadeia de empacotamento compatível e abre a interface no navegador padrão.

## Runtime Legacy

- Python 3.8.10 x64.
- PyInstaller 5.13.2.
- Waitress 3.0.0.
- Pillow 10.4.0.
- psutil 6.1.1.
- Sem dependência de pywebview/WebView2.
- Interface servida pelo backend local Flask/Waitress e aberta no navegador padrão.

## Artefatos

- `PT2VHF_APRS_Client_Setup_Win7_Legacy_x64_v<versão>.exe`
- `PT2VHF_APRS_Client_Win7_Legacy_Portable_x64_v<versão>.exe`

O instalador Legacy usa identidade separada da instalação moderna, evitando substituição acidental.

## Atualizações

O build Legacy possui canal próprio. Uma instalação Win7 Legacy procura exclusivamente os assets Legacy da mesma versão e nunca baixa automaticamente um executável Windows moderno.

## Requisitos e limites

- Mínimo: **Windows 7 SP1 x64**.
- Windows 8/8.1 x64 podem utilizar o mesmo build Legacy quando necessário.
- Windows Vista e Windows XP não são suportados.
- É necessário um navegador capaz de executar a interface HTML/CSS/JavaScript do cliente. Internet Explorer 11 não é alvo suportado.
- Acesso Web pela LAN continua desligado por padrão; quando habilitado, pode exigir liberação da porta no Firewall do Windows.

## Validação

Antes da incorporação ao pipeline de produção, o build Legacy v1.14.24 foi executado com sucesso em uma máquina Windows 7 real, eliminando a falha `api-ms-win-core-path-l1-1-0.dll`.
