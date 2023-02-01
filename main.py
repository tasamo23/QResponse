import qr_gen
import qr_config
import qr_export as Export
import interaction as Input
import qr_display as Display

currentConfiguration = {}

print("\nInitializing...\n")

allCodeConfigurations = Input.loadAllConfigurations()

Display.initialize()

program_mode = Input.initPrompt()

print(program_mode)
