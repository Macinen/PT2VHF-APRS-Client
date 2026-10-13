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
- o endereço Web no cabeçalho é informativo; use o endereço IPv4 real e a porta efetiva para outros dispositivos;
- regra de firewall exige UAC explícito e limita a porta TCP efetiva à sub-rede local (`LocalSubnet`), sem exposição à Internet;
- não há UPnP/port-forwarding automático.

## Requisitos

- mínimo: **Windows 7 SP1 x64**;
- Windows Vista e XP não são suportados;
- para a janela dedicada, recomenda-se um Chrome/Chromium/Brave ainda funcional no Windows 7;
- sem navegador compatível, o modo fallback usa o navegador padrão.

## Validação

O primeiro build Legacy sem dependência de APIs modernas foi validado em Windows 7 real. A v1.14.27 acrescenta validação automática de versão do Portable e do executável realmente instalado pelo Setup. O pipeline v1.14.32 verifica HTTP real do servidor usando Python 3.8 em runner Windows. Isso não comprova a interface gráfica, popup transitório ou compartilhamento LAN em Windows 7 real, que continuam dependentes de teste físico.

## Alterações a partir da v1.14.33

- Instalações novas ativam Web LAN por padrão, mas não abrem uma aba adicional no navegador por causa dessa opção. O modo janela do navegador no Win7 Legacy continua necessário para a interface principal.
- Se o servidor LAN responder no IPv4 local, a janela Chrome/Chromium/Brave Legacy passa a abri-lo usando o IP da rede e a porta efetiva; em caso de ausência/falha, utiliza localhost.
- O ícone do executável, da bandeja e dos atalhos agora inclui letras **APRS** de maior contraste.
- A presença de usuários remotos pode destacar o IP do cabeçalho em laranja com texto preto. A presença requer heartbeat e expira automaticamente.
- Regra de firewall continua sujeita ao UAC, restrita à sub-rede local. Não habilitar acesso pela Internet.

## v1.14.34 — atualizador e bandeja

- O Portable passa a verificar a prontidão da nova instância após a atualização e tenta recuperar a cópia anterior caso o novo processo não inicie. Atualizadores de versões antigas não têm essa proteção.
- O ícone da área de notificação agora é desenhado com fundo sólido e texto APRS contrastante. Sua legibilidade real no Windows 7 ainda requer teste físico.
- O painel de Mensagens agendadas é exibido em popup, com editores sob demanda e funcionamento independente do serviço de envio.
- Não confundir esse modal com a janela nativa breve do Windows 7, ainda em investigação.
