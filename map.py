import evdev
from evdev import InputDevice, uinput, ecodes as e

# Localiza os dispositivos de entrada
devices = [InputDevice(path) for path in evdev.list_devices()]

print("\n--- DISPOSITIVOS ENCONTRADOS ---")
for i, device in enumerate(devices):
    print(f"[{i}] Caminho: {device.path} | Nome: {device.name}")
print("--------------------------------\n")

try:
    opcao = int(input("Digite o número do seu controle: "))
    target = devices[opcao].path
except (ValueError, IndexError):
    print("Opção inválida!")
    exit()

dev = InputDevice(target)

# Sequestra o controle físico para o Chrome só ouvir o virtual puro oficial
try:
    dev.grab()
    print(f"\n[OK] Controle físico ocultado com sucesso!")
    print("[FINALIZADO] Tudo 100% calibrado. Boa jogada!\n")
except IOError:
    print("[ERRO] Rode o script usando 'sudo'.")
    exit()

# Máscara perfeita de um controle de Xbox 360 oficial de fábrica
cap = {
    e.EV_KEY: [
        e.BTN_SOUTH, e.BTN_EAST, e.BTN_WEST, e.BTN_NORTH, 
        e.BTN_TL, e.BTN_TR, e.BTN_SELECT, e.BTN_START, 
        e.BTN_THUMBL, e.BTN_THUMBR
    ],
    e.EV_ABS: [
        (e.ABS_X, evdev.AbsInfo(value=0, min=-32768, max=32767, fuzz=16, flat=128, resolution=0)),  # LS X
        (e.ABS_Y, evdev.AbsInfo(value=0, min=-32768, max=32767, fuzz=16, flat=128, resolution=0)),  # LS Y
        (e.ABS_Z, evdev.AbsInfo(value=0, min=0, max=255, fuzz=0, flat=0, resolution=0)),            # LT
        (e.ABS_RX, evdev.AbsInfo(value=0, min=-32768, max=32767, fuzz=16, flat=128, resolution=0)), # RS X
        (e.ABS_RY, evdev.AbsInfo(value=0, min=-32768, max=32767, fuzz=16, flat=128, resolution=0)), # RS Y
        (e.ABS_RZ, evdev.AbsInfo(value=0, min=0, max=255, fuzz=0, flat=0, resolution=0)),           # RT
        (e.ABS_HAT0X, evdev.AbsInfo(value=0, min=-1, max=1, fuzz=0, flat=0, resolution=0)),         # D-Pad X
        (e.ABS_HAT0Y, evdev.AbsInfo(value=0, min=-1, max=1, fuzz=0, flat=0, resolution=0))          # D-Pad Y
    ]
}

observed_bounds = {}

def scale_axis_dynamic(val, code):
    if code not in observed_bounds:
        observed_bounds[code] = [val, val]
    else:
        if val < observed_bounds[code][0]: observed_bounds[code][0] = val
        if val > observed_bounds[code][1]: observed_bounds[code][1] = val
    
    amin, amax = observed_bounds[code]
    if amax == amin:
        return 0
    
    percentage = float(val - amin) / float(amax - amin)
    return int(-32768 + (percentage * 65535))

# Criamos o barramento virtual mascarado com as IDs legítimas da Microsoft
with uinput.UInput(cap, name="Microsoft X-Box 360 pad", vendor=0x045e, product=0x028e) as ui:
    for event in dev.read_loop():
        
        # MAPEAMENTO DOS ANALÓGICOS (AUTO-CALIBRÁVEIS)
        if event.type == e.EV_ABS:
            if event.code == 0:
                ui.write(e.EV_ABS, e.ABS_X, scale_axis_dynamic(event.value, 0))
            elif event.code == 1:
                ui.write(e.EV_ABS, e.ABS_Y, scale_axis_dynamic(event.value, 1))
            elif event.code == 2:  # RS X
                ui.write(e.EV_ABS, e.ABS_RX, scale_axis_dynamic(event.value, 2))
            elif event.code in [3, 4, 5]:  # RS Y Inteligente
                ui.write(e.EV_ABS, e.ABS_RY, scale_axis_dynamic(event.value, event.code))
            elif event.code == 16:
                ui.write(e.EV_ABS, e.ABS_HAT0X, event.value)
            elif event.code == 17:
                ui.write(e.EV_ABS, e.ABS_HAT0Y, event.value)
                
        # MAPEAMENTO DOS BOTÕES (COM DESINVERSÃO DO X E Y) 
        elif event.type == e.EV_KEY:
            if event.code == e.BTN_SOUTH:    ui.write(e.EV_KEY, e.BTN_SOUTH, event.value) # A
            elif event.code == e.BTN_EAST:   ui.write(e.EV_KEY, e.BTN_EAST, event.value)  # B
            
            # Ajuste definitivo: mandando cada um direto para sua respectiva ID padrão Xbox
            elif event.code == e.BTN_NORTH:  ui.write(e.EV_KEY, e.BTN_NORTH, event.value) # X físico vai como X real
            elif event.code == e.BTN_WEST:   ui.write(e.EV_KEY, e.BTN_WEST, event.value)  # Y físico vai como Y real
            
            elif event.code == e.BTN_TL:     ui.write(e.EV_KEY, e.BTN_TL, event.value)    # LB
            elif event.code == e.BTN_TR:     ui.write(e.EV_KEY, e.BTN_TR, event.value)    # RB
            elif event.code == e.BTN_SELECT: ui.write(e.EV_KEY, e.BTN_SELECT, event.value)
            elif event.code == e.BTN_START:  ui.write(e.EV_KEY, e.BTN_START, event.value)
            elif event.code == e.BTN_THUMBL: ui.write(e.EV_KEY, e.BTN_THUMBR, event.value) # L3 
            elif event.code == e.BTN_THUMBR: ui.write(e.EV_KEY, e.BTN_THUMBL, event.value) # R3 
            
            # Gatilhos puros nos eixos analógicos do Xbox
            elif event.code == e.BTN_TL2:    # LT
                ui.write(e.EV_ABS, e.ABS_Z, 255 if event.value == 1 else 0)
            elif event.code == e.BTN_TR2:    # RT
                ui.write(e.EV_ABS, e.ABS_RZ, 255 if event.value == 1 else 0)
                
        ui.syn()