# ESP32-S3 Flash Example

## Erase flash

esptool.py --chip esp32s3 --port /dev/ttyACM0 erase_flash

## Flash firmware
esptool.py --chip esp32s3 --port /dev/ttyACM0 write_flash -z 0 firmware.bin

Power Cycle device 
