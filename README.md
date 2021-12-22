
# ST7789 Driver for MicroPython

# MicroPython的ST7789驱动程序

This driver is based on [devbis' st7789_mpy driver.](https://github.com/devbis/st7789_mpy)

此驱动程序基于[devbis' st7789_mpy driver.](https://github.com/devbis/st7789_mpy)

I modified the original driver for one of my projects to add:

我修改了我的一个项目的原始驱动程序，以添加：
- Display Rotation.
- 显示旋转。
- Scrolling
- 滚动
- Writing text using bitmaps converted from True Type fonts
- 使用从True Type字体转换的位图写入文本
- Drawing text using 8 and 16 bit wide bitmap fonts
- 使用8位和16位宽位图字体绘制文本
- Drawing text using Hershey vector fonts
- 使用Hershey vector字体绘制文本
- Drawing JPG's, including a SLOW mode to draw jpg's larger than available ram
- 绘制JPG，包括绘制JPG大于可用ram的慢速模式
  using the TJpgDec - Tiny JPEG Decompressor R0.01d. from
  使用TJpgDec-微型JPEG解压器R0。01d。从…起
  http://elm-chan.org/fsw/tjpgd/00index.html
- Drawing and rotating Polygons and filled Polygons.
- 绘制和旋转多边形以及填充多边形。
- Tracking bounds
- 跟踪边界
- Support for st7735 displays
- 支持st7735显示器

Included are 12 bitmap fonts derived from classic pc text mode fonts, 26
Hershey vector fonts and several example programs for different devices.

包括12种源于经典pc文本模式字体的位图字体、26种Hershey vector字体以及用于不同设备的几个示例程序。

## Display Configuration

## 显示配置

Some displays may use a BGR color order or iverted colors. The `cfg_helper.py` program can use used to determine the color order, inversion_mode, colstart, and rowstart values needed for a display.

某些显示器可能使用BGR颜色顺序或分散颜色。`cfg_helper.py`程序可用于确定显示所需的颜色顺序、反转模式、colstart和rowstart值。

### Color Modes

### 颜色模式

You can test the color order needed by a display by filling the display with the `st7789.RED` color and observing the color displayed.

通过使用`st7789.RED`颜色填充显示器并观察显示的颜色，可以测试显示器所需的颜色顺序。
  - If the display is RED, the settings are correct.
  - 如果显示为红色，则设置正确
  - If the display is BLUE, `color_order` should be `st7789.BGR`.
  - 如果显示为蓝色，`color_order`颜色顺序应为`st7789.BGR`。
  - If the display is YELLOW, `inversion_mode` should be `True`.
  - 如果显示为黄色，`inversion_mode` 反转模式应为 `True`。
  - If the display is CYAN, `color_order` should be `st7789.BGR` and `inversion_mode` should be `True`.
  - 如果显示为青色，`color_order`颜色顺序应为`st7789.BGR`，而`inversion_mode`反转模式应为`True`。

### colstart and rowstart

Some displays have a frame buffer memory larger than the physical LCD or LED matrix. In these cases the driver must be configured with the position of the first physcial column and row pixels relative to the frame buffer.  Each rotation setting of the display may require different colstart and rowstart values.

某些显示器的帧缓冲存储器大于物理LCD或LED矩阵。在这些情况下，必须为驱动程序配置第一个物理列和行像素相对于帧缓冲区的位置。显示器的每个旋转设置可能需要不同的colstart和rowstart值。

The driver automatically adjusts the colstart and rowstarts values for common 135x240, 240x240 and 240x320 displays. These values can be overridden using the `offsets` method if the default values do not work for your display. The `offsets` method  should be called after any calls of the `rotation` method.

驱动程序会自动调整常用135x240、240x240和240x320显示器的colstart和rowstarts值。如果默认值不适用于您的显示，则可以使用`offsets`（偏移量）方法覆盖这些值。应在调用`rotation`方法之后调用`offsets`方法。

#### 128x128 st7735 cfg_helper.py example

```
inversion_mode(False)
color_order = st7789.BGR
for rotation 0 use offset(2, 1)
for rotation 1 use offset(1, 2)
for rotation 2 use offset(2, 3)
for rotation 3 use offset(3, 2)
```

#### 128x160 st7735 cfg_helper.py example

```
inversion_mode(False)
color_order = st7789.RGB
for rotation 0 use offset(0, 0)
for rotation 1 use offset(0, 0)
for rotation 2 use offset(0, 0)
for rotation 3 use offset(0, 0)
```

## Pre-compiled firmware files

## 预编译固件文件

The firmware directory contains pre-compiled firmware for various devices with
the st7789 C driver and frozen python font files. See the README.md file in the
fonts folder for more information on the font files.

MicroPython v1.17-231-g0892ebe09 compiled with ESP IDF v4.2 using CMake

固件目录包含各种设备的预编译固件，其中包含st7789 C驱动程序和固化的python字体文件。有关字体文件的详细信息，请参阅字体文件夹中的README.md文件。

使用CMake使用ESP IDF v4.2编译的MicroPython v1.17-231-g0892ebe09

Directory             | File         | Device
--------------------- | ------------ | ----------------------------------
GENERIC-7789          | firmware.bin | Generic ESP32 devices
GENERIC_SPIRAM-7789   | firmware.bin | Generic ESP32 devices with SPI Ram
PYBV11                | firmware.dfu | Pyboard v1.1
RP2                   | firmware.uf2 | Raspberry Pi Pico RP2040
T-DISPLAY             | firmware.bin | LILYGO® TTGO T-Display
T-Watch-2020          | firmware.bin | LILYGO® T-Watch 2020

## Additional Modules

## 附加模块

Module             | Source
------------------ | -----------------------------------------------------------
axp202c            | https://github.com/lewisxhe/AXP202X_Libraries
focaltouch         | https://gitlab.com/mooond/t-watch2020-esp32-with-micropython

## Video Examples

## 视频示例

Example               | Video
--------------------- | -----------------------------------------------------------
PYBV11 hello.py       | https://youtu.be/OtcERmad5ps
PYBV11 scroll.py      | https://youtu.be/ro13rvaLKAc
T-DISPLAY fonts.py    | https://youtu.be/2cnAhEucPD4
T-DISPLAY hello.py    | https://youtu.be/z41Du4GDMSY
T-DISPLAY scroll.py   | https://youtu.be/GQa-RzHLBak
T-DISPLAY roids.py    | https://youtu.be/JV5fPactSPU
TWATCH-2020 draw.py   | https://youtu.be/O_lDBnvH1Sw
TWATCH-2020 hello.py  | https://youtu.be/Bwq39tuMoY4
TWATCH-2020 bitmap.py | https://youtu.be/DgYzgnAW2d8
TWATCH-2020 watch.py  | https://youtu.be/NItKb6umMc4

This is a work in progress.

这是一项正在进行的工作。

## Thanks go out to:

## 致谢：

- https://github.com/devbis for the original driver this is based on.
- 基于此原始驱动程序。
- https://github.com/hklang10 for letting me know of the new mp_raise_ValueError().
- 让我知道新的 mp_raise_ValueError().
- https://github.com/aleggon for finding the correct offsets for a 240x240
  display and discovering issues compiling for STM32 based boards.
- 查找240x240显示器的正确偏移量，并发现基于STM32的板的编译问题。
-- Russ

## Overview

## 概述

This is a driver for MicroPython to handle cheap displays based on the ST7789
chip.

这是MicroPython基于ST7789芯片的廉价显示器的驱动程序。

<p align="center">
  <img src="https://raw.githubusercontent.com/russhughes/st7789_mpy/master/docs/ST7789.jpg" alt="ST7789 display photo"/>
</p>

The driver is written in C. Firmware is provided for ESP32, ESP32 with SPIRAM,
pyboard1.1, and Raspberry Pi Pico devices.

驱动程序是用C编写的。为ESP32，带有SPIRAM的ESP32、pyboard1.1和Raspberry Pi Pico设备提供固件。


# Setup MicroPython Build Environment in Ubuntu 20.04.2

# 在Ubuntu 20.04.2中设置MicroPython构建环境。

Update and upgrade Ubuntu using apt-get if you are using a new install of Ubuntu or the Windows Subsystem for Linux.

如果您正在使用新安装的Ubuntu或Linux Windows子系统，请使用`apt-get`更新和升级Ubuntu。

```bash
sudo apt-get -y update
sudo apt-get -y upgrade
```

Use apt-get to install the required build tools.

使用apt-get安装所需的构建工具。

```bash
sudo apt-get -y install build-essential libffi-dev git pkg-config cmake virtualenv python3-pip python3-virtualenv
```

Clone the esp-idf SDK repo & install -- this usually takes several minutes

克隆esp idf SDK repo&install--这通常需要几分钟的时间

```bash
git clone --recursive https://github.com/espressif/esp-idf.git
cd esp-idf/
./install.sh
```

Source the esp-idf export.sh script to set the required environment variables. It's important that you source the file and not run it using ./export.sh. You will need to source this file before compiling MicroPython.

获取 esp-idf export.sh 脚本以设置所需的环境变量。 重要的是您获取文件而不是使用 ./export.sh 运行它。 在编译 MicroPython 之前，您需要获取此文件的源代码。

```bash
source export.sh
cd ..
```

Clone the MicroPython repo.

```bash
git clone https://github.com/micropython/micropython.git
```

Clone the st7789 driver repo.

```bash
git clone https://github.com/russhughes/st7789_mpy.git
```

Update the git submodules and compile the micropython cross-compiler

更新git子模块并编译micropython交叉编译器

```bash
cd micropython/
git submodule update --init
cd mpy-cross/
make
cd ..
cd ports/esp32
```

Copy any .py files you want to include in the firmware as frozen python modules to the modules subdirectory in ports/esp32. Be aware there is a limit to the flash space available. You will know you have exceeded this limit if you receive an error message saying the code won't fit in the partition or if your firmware continuously reboots with an error.

将要包含在固件中的任何 .py 文件作为固化的 python 模块复制到端口/esp32 中的模块子目录。 请注意，可用闪存空间是有限的。 如果您收到一条错误消息，指出代码不适合该分区，或者您的固件不断重启并出现错误，您就会知道您已超出此限制。 

For example:

```bash
cp ../../../st7789_mpy/fonts/bitmap/vga1_16x16.py modules
cp ../../../st7789_mpy/fonts/truetype/NotoSans_32.py modules
cp ../../../st7789_mpy/fonts/vector/scripts.py modules
```

Build the MicroPython firmware with the driver and frozen .py files in the modules directory. If you did not add any .py files to the modules directory you can leave out the FROZEN_MANIFEST and FROZEN_MPY_DIR settings.

使用模块目录中的驱动程序和固化的 .py 文件构建 MicroPython 固件。 如果您没有将任何 .py 文件添加到模块目录中，您可以省略 FROZEN_MANIFEST 和 FROZEN_MPY_DIR 设置。 

```bash
make USER_C_MODULES=../../../../st7789_mpy/st7789/micropython.cmake FROZEN_MANIFEST="" FROZEN_MPY_DIR=$UPYDIR/modules
```

Erase and flash the firmware to your device. Set PORT= to the ESP32's usb serial port. I could not get the usb serial port to work under the Windows Subsystem (WSL2) for Linux. If you have the same issue you can copy the firmware.bin file and use the Windows esptool.py to flash your device.

擦除和烧录固件到您的设备。 将 PORT= 设置为 ESP32 的 USB 串口。 我无法让 USB 串行端口在适用于 Linux 的 Windows 子系统 (WSL2) 下工作。 如果您遇到同样的问题，您可以复制 firmware.bin 文件并使用 Windows esptool.py 来烧录您的设备。 

```bash
make USER_C_MODULES=../../../../st7789_mpy/st7789/micropython.cmake PORT=/dev/ttyUSB0 erase
make USER_C_MODULES=../../../../st7789_mpy/st7789/micropython.cmake PORT=/dev/ttyUSB0 deploy
```

The firmware.bin file will be in the build-GENERIC directory. To flash using the python esptool.py utility. Use pip3 to install the esptool if it's not already installed.

firmware.bin 文件将位于 build-GENERIC 目录中。 使用 python esptool.py 烧录。 如果尚未安装 esptool，请使用 pip3 安装它。 

```bash
pip3 install esptool
```

Set PORT= to the ESP32's usb serial port

设置 PORT= 为 ESP32 的 USB 串口 

```bash
esptool.py --port COM3 erase_flash
esptool.py --chip esp32 --port COM3 write_flash -z 0x1000 firmware.bin
```
## CMake building instructions for MicroPython 1.14 and later

## MicroPython 1.14 及更高版本的 CMake 构建说明 

for ESP32:

    $ cd micropython/ports/esp32

And then compile the module with specified USER_C_MODULES dir

然后使用指定的 USER_C_MODULES 目录编译模块 

    $ make USER_C_MODULES=../../../../st7789_mpy/st7789/micropython.cmake

for Raspberry Pi PICO:

    $ cd micropython/ports/rp2

And then compile the module with specified USER_C_MODULES dir

然后使用指定的 USER_C_MODULES 目录编译模块 

    $ make USER_C_MODULES=../../../st7789_mpy/st7789/micropython.cmake

## Working examples

## 工作示例

This module was tested on ESP32, STM32 based pyboard v1.1 and the Raspberry Pi
Pico. You have to provide a `SPI` object and the pin to use for the `dc' input of the screen.

该模块在 ESP32、基于 STM32 的 pyboard v1.1 和 Raspberry Pi Pico 上进行了测试。 您必须提供一个`SPI`对象和用于屏幕`dc`输入的引脚。 

    # ESP32

    import machine
    import st7789
    spi = machine.SPI(2, baudrate=40000000, polarity=1, sck=machine.Pin(18), mosi=machine.Pin(23))
    display = st7789.ST7789(spi, 240, 240, reset=machine.Pin(4, machine.Pin.OUT), dc=machine.Pin(2, machine.Pin.OUT))
    display.init()


I was not able to run the display with a baud rate over 40MHZ.

我无法以超过 40MHZ 的波特率运行显示器。

## Methods

## 方法 

- `st7789.ST7789(spi, width, height, dc, reset, cs, backlight, rotation, color_order, buffer_size)`

    ### Required positional arguments:
    ### 必要的位置参数： 
    - `spi` spi device 
    - `spi` SPI设备 
    - `width` display width
    - `width` 显示宽度
    - `height` display height
    - `height` 显示高度 
    
    ### Required keyword arguments:
    ### 必需的关键字参数： 
    - `dc` sets the pin connected to the display data/command selection input. This parameter is always required.
    - `dc` 设置连接到显示数据/命令选择输入的引脚。 此参数始终是必需的。 

    ### Optional keyword arguments:
    ### 可选的关键字参数： 

    - `reset` sets the pin connected to the displays hardware reset input. If the displays reset pin is tied high the `reset` parameter is not required.
    - `reset` 设置连接到显示器硬件复位输入的引脚。 如果显示器复位引脚被拉高，则不需要`reset`参数。 

    - `cs` sets the pin connected to the displays chip select input. If the displays CS pin is tied low, the display must be the only device connected to the SPI port. The display will always be the selected device and the `cs` parameter is not required.
    - `cs` 设置连接到显示器芯片选择输入的引脚。如果显示器 CS 引脚被拉低，则显示器必须是唯一连接到 SPI 端口的设备。显示器将始终是选定的设备，不需要 `cs` 参数。

    - `backlight` sets the pin connected to the displays backlight enable input. The displays backlight input can often be left floating or disconnected as the backlight on some displays are always powered on and cannot be turned off.
    - `backlight` 设置连接到显示器背光启用输入的引脚。由于某些显示器上的背光始终处于开启状态且无法关闭，因此显示器背光输入通常会悬空或断开连接。

    - `rotation` 0-0 degrees, 1-90 degrees, 2-180 degrees, 3-270 degrees
    - `旋转` 0-0 度、1-90 度、2-180 度、3-270 度

    - `color_order` set the color order used by the driver st7789.RGB and st7789.BGR are supported.
    - `color_order` 设置驱动程序使用的颜色顺序，支持st7789.RGB 和 st7789.BGR 。

    - `buffer_size` If a buffer_size is not specified a dynamically allocated buffer is created and freed as needed. If a buffer_size is specified it must be large enough to contain the largest bitmap, font character and/or decoded JPG image used (Rows * Columns * 2 bytes, 16bit colors in RGB565 notation). Dynamic allocation is slower and can cause heap fragmentation so garbage collection (GC) should be enabled.
    - `buffer_size` 如果没有指定buffer_size，则根据需要创建和释放动态分配的缓冲区。如果指定了 buffer_size，它必须足够大以包含所使用的最大位图、字体字符和/或解码的 JPG 图像（行 * 列 * 2 字节，RGB565 表示法中的 16 位颜色）。动态分配速度较慢，可能会导致堆碎片，因此应启用垃圾回收 (GC)。 

- `inversion_mode(bool)` Sets the display color inversion mode if True,
   clears the display color inversion mode if false.
- `inversion_mode(bool)` 如果为 True，则设置显示颜色反转模式，
    如果为 false，则清除显示颜色反转模式。

- `madctl(value)` Returns the current value of the MADCTL register.
   Optionally sets the MADCTL register if a value is passed to the method.
- `madctl(value)` 返回 MADCTL 寄存器的当前值。如果将值传递给此方法，则可选择设置 MADCTL 寄存器。 

  Constant Name    | Value | Description
  ---------------- | ----- | ----------------------
  st7789.MADCTL_MY | 0x80  | Page Address Order
  st7789_MADCTL_MX | 0x40  | Column Address Order
  st7789_MADCTL_MV | 0x20  | Page/Column Order
  st7789_MADCTL_ML | 0x10  | Line Address Order
  st7789_MADCTL_MH | 0x04  | Display Data Latch Order
  st7789_RGB       | 0x00  | RGB color order
  st7789_BGR       | 0x08  | BGR color order

  常数名称 | 值 | 描述
   ---------------- | ----- | ---------------
   st7789.MADCTL_MY | 0x80 | 页面地址顺序
   st7789_MADCTL_MX | 0x40 | 列地址顺序
   st7789_MADCTL_MV | 0x20 | 页/列顺序
   st7789_MADCTL_ML | 0x10 | 线路地址顺序
   st7789_MADCTL_MH | 0x04 | 显示数据锁存顺序
   st7789_RGB | 0x00 | RGB 颜色顺序
   st7789_BGR | 0x08 | BGR颜色顺序 



- `on()`

  Turn on the backlight pin if one was defined during init.
  如果在初始化期间定义了背光引脚，则打开背光引脚。

- `off()`

  Turn off the backlight pin if one was defined during init.
  如果在 init 期间定义了背光引脚，则关闭背光引脚。

- `pixel(x, y, color)`

  Set the specified pixel to the given `color`.
  将指定像素设置为给定的`color`。

- `line(x0, y0, x1, y1, color)`

  Draws a single line with the provided `color` from (`x0`, `y0`) to (`x1`, `y1`).
  使用提供的 `color`从 (`x0`, `y0`) 到（`x1`，`y1`） 绘制一条线。

- `hline(x, y, length, color)`

  Draws a single horizontal line with the provided `color` and `length`
  in pixels. Along with `vline`, this is a fast version with reduced
  number of SPI calls.
  使用提供的`color`和`length`以像素为单位绘制一条水平线。 与 `vline` 一起，这是一个快速版本，减少了 SPI 调用的数量。 

- `vline(x, y, length, color)`

  Draws a single horizontal line with the provided `color` and `length`
  in pixels.
  使用提供的`color`和`length`以像素为单位绘制一条水平线。 

- `rect(x, y, width, height, color)`

  Draws a rectangle from (`x`, `y`) with corresponding dimensions
  从具有相应尺寸的 (`x`, `y`) 绘制一个矩形

- `fill_rect(x, y, width, height, color)`

  Fill a rectangle starting from (`x`, `y`) coordinates
  填充从 (`x`, `y`) 坐标开始的矩形

- `circle(x, y, r, color)`

  Draws a circle with radius `r` centered at the (`x`, `y`) coordinates in the given
  `color`.

- `fill_circle(x, y, r, color)`

  Draws a filled circle with radius `r` centered at the (`x`, `y`) coordinates in the given `color`.
  绘制一个半径为 r 的实心圆，以给定的颜色中的 (`x`, `y`) 坐标为圆心。 

- `blit_buffer(buffer, x, y, width, height)`

  Copy bytes() or bytearray() content to the screen internal memory.
  Note: every color requires 2 bytes in the array
  将 bytes() 或 bytearray() 内容复制到屏幕内部存储器中。
  注意：每种颜色在数组中需要 2 个字节 

- `text(font, s, x, y[, fg, bg])`

  Write text to the display using the specified bitmap `font` with the
  coordinates as the upper-left corner of the text. The foreground and
  background colors of the text can be set by the optional arguments `fg` and
  `bg`, otherwise the foreground color defaults to `WHITE` and the background
  color defaults to `BLACK`.  See the `README.md` in the `fonts/bitmap`
  directory for example fonts.

- `write(bitmap_font, s, x, y[, fg, bg, background_tuple, fill_flag])`

  Write text to the display using the specified proportional or Monospace bitmap
  font module with the coordinates as the upper-left corner of the text. The
  foreground and background colors of the text can be set by the optional
  arguments `fg` and `bg`, otherwise the foreground color defaults to `WHITE`
  and the background color defaults to `BLACK`.

  Transparency can be emulated by providing a `background_tuple` containing
  (bitmap_buffer, width, height).  This is the same format used by the jpg_decode
  method. See examples/T-DISPLAY/clock/clock.py for an example.

  See the `README.md` in the `truetype/fonts` directory for example fonts.
  Returns the width of the string as printed in pixels. Accepts UTF8 encoded strings.

  The `font2bitmap` utility creates compatible 1 bit per pixel bitmap modules
  from Proportional or Monospaced True Type fonts. The character size,
  foreground, background colors and the characters to include in the bitmap
  module may be specified as parameters. Use the -h option for details. If you
  specify a buffer_size during the display initialization it must be large
  enough to hold the widest character (HEIGHT * MAX_WIDTH * 2).

- `write_len(bitap_font, s)`

  Returns the width of the string in pixels if printed in the specified font.

- `draw(vector_font, s, x, y[, fg, scale])`

  Draw text to the display using the specified hershey vector font with the
  coordinates as the lower-left corner of the text. The foreground color of the
  text can be set by the optional argument `fg`, otherwise the foreground color
  defaults to `WHITE`. The size of the text can be scaled by specifying a
  `scale` value. The `scale` value must be larger then 0 and can be a floating
  point or an integer value. The `scale` value defaults to 1.0. See the
  README.md in the `vector/fonts` directory for example fonts and the utils
  directory for a font conversion program.

- `jpg(jpg_filename, x, y [, method])`

  Draw JPG file on the display at the given `x` and `y` coordinates as the upper
  left corner of the image. There memory required to decode and display a JPG
  can be considerable as a full screen 320x240 JPG would require at least 3100
  bytes for the working area + 320 * 240 * 2 bytes of ram to buffer the image.
  Jpg images that would require a buffer larger than available memory can be drawn
  by passing `SLOW` for method. The `SLOW` method will draw the image a piece
  at a time using the Minimum Coded Unit (MCU, typically a multiple of 8x8)
  of the image.

- `jpg_decode(jpg_filename [, x, y, width, height])`

  Decode a jpg file and return it or a portion of it as a tuple composed of
  (buffer, width, height). The buffer is a color565 blit_buffer compatible byte
  array. The buffer will require width * height * 2 bytes of memory.

  If the optional x, y, width and height parameters are given the buffer will
  only contain the specified area of the image. See examples/T-DISPLAY/clock/clock.py
  examples/T-DISPLAY/toasters_jpg/toasters_jpg.py for examples.

- `polygon_center(polygon)`

   Return the center of the `polygon` as an (x, y) tuple. The `polygon` should
   consist of a list of (x, y) tuples forming a closed convex polygon.

- `fill_polygon(polygon, x, y, color[, angle, center_x, center_y])`

  Draw a filled `polygon` at the `x`, `y` coordinates in the `color` given.
  The polygon may be rotated `angle` radians about the `center_x` and
  `center_y` point. The polygon should consist of a list of (x, y) tuples
  forming a closed convex polygon.

  See the TWATCH-2020 `watch.py` demo for an example.

- `polygon(polygon, x, y, color, angle, center_x, center_y)`

  Draw a `polygon` at the `x`, `y` coordinates in the `color` given. The polygon
  may be rotated `angle` radians a bout the `center_x` and `center_y` point.
  The polygon should consist of a list of (x, y) tuples forming a closed
  convex polygon.

  See the T-Display `roids.py` for an example.

- `bounding([status])`

  Bounding turns on and off tracking the area of the display that has been
  written to. Initially tracking is disabled, pass a True value to enable
  tracking and False to disable. Passing a True or False parameter will reset
  the current bounding rectangle to (display_width, display_height, 0, 0).

  Returns a four integer tuple containing (min_x, min_y, max_x, max_y) indicating
  the area of the display that has been written to since the last clearing.

  See the TWATCH-2020 `watch.py` demo for an example.

- `bitmap(bitmap, x , y [, index])`

  Draw `bitmap` using the specified `x`, `y` coordinates as the upper-left
  corner of the of the `bitmap`. The optional `index` parameter provides a
  method to select from multiple bitmaps contained a `bitmap` module. The
  `index` is used to calculate the offset to the beginning of the desired bitmap
  using the modules HEIGHT, WIDTH and BPP values.

  The `imgtobitmap.py` utility creates compatible 1 to 8 bit per pixel bitmap modules
  from image files using the Pillow Python Imaging Library.

  The `monofont2bitmap.py` utility creates compatible 1 to 8 bit per pixel
  bitmap modules from Monospaced True Type fonts. See the `inconsolata_16.py`,
  `inconsolata_32.py` and `inconsolata_64.py` files in the `examples/lib` folder
  for sample modules and the `mono_font.py` program for an example using the
  generated modules.

  The character sizes, bit per pixel, foreground, background
  colors and the characters to include in the bitmap module may be specified as
  parameters. Use the -h option for details. Bits per pixel settings larger than
  one may be used to create antialiased characters at the expense of memory use.
  If you specify a buffer_size during the display initialization it must be
  large enough to hold the one character (HEIGHT * WIDTH * 2).

- `width()`

  Returns the current logical width of the display. (ie a 135x240 display
  rotated 90 degrees is 240 pixels wide)

- `height()`

  Returns the current logical height of the display. (ie a 135x240 display
  rotated 90 degrees is 135 pixels high)

- `rotation(r)`

  Set the rotates the logical display in a clockwise direction. 0-Portrait
  (0 degrees), 1-Landscape (90 degrees), 2-Inverse Portrait (180 degrees),
  3-Inverse Landscape (270 degrees)

- `offset(x_start, y_start)` The memory in the ST7789 controller is
  configured for a 240x320 display. When using a smaller display like a
  240x240 or 135x240 an offset needs to added to the x and y parameters so
  that the pixels are written to the memory area that corresponds to the
  visible display.  The offsets may need to be adjusted when rotating the
  display.

  For example the TTGO-TDisplay is 135x240 and uses the following offsets.
  | Rotation | x_start | y_start |
  |----------|---------|---------|
  | 0        | 52      | 40      |
  | 1        | 40      | 53      |
  | 2        | 53      | 40      |
  | 3        | 40      | 52      |

  When the rotation method is called the driver will adjust the offsets for a
  135x240 or 240x240 display. Your display may require using different offset
  values, if so, use the `offset` method after `rotation` to set the offset
  values.

  The values needed for particular display may not be documented and may
  require some experimentation to determine the correct values. One technique
  is to draw a box the same size as the display and then make small changes
  to the offsets until the display looks correct. See the `cfg_helper.py` program
  in the examples folder for more information.


The module exposes predefined colors:
  `BLACK`, `BLUE`, `RED`, `GREEN`, `CYAN`, `MAGENTA`, `YELLOW`, and `WHITE`


## Helper functions

- `color565(r, g, b)`

  Pack a color into 2-bytes rgb565 format

- `map_bitarray_to_rgb565(bitarray, buffer, width, color=WHITE, bg_color=BLACK)`

  Convert a `bitarray` to the rgb565 color `buffer` that is suitable for blitting.
  Bit 1 in `bitarray` is a pixel with `color` and 0 - with `bg_color`.

  This is a helper with a good performance to print text with a high
  resolution font. You can use an awesome tool
  https://github.com/peterhinch/micropython-font-to-py
  to generate a bitmap fonts from .ttf and use them as a frozen bytecode from
  the ROM memory.
