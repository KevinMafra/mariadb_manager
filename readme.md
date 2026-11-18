# MariaDB Manager

Gerenciador desktop para uma instância **portátil do MariaDB** no Windows. A aplicação oferece uma interface gráfica simples (CustomTkinter) para iniciar, parar, verificar atualizações e restaurar o banco de dados sem precisar digitar comandos no terminal.

## Funcionalidades

- **Start**: inicializa o banco (caso ainda não exista) e inicia o servidor `mariadbd.exe`.
- **Shutdown**: encerra o servidor com `mariadb-admin.exe ... shutdown`.
- **Check update**: executa `mysql_upgrade.exe` para verificar/atualizar a instalação.
- **Reset database**: remove o diretório de dados e as chaves de acesso após confirmação explícita digitando `DELETE`.
- **Status em tempo real**: indicador colorido com os estados `starting`, `online`, `stopping`, `offline`, `updating` e `reseting`.
- **Saída do terminal**: painel com a saída do processo do MariaDB, atualizado em uma thread separada.
- **Encerramento seguro**: ao fechar a janela, o aplicativo tenta desligar o servidor antes de sair.

## Requisitos

- **Windows** (o projeto depende de `powershell.exe` e dos binários `.exe` incluídos).
- **Python 3.x** (testado com Python 3.14).
- Dependências Python:
  - `customtkinter`
  - `pillow` (Pillow)
  - Opcional: `mariadb` (conector, presente no ambiente virtual)

> Os binários do MariaDB já estão incluídos no projeto, não sendo necessária uma instalação separada do servidor.

## Instalação

```powershell
# 1. Clone/copie o projeto e entre na pasta
cd mariadb_manager

# 2. Crie e ative um ambiente virtual (opcional, mas recomendado)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 3. Instale as dependências
pip install customtkinter pillow

# 4. Execute a aplicação
python app.py
```

## Primeira execução

Na primeira inicialização o aplicativo:

1. Extrai o arquivo `assets/mariadb.zip` para a pasta `mariadb/` (caso ela não exista).
2. Gera uma senha aleatória para o usuário `root` com `secrets.token_hex(8)` (16 caracteres hexadecimais).
3. Executa `mysql_install_db.exe -p<senha>` para criar o diretório de dados em `mariadb/data`.
4. Salva a senha nos arquivos `mariadb/hex_key.txt` e `mariadb/passwd_key.txt`.

⚠️ **Importante:** a senha do `root` fica armazenada em texto puro nesses dois arquivos. Não os compartilhe e não os versione em um repositório público.

## Como usar

| Ação | Descrição |
|------|-----------|
| **Start** | Inicia o servidor. Se o banco não existir, cria a estrutura de dados primeiro. |
| **Shutdown** | Para o servidor somente quando ele estiver `online`. |
| **Check update** | Executa a verificação de atualização com o banco online. |
| **Reset database** | Abre um campo de confirmação; digite `DELETE` e pressione `Enter` para apagar `mariadb/data` e os arquivos de chave. |

O status é verificado via PowerShell (`Get-Process mariadbd` + `Get-NetTCPConnection`). O painel de texto exibe a saída do processo em tempo real.

## Estrutura do projeto

```text
mariadb_manager/
├── app.py                     # Interface gráfica (CustomTkinter)
├── mariadb_controller.py      # Controle do servidor: status, start, stop, update, reset
├── config.py                  # Caminho raiz do projeto (Path(__file__).parent)
├── assets/
│   ├── mariadb.zip            # Distribuição portátil do MariaDB
│   ├── icon.ico               # Ícone da aplicação
│   ├── mariadb_manager.svg    # Fonte do ícone
│   └── check_update.png       # Ícone do botão de atualização
├── mariadb/                   # Instalação portátil (bin/, data/, share/, lib/)
│   ├── hex_key.txt            # Chave/senha gerada na instalação
│   ├── passwd_key.txt         # Senha usada pelo controle
│   ├── COPYING / THIRDPARTY   # Licenças do MariaDB
│   └── README.md              # Documentação oficial do MariaDB
├── DOCUMENTATION/
│   ├── mariadb parameters.txt # Comandos úteis do MariaDB
│   ├── powershell.txt         # Anotações sobre comandos PowerShell
│   └── icon_gen.py            # Gerador do ícone .ico (requer Inkscape)
└── readme.md                  # Este arquivo
```

## Gerando o ícone

O arquivo `assets/icon.ico` pode ser regerado a partir do SVG com o script auxiliar (é necessário ter o Inkscape instalado em `C:\Program Files\Inkscape\bin\inkscape.exe`):

```powershell
python DOCUMENTATION\icon_gen.py
```

## Observações

- O arquivo `mariadb/data/my.ini` contém caminhos absolutos configurados no ambiente de desenvolvimento. Se o projeto for movido, atualize as diretivas `datadir` e `plugin-dir`.
- O botão de reset é destrutivo: ele remove **todos** os dados do banco e as chaves de acesso. A nova senha será gerada apenas na próxima inicialização.
- O projeto é voltado exclusivamente para Windows devido ao uso de PowerShell e executáveis `.exe`.

## Licença

O código desta aplicação não possui uma licença declarada. A distribuição portátil do MariaDB incluída em `mariadb/` é licenciada sob **GPLv2** (consulte `mariadb/COPYING` e `mariadb/THIRDPARTY`).