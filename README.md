# Mapeador de controle
Este projeto resolve de forma definitiva o problema de controles sem fio (especialmente os que usam Dongle 2.4Ghz, como o Machenike G5 Pro, Flydigi, Vader, etc.) que ficam com os botões invertidos, gatilhos digitais bugados ou analógicos travados/sem alcance total no Linux (Fedora, Ubuntu, Arch, etc.).

O script intercepta o sinal bruto do seu hardware, oculta o controle problemático para evitar comandos duplos (Double Input) e cria um Controle Virtual Oficial de Xbox 360 direto no Kernel do Linux. Isso garante compatibilidade de 100% com o Google
Chrome (Xbox Cloud Gaming/xCloud), Steam e emuladores.

----
## Funcionalidades atuais: O script intercepta o sinal bruto do seu hardware, oculta o controle físico problemático para evitar comandos duplos (Double Input) e cria um controle virtual oficial de xbox 360 direto no Kernel.

Fedora / RedHat / CentOS
```
sudo dnf install python3-evdev -y
```
Ubuntu / Debian / Mint
```
sudo apt install python3-evdev -y
```
Arch Linux / Manjaro
```
sudo pacman -S python-evdev --noconfirm
```
----
## Como Executar
Por segurança, o Linux bloqueia o acesso direto à leitura de hardware bruto para usuários comuns. Por isso, o script deve ser executado com privilégios de administrador (sudo):
```
sudo python3 map.py
```
----
## Como identificar o seu controle na lista?

Quando você rodar o script, ele vai cuspir uma lista de todos os dispositivos de entrada conectados na máquina. Para saber qual número escolher:

* Pelo nome de fábrica: Procure pelo nome da sua marca ou modelo (Ex: MACHENIKE G5Pro).

* Por palavras-chave: Procure por linhas contendo Gamepad, Controller, Joystick ou Wireless Device.

* O truque de tirar e colocar: Rode o script com o dongle desplugado, plugue-o no USB e rode de novo. O número novo que apareceu é o seu controle!

! DICA CRUCIAL !: Assim que você digitar o número e o script mostrar a mensagem [RUNNING], pegue o seu controle e gire os dois analógicos fazendo círculos completos 2 ou 3 vezes. Isso calibra o alcance máximo de 100% da borda automaticamente!

Se não quiser usar sudo toda vez que for jogar, dê permissão permanente para o seu usuário gerenciar o módulo uinput. Cole estes comandos no terminal uma única vez
```
echo 'KERNEL=="uinput", MODE="0660", GROUP="input"' | sudo tee /etc/udev/rules.d/99-uinput.rules
sudo usermod -aG input $USER
```
Depois de executar, reinicie o computador e você poderá rodar apenas com python3 map.py.

----

O projeto pretende evoluir mais. As próximas metas são:

* Correção de eixos e inversão de botões para o Machenike G5 Pro. ✓

* Interface gráfica (GUI) simplificada para remapeamento visual.

* Criação de um serviço de inicialização automática (systemd service) ao espetar o dongle.
