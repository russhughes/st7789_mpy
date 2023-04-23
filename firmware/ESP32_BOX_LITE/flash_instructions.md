# Flashing firmware

## ESP32

### Erase flash

esptool.py --chip esp32 --port /dev/ttyACM0 erase_flash

### Flash firmware
esptool.py --chip esp32 --port /dev/ttyACM0 write_flash -z 0x1000 firmware.bin

Power Cycle device


## ESP32-S3

Place device unto flash mode by pressing and holding the BOOT button, then
pressing and releasing the RESET button and finally releasing the BOOT button.

### Erase flash

esptool.py --chip esp32s3 --port /dev/ttyACM0 erase_flash

### Flash firmware
esptool.py --chip esp32s3 --port /dev/ttyACM0 write_flash -z 0 firmware.bin

Power Cycle device
