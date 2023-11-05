/*
 * Modifications and additions Copyright (c) 2020, 2021 Russ Hughes
 *
 * This file licensed under the MIT License and incorporates work covered by
 * the following copyright and permission notice:
 *
 * The MIT License (MIT)
 *
 * Copyright (c) 2019 Ivan Belokobylskiy
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 */

#define __ST7789_VERSION__ "0.2.1"
#include <stdlib.h>
#include <math.h>
#include <stdio.h>
#include <string.h>
#include "py/obj.h"
#include "py/objstr.h"
#include "py/objmodule.h"
#include "py/runtime.h"
#include "py/builtin.h"
#include "py/mphal.h"

// Fix for MicroPython > 1.21 https://github.com/ricksorensen
#if MICROPY_VERSION_MAJOR >= 1 && MICROPY_VERSION_MINOR > 21
#include "extmod/modmachine.h"
#else
#include "extmod/machine_spi.h"
#endif

#include "mpfile.h"
#include "st7789.h"
#include "jpg/tjpgd565.h"
#include "png/pngle.h"

#define _swap_int16_t(a, b) { int16_t t = a; a = b; b = t; }
#define _swap_bytes(val) ((((val) >> 8) & 0x00FF) | (((val) << 8) & 0xFF00))

#define ABS(N) (((N) < 0) ? (-(N)) : (N))
#define mp_hal_delay_ms(delay) (mp_hal_delay_us(delay * 1000))

// GPIO_NUM_NC is not defined in all ports, you may have to change this to
// a different value or type depending on your port. This works for esp32,
// stm32, and the samd ports that I've tested.

#ifndef GPIO_NUM_NC
  #ifdef  STM32_HAL_H
    #define GPIO_NUM_NC NULL
  #else
    #define GPIO_NUM_NC -1
  #endif
#endif

#define CS_LOW()                       \
{                                      \
    if (self->cs != GPIO_NUM_NC) {     \
        mp_hal_pin_write(self->cs, 0); \
    }                                  \
}

#define CS_HIGH()                      \
{                                      \
    if (self->cs != GPIO_NUM_NC) {     \
        mp_hal_pin_write(self->cs, 1); \
    }                                  \
}

#define DC_LOW() (mp_hal_pin_write(self->dc, 0))
#define DC_HIGH() (mp_hal_pin_write(self->dc, 1))

#define RESET_LOW()                         \
{                                           \
    if (self->reset != GPIO_NUM_NC) {       \
        mp_hal_pin_write(self->reset, 0);   \
    }                                       \
}

#define RESET_HIGH()                        \
{                                           \
    if (self->reset != GPIO_NUM_NC) {       \
        mp_hal_pin_write(self->reset, 1);   \
    }                                       \
}

//
// Default st7789 and st7735 display orientation tables
// can be overridden during init(), madctl values
// will be combined with color_mode
//

// { madctl, width, height, colstart, rowstart }

st7789_rotation_t ORIENTATIONS_240x320[4] = {
    {0x00, 240, 320, 0, 0},
    {0x60, 320, 240, 0, 0},
    {0xc0, 240, 320, 0, 0},
    {0xa0, 320, 240, 0, 0}
};

st7789_rotation_t ORIENTATIONS_170x320[4] = {
    {0x00, 170, 320, 35, 0},
    {0x60, 320, 170, 0, 35},
    {0xc0, 170, 320, 35, 0},
    {0xa0, 320, 170, 0, 35}
};

st7789_rotation_t ORIENTATIONS_240x240[4] = {
    {0x00, 240, 240, 0, 0},
    {0x60, 240, 240, 0, 0},
    {0xc0, 240, 240, 0, 80},
    {0xa0, 240, 240, 80, 0}
};

st7789_rotation_t ORIENTATIONS_135x240[4] = {
    {0x00, 135, 240, 52, 40},
    {0x60, 240, 135, 40, 53},
    {0xc0, 135, 240, 53, 40},
    {0xa0, 240, 135, 40, 52}
};

st7789_rotation_t ORIENTATIONS_128x160[4] = {
    {0x00, 128, 160, 0, 0},
    {0x60, 160, 128, 0, 0},
    {0xc0, 128, 160, 0, 0},
    {0xa0, 160, 128, 0, 0}
};

st7789_rotation_t ORIENTATIONS_80x160[4] = {
    {0x00, 80, 160, 26, 1},
    {0x60, 160, 80, 1, 26},
    {0xc0, 80, 160, 26, 1},
    {0xa0, 160, 80, 1, 26}
};

st7789_rotation_t ORIENTATIONS_128x128[4] = {
    {0x00, 128, 128, 2, 1},
    {0x60, 128, 128, 1, 2},
    {0xc0, 128, 128, 2, 3},
    {0xa0, 128, 128, 3, 2}
};

STATIC void write_spi(mp_obj_base_t *spi_obj, const uint8_t *buf, int len) {
    #ifdef MP_OBJ_TYPE_GET_SLOT
    mp_machine_spi_p_t *spi_p = (mp_machine_spi_p_t *)MP_OBJ_TYPE_GET_SLOT(spi_obj->type, protocol);
    #else
    mp_machine_spi_p_t *spi_p = (mp_machine_spi_p_t *)spi_obj->type->protocol;
    #endif
    spi_p->transfer(spi_obj, len, buf, NULL);
}

STATIC void st7789_ST7789_print(const mp_print_t *print, mp_obj_t self_in, mp_print_kind_t kind) {
    (void)kind;
    st7789_ST7789_obj_t *self = MP_OBJ_TO_PTR(self_in);
    mp_printf(print, "<ST7789 width=%u, height=%u, spi=%p>", self->width, self->height, self->spi_obj);
}

STATIC void write_cmd(st7789_ST7789_obj_t *self, uint8_t cmd, const uint8_t *data, int len) {
    CS_LOW()
    if (cmd) {
        DC_LOW();
        write_spi(self->spi_obj, &cmd, 1);
    }
    if (len > 0) {
        DC_HIGH();
        write_spi(self->spi_obj, data, len);
    }
    CS_HIGH()
}

STATIC void set_window(st7789_ST7789_obj_t *self, uint16_t x0, uint16_t y0, uint16_t x1, uint16_t y1) {
    if (x0 > x1 || x1 >= self->width) {
        return;
    }
    if (y0 > y1 || y1 >= self->height) {
        return;
    }

    if (self->bounding) {
        if (x0 < self->min_x) {
            self->min_x = x0;
        }
        if (x1 > self->max_x) {
            self->max_x = x1;
        }
        if (y0 < self->min_y) {
            self->min_y = y0;
        }
        if (y1 > self->max_y) {
            self->max_y = y1;
        }
    }

    uint8_t bufx[4] = {(x0 + self->colstart) >> 8, (x0 + self->colstart) & 0xFF, (x1 + self->colstart) >> 8, (x1 + self->colstart) & 0xFF};
    uint8_t bufy[4] = {(y0 + self->rowstart) >> 8, (y0 + self->rowstart) & 0xFF, (y1 + self->rowstart) >> 8, (y1 + self->rowstart) & 0xFF};
    write_cmd(self, ST7789_CASET, bufx, 4);
    write_cmd(self, ST7789_RASET, bufy, 4);
    write_cmd(self, ST7789_RAMWR, NULL, 0);
}

STATIC void fill_color_buffer(mp_obj_base_t *spi_obj, uint16_t color, int length) {
    const int buffer_pixel_size = 128;
    int chunks = length / buffer_pixel_size;
    int rest = length % buffer_pixel_size;
    uint16_t color_swapped = _swap_bytes(color);
    uint16_t buffer[buffer_pixel_size];      // 128 pixels

    // fill buffer with color data

    for (int i = 0; i < length && i < buffer_pixel_size; i++) {
        buffer[i] = color_swapped;
    }
    if (chunks) {
        for (int j = 0; j < chunks; j++) {
            write_spi(spi_obj, (uint8_t *)buffer, buffer_pixel_size * 2);
        }
    }
    if (rest) {
        write_spi(spi_obj, (uint8_t *)buffer, rest * 2);
    }
}

int mod(int x, int m) {
    int r = x % m;
    return (r < 0) ? r + m : r;
}

void draw_pixel(st7789_ST7789_obj_t *self, int16_t x, int16_t y, uint16_t color) {
    if ((self->options & OPTIONS_WRAP)) {
        if ((self->options & OPTIONS_WRAP_H) && ((x >= self->width) || (x < 0))) {
            x = mod(x, self->width);
        }
        if ((self->options & OPTIONS_WRAP_V) && ((y >= self->height) || (y < 0))) {
            y = mod(y, self->height);
        }
    }

    if ((x < self->width) && (y < self->height) && (x >= 0) && (y >= 0)) {
        uint8_t hi = color >> 8, lo = color & 0xff;
        set_window(self, x, y, x, y);
        DC_HIGH();
        CS_LOW();
        write_spi(self->spi_obj, &hi, 1);
        write_spi(self->spi_obj, &lo, 1);
        CS_HIGH();
    }
}

void fast_hline(st7789_ST7789_obj_t *self, int16_t x, int16_t y, int16_t w, uint16_t color) {
    if ((self->options & OPTIONS_WRAP) == 0) {
        if (y >= 0 && self->width > x && self->height > y) {
            if (0 > x) {
                w += x;
                x = 0;
            }

            if (self->width < x + w) {
                w = self->width - x;
            }

            if (w > 0) {
                int16_t x2 = x + w - 1;
                set_window(self, x, y, x2, y);
                DC_HIGH();
                CS_LOW();
                fill_color_buffer(self->spi_obj, color, w);
                CS_HIGH();
            }
        }
    } else {
        for (int d = 0; d < w; d++) {
            draw_pixel(self, x + d, y, color);
        }
    }
}

STATIC void fast_vline(st7789_ST7789_obj_t *self, int16_t x, int16_t y, int16_t h, uint16_t color) {
    if ((self->options & OPTIONS_WRAP) == 0) {
        if (x >= 0 && self->width > x && self->height > y) {
            if (0 > y) {
                h += y;
                y = 0;
            }

            if (self->height < y + h) {
                h = self->height - y;
            }

            if (h > 0) {
                int16_t y2 = y + h - 1;

                set_window(self, x, y, x, y2);
                DC_HIGH();
                CS_LOW();
                fill_color_buffer(self->spi_obj, color, h);
                CS_HIGH();
            }
        }
    } else {
        for (int d = 0; d < h; d++) {
            draw_pixel(self, x, y + d, color);
        }
    }
}

STATIC mp_obj_t st7789_ST7789_hard_reset(mp_obj_t self_in) {
    st7789_ST7789_obj_t *self = MP_OBJ_TO_PTR(self_in);

    CS_LOW();
    RESET_HIGH();
    mp_hal_delay_ms(50);
    RESET_LOW();
    mp_hal_delay_ms(50);
    RESET_HIGH();
    mp_hal_delay_ms(150);
    CS_HIGH();
    return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_1(st7789_ST7789_hard_reset_obj, st7789_ST7789_hard_reset);

STATIC mp_obj_t st7789_ST7789_soft_reset(mp_obj_t self_in) {
    st7789_ST7789_obj_t *self = MP_OBJ_TO_PTR(self_in);

    write_cmd(self, ST7789_SWRESET, NULL, 0);
    mp_hal_delay_ms(150);
    return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_1(st7789_ST7789_soft_reset_obj, st7789_ST7789_soft_reset);

STATIC mp_obj_t st7789_ST7789_sleep_mode(mp_obj_t self_in, mp_obj_t value) {
    st7789_ST7789_obj_t *self = MP_OBJ_TO_PTR(self_in);
    if (mp_obj_is_true(value)) {
        write_cmd(self, ST7789_SLPIN, NULL, 0);
    } else {
        write_cmd(self, ST7789_SLPOUT, NULL, 0);
    }
    return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_2(st7789_ST7789_sleep_mode_obj, st7789_ST7789_sleep_mode);

STATIC mp_obj_t st7789_ST7789_inversion_mode(mp_obj_t self_in, mp_obj_t value) {
    st7789_ST7789_obj_t *self = MP_OBJ_TO_PTR(self_in);

    self->inversion = mp_obj_is_true(value);
    if (self->inversion) {
        write_cmd(self, ST7789_INVON, NULL, 0);
    } else {
        write_cmd(self, ST7789_INVOFF, NULL, 0);
    }
    return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_2(st7789_ST7789_inversion_mode_obj, st7789_ST7789_inversion_mode);

STATIC mp_obj_t st7789_ST7789_fill_rect(size_t n_args, const mp_obj_t *args) {
    st7789_ST7789_obj_t *self = MP_OBJ_TO_PTR(args[0]);
    mp_int_t x = mp_obj_get_int(args[1]);
    mp_int_t y = mp_obj_get_int(args[2]);
    mp_int_t w = mp_obj_get_int(args[3]);
    mp_int_t h = mp_obj_get_int(args[4]);
    mp_int_t color = mp_obj_get_int(args[5]);

    uint16_t right = x + w - 1;
    uint16_t bottom = y + h - 1;

    if (x < self->width && y < self->height) {
        if (right > self->width) {
            right = self->width;
        }

        if (bottom > self->height) {
            bottom = self->height;
        }

        set_window(self, x, y, right, bottom);
        DC_HIGH();
        CS_LOW();
        fill_color_buffer(self->spi_obj, color, w * h);
        CS_HIGH();
    }
    return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(st7789_ST7789_fill_rect_obj, 6, 6, st7789_ST7789_fill_rect);

STATIC mp_obj_t st7789_ST7789_fill(mp_obj_t self_in, mp_obj_t _color) {
    st7789_ST7789_obj_t *self = MP_OBJ_TO_PTR(self_in);
    mp_int_t color = mp_obj_get_int(_color);

    set_window(self, 0, 0, self->width - 1, self->height - 1);
    DC_HIGH();
    CS_LOW();
    fill_color_buffer(self->spi_obj, color, self->width * self->height);
    CS_HIGH();

    return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_2(st7789_ST7789_fill_obj, st7789_ST7789_fill);

STATIC mp_obj_t st7789_ST7789_pixel(size_t n_args, const mp_obj_t *args) {
    st7789_ST7789_obj_t *self = MP_OBJ_TO_PTR(args[0]);
    mp_int_t x = mp_obj_get_int(args[1]);
    mp_int_t y = mp_obj_get_int(args[2]);
    mp_int_t color = mp_obj_get_int(args[3]);

    draw_pixel(self, x, y, color);

    return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(st7789_ST7789_pixel_obj, 4, 4, st7789_ST7789_pixel);

STATIC void line(st7789_ST7789_obj_t *self, int16_t x0, int16_t y0, int16_t x1, int16_t y1, int16_t color) {
    bool steep = ABS(y1 - y0) > ABS(x1 - x0);
    if (steep) {
        _swap_int16_t(x0, y0);
        _swap_int16_t(x1, y1);
    }

    if (x0 > x1) {
        _swap_int16_t(x0, x1);
        _swap_int16_t(y0, y1);
    }

    int16_t dx = x1 - x0, dy = ABS(y1 - y0);
    int16_t err = dx >> 1, ystep = -1, xs = x0, dlen = 0;

    if (y0 < y1) {
        ystep = 1;
    }

    // Split into steep and not steep for FastH/V separation
    if (steep) {
        for (; x0 <= x1; x0++) {
            dlen++;
            err -= dy;
            if (err < 0) {
                err += dx;
                if (dlen == 1) {
                    draw_pixel(self, y0, xs, color);
                } else {
                    fast_vline(self, y0, xs, dlen, color);
                }
                dlen = 0;
                y0 += ystep;
                xs = x0 + 1;
            }
        }
        if (dlen) {
            fast_vline(self, y0, xs, dlen, color);
        }
    } else {
        for (; x0 <= x1; x0++) {
            dlen++;
            err -= dy;
            if (err < 0) {
                err += dx;
                if (dlen == 1) {
                    draw_pixel(self, xs, y0, color);
                } else {
                    fast_hline(self, xs, y0, dlen, color);
                }
                dlen = 0;
                y0 += ystep;
                xs = x0 + 1;
            }
        }
        if (dlen) {
            fast_hline(self, xs, y0, dlen, color);
        }
    }
}

STATIC mp_obj_t st7789_ST7789_line(size_t n_args, const mp_obj_t *args) {
    st7789_ST7789_obj_t *self = MP_OBJ_TO_PTR(args[0]);
    mp_int_t x0 = mp_obj_get_int(args[1]);
    mp_int_t y0 = mp_obj_get_int(args[2]);
    mp_int_t x1 = mp_obj_get_int(args[3]);
    mp_int_t y1 = mp_obj_get_int(args[4]);
    mp_int_t color = mp_obj_get_int(args[5]);

    line(self, x0, y0, x1, y1, color);

    return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(st7789_ST7789_line_obj, 6, 6, st7789_ST7789_line);

STATIC mp_obj_t st7789_ST7789_blit_buffer(size_t n_args, const mp_obj_t *args) {
    st7789_ST7789_obj_t *self = MP_OBJ_TO_PTR(args[0]);
    mp_buffer_info_t buf_info;
    mp_get_buffer_raise(args[1], &buf_info, MP_BUFFER_READ);
    mp_int_t x = mp_obj_get_int(args[2]);
    mp_int_t y = mp_obj_get_int(args[3]);
    mp_int_t w = mp_obj_get_int(args[4]);
    mp_int_t h = mp_obj_get_int(args[5]);

    set_window(self, x, y, x + w - 1, y + h - 1);
    DC_HIGH();
    CS_LOW();

    const int buf_size = 256;
    int limit = MIN(buf_info.len, w * h * 2);
    int chunks = limit / buf_size;
    int rest = limit % buf_size;
    int i = 0;
    for (; i < chunks; i++) {
        write_spi(self->spi_obj, (const uint8_t *)buf_info.buf + i * buf_size, buf_size);
    }
    if (rest) {
        write_spi(self->spi_obj, (const uint8_t *)buf_info.buf + i * buf_size, rest);
    }
    CS_HIGH();

    return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(st7789_ST7789_blit_buffer_obj, 6, 6, st7789_ST7789_blit_buffer);

STATIC mp_obj_t st7789_ST7789_draw(size_t n_args, const mp_obj_t *args) {
    st7789_ST7789_obj_t *self = MP_OBJ_TO_PTR(args[0]);
    char single_char_s[] = {0, 0};
    const char *s;

    mp_obj_module_t *hershey = MP_OBJ_TO_PTR(args[1]);

    if (mp_obj_is_int(args[2])) {
        mp_int_t c = mp_obj_get_int(args[2]);
        single_char_s[0] = c & 0xff;
        s = single_char_s;
    } else {
        s = mp_obj_str_get_str(args[2]);
    }

    mp_int_t x = mp_obj_get_int(args[3]);
    mp_int_t y = mp_obj_get_int(args[4]);

    mp_int_t color = (n_args > 5) ? mp_obj_get_int(args[5]) : WHITE;

    mp_float_t scale = 1.0;
    if (n_args > 6) {
        if (mp_obj_is_float(args[6])) {
            scale = mp_obj_float_get(args[6]);
        }
        if (mp_obj_is_int(args[6])) {
            scale = (mp_float_t)mp_obj_get_int(args[6]);
        }
    }

    mp_obj_dict_t *dict = MP_OBJ_TO_PTR(hershey->globals);
    mp_obj_t *index_data_buff = mp_obj_dict_get(dict, MP_OBJ_NEW_QSTR(MP_QSTR_INDEX));
    mp_buffer_info_t index_bufinfo;
    mp_get_buffer_raise(index_data_buff, &index_bufinfo, MP_BUFFER_READ);
    uint8_t *index = index_bufinfo.buf;

    mp_obj_t *font_data_buff = mp_obj_dict_get(dict, MP_OBJ_NEW_QSTR(MP_QSTR_FONT));
    mp_buffer_info_t font_bufinfo;
    mp_get_buffer_raise(font_data_buff, &font_bufinfo, MP_BUFFER_READ);
    int8_t *font = font_bufinfo.buf;

    int16_t from_x = x;
    int16_t from_y = y;
    int16_t to_x = x;
    int16_t to_y = y;
    int16_t pos_x = x;
    int16_t pos_y = y;
    bool penup = true;
    char c;
    int16_t ii;

    while ((c = *s++)) {
        if (c >= 32 && c <= 127) {
            ii = (c - 32) * 2;

            int16_t offset = index[ii] | (index[ii + 1] << 8);
            int16_t length = font[offset++];
            int16_t left = (int)(scale * (font[offset++] - 0x52) + 0.5);
            int16_t right = (int)(scale * (font[offset++] - 0x52) + 0.5);
            int16_t width = right - left;

            if (length) {
                int16_t i;
                for (i = 0; i < length; i++) {
                    if (font[offset] == ' ') {
                        offset += 2;
                        penup = true;
                        continue;
                    }

                    int16_t vector_x = (int)(scale * (font[offset++] - 0x52) + 0.5);
                    int16_t vector_y = (int)(scale * (font[offset++] - 0x52) + 0.5);

                    if (!i || penup) {
                        from_x = pos_x + vector_x - left;
                        from_y = pos_y + vector_y;
                    } else {
                        to_x = pos_x + vector_x - left;
                        to_y = pos_y + vector_y;

                        line(self, from_x, from_y, to_x, to_y, color);
                        from_x = to_x;
                        from_y = to_y;
                    }
                    penup = false;
                }
            }
            pos_x += width;
        }
    }

    return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(st7789_ST7789_draw_obj, 5, 7, st7789_ST7789_draw);

STATIC mp_obj_t st7789_ST7789_draw_len(size_t n_args, const mp_obj_t *args) {
    char single_char_s[] = {0, 0};
    const char *s;

    mp_obj_module_t *hershey = MP_OBJ_TO_PTR(args[1]);

    if (mp_obj_is_int(args[2])) {
        mp_int_t c = mp_obj_get_int(args[2]);
        single_char_s[0] = c & 0xff;
        s = single_char_s;
    } else {
        s = mp_obj_str_get_str(args[2]);
    }

    mp_float_t scale = 1.0;
    if (n_args > 3) {
        if (mp_obj_is_float(args[3])) {
            scale = mp_obj_float_get(args[3]);
        }
        if (mp_obj_is_int(args[3])) {
            scale = (mp_float_t)mp_obj_get_int(args[3]);
        }
    }

    mp_obj_dict_t *dict = MP_OBJ_TO_PTR(hershey->globals);
    mp_obj_t *index_data_buff = mp_obj_dict_get(dict, MP_OBJ_NEW_QSTR(MP_QSTR_INDEX));
    mp_buffer_info_t index_bufinfo;
    mp_get_buffer_raise(index_data_buff, &index_bufinfo, MP_BUFFER_READ);
    uint8_t *index = index_bufinfo.buf;

    mp_obj_t *font_data_buff = mp_obj_dict_get(dict, MP_OBJ_NEW_QSTR(MP_QSTR_FONT));
    mp_buffer_info_t font_bufinfo;
    mp_get_buffer_raise(font_data_buff, &font_bufinfo, MP_BUFFER_READ);
    int8_t *font = font_bufinfo.buf;

    int16_t print_width = 0;
    char c;
    int16_t ii;

    while ((c = *s++)) {
        if (c >= 32 && c <= 127) {
            ii = (c - 32) * 2;

            int16_t offset = (index[ii] | (index[ii + 1] << 8)) + 1;
            int16_t left =  font[offset++] - 0x52;
            int16_t right = font[offset++] - 0x52;
            int16_t width = right - left;
            print_width += width;
        }
    }

    return mp_obj_new_int((int)(print_width * scale + 0.5));
}
STATIC MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(st7789_ST7789_draw_len_obj, 3, 4, st7789_ST7789_draw_len);

STATIC uint32_t bs_bit = 0;
uint8_t *bitmap_data = NULL;

STATIC uint8_t get_color(uint8_t bpp) {
    uint8_t color = 0;
    int i;

    for (i = 0; i < bpp; i++) {
        color <<= 1;
        color |= (bitmap_data[bs_bit / 8] & 1 << (7 - (bs_bit % 8))) > 0;
        bs_bit++;
    }
    return color;
}

STATIC mp_obj_t dict_lookup(mp_obj_t self_in, mp_obj_t index) {
    mp_obj_dict_t *self = MP_OBJ_TO_PTR(self_in);
    mp_map_elem_t *elem = mp_map_lookup(&self->map, index, MP_MAP_LOOKUP);
    if (elem == NULL) {
        return NULL;
    } else {
        return elem->value;
    }
}

STATIC mp_obj_t st7789_ST7789_write_len(size_t n_args, const mp_obj_t *args) {
    mp_obj_module_t *font = MP_OBJ_TO_PTR(args[1]);
    mp_obj_dict_t *dict = MP_OBJ_TO_PTR(font->globals);
    mp_obj_t widths_data_buff = mp_obj_dict_get(dict, MP_OBJ_NEW_QSTR(MP_QSTR_WIDTHS));
    mp_buffer_info_t widths_bufinfo;
    mp_get_buffer_raise(widths_data_buff, &widths_bufinfo, MP_BUFFER_READ);
    const uint8_t *widths_data = widths_bufinfo.buf;

    uint16_t print_width = 0;

    mp_obj_t map_obj = mp_obj_dict_get(dict, MP_OBJ_NEW_QSTR(MP_QSTR_MAP));
    GET_STR_DATA_LEN(map_obj, map_data, map_len);
    GET_STR_DATA_LEN(args[2], str_data, str_len);
    const byte *s = str_data, *top = str_data + str_len;

    while (s < top) {
        unichar ch;
        ch = utf8_get_char(s);
        s = utf8_next_char(s);

        const byte *map_s = map_data, *map_top = map_data + map_len;
        uint16_t char_index = 0;

        while (map_s < map_top) {
            unichar map_ch;
            map_ch = utf8_get_char(map_s);
            map_s = utf8_next_char(map_s);

            if (ch == map_ch) {
                print_width += widths_data[char_index];
                break;
            }
            char_index++;
        }
    }

    return mp_obj_new_int(print_width);
}
STATIC MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(st7789_ST7789_write_len_obj, 3, 3, st7789_ST7789_write_len);

//
//	write(font_module, s, x, y[, fg, bg, background_tuple, fill])
//		background_tuple (bitmap_buffer, width, height)
//

STATIC mp_obj_t st7789_ST7789_write(size_t n_args, const mp_obj_t *args) {
    st7789_ST7789_obj_t *self = MP_OBJ_TO_PTR(args[0]);
    mp_obj_module_t *font = MP_OBJ_TO_PTR(args[1]);

    mp_int_t x = mp_obj_get_int(args[3]);
    mp_int_t y = mp_obj_get_int(args[4]);
    mp_int_t fg_color;
    mp_int_t bg_color;

    fg_color = (n_args > 5) ? _swap_bytes(mp_obj_get_int(args[5])) : _swap_bytes(WHITE);
    bg_color = (n_args > 6) ? _swap_bytes(mp_obj_get_int(args[6])) : _swap_bytes(BLACK);

    mp_obj_t *tuple_data = NULL;
    size_t tuple_len = 0;

    mp_buffer_info_t background_bufinfo;
    uint16_t background_width = 0;
    uint16_t background_height = 0;
    uint16_t *background_data = NULL;

    if (n_args > 7) {
        mp_obj_tuple_get(args[7], &tuple_len, &tuple_data);
        if (tuple_len > 2) {
            mp_get_buffer_raise(tuple_data[0], &background_bufinfo, MP_BUFFER_READ);
            background_data = background_bufinfo.buf;
            background_width = mp_obj_get_int(tuple_data[1]);
            background_height = mp_obj_get_int(tuple_data[2]);
        }
    }

    bool fill = (n_args > 8) ? mp_obj_is_true(args[8]) : false;

    mp_obj_dict_t *dict = MP_OBJ_TO_PTR(font->globals);
    const uint8_t bpp = mp_obj_get_int(mp_obj_dict_get(dict, MP_OBJ_NEW_QSTR(MP_QSTR_BPP)));
    const uint8_t height = mp_obj_get_int(mp_obj_dict_get(dict, MP_OBJ_NEW_QSTR(MP_QSTR_HEIGHT)));
    const uint8_t offset_width = mp_obj_get_int(mp_obj_dict_get(dict, MP_OBJ_NEW_QSTR(MP_QSTR_OFFSET_WIDTH)));
    const uint8_t max_width = mp_obj_get_int(mp_obj_dict_get(dict, MP_OBJ_NEW_QSTR(MP_QSTR_MAX_WIDTH)));

    mp_obj_t widths_data_buff = mp_obj_dict_get(dict, MP_OBJ_NEW_QSTR(MP_QSTR_WIDTHS));
    mp_buffer_info_t widths_bufinfo;
    mp_get_buffer_raise(widths_data_buff, &widths_bufinfo, MP_BUFFER_READ);
    const uint8_t *widths_data = widths_bufinfo.buf;

    mp_obj_t offsets_data_buff = mp_obj_dict_get(dict, MP_OBJ_NEW_QSTR(MP_QSTR_OFFSETS));
    mp_buffer_info_t offsets_bufinfo;
    mp_get_buffer_raise(offsets_data_buff, &offsets_bufinfo, MP_BUFFER_READ);
    const uint8_t *offsets_data = offsets_bufinfo.buf;

    mp_obj_t bitmaps_data_buff = mp_obj_dict_get(dict, MP_OBJ_NEW_QSTR(MP_QSTR_BITMAPS));
    mp_buffer_info_t bitmaps_bufinfo;
    mp_get_buffer_raise(bitmaps_data_buff, &bitmaps_bufinfo, MP_BUFFER_READ);
    bitmap_data = bitmaps_bufinfo.buf;

    // allocate buffer large enough the the widest character in the font
    // if a buffer was not specified during the driver init.

    size_t buf_size = max_width * height * 2;
    if (self->buffer_size == 0) {
        self->i2c_buffer = m_malloc(buf_size);
    }

    // if fill is set, and background bitmap data is available copy the background
    // bitmap data into the buffer. The background buffer must be the size of the
    // widest character in the font.

    if (fill && background_data && self->i2c_buffer) {
        memcpy(self->i2c_buffer, background_data, background_width * background_height * 2);
    }

    uint16_t print_width = 0;
    mp_obj_t map_obj = mp_obj_dict_get(dict, MP_OBJ_NEW_QSTR(MP_QSTR_MAP));
    GET_STR_DATA_LEN(map_obj, map_data, map_len);
    GET_STR_DATA_LEN(args[2], str_data, str_len);
    const byte *s = str_data, *top = str_data + str_len;
    while (s < top) {
        unichar ch;
        ch = utf8_get_char(s);
        s = utf8_next_char(s);

        const byte *map_s = map_data, *map_top = map_data + map_len;
        uint16_t char_index = 0;

        while (map_s < map_top) {
            unichar map_ch;
            map_ch = utf8_get_char(map_s);
            map_s = utf8_next_char(map_s);

            if (ch == map_ch) {
                uint8_t width = widths_data[char_index];

                bs_bit = 0;
                switch (offset_width) {
                    case 1:
                        bs_bit = offsets_data[char_index * offset_width];
                        break;

                    case 2:
                        bs_bit = (offsets_data[char_index * offset_width] << 8) +
                            (offsets_data[char_index * offset_width + 1]);
                        break;

                    case 3:
                        bs_bit = (offsets_data[char_index * offset_width] << 16) +
                            (offsets_data[char_index * offset_width + 1] << 8) +
                            (offsets_data[char_index * offset_width + 2]);
                        break;
                }

                uint16_t buffer_width = (fill) ? max_width : width;

                uint16_t color = 0;
                for (uint16_t yy = 0; yy < height; yy++) {
                    for (uint16_t xx = 0; xx < width; xx++) {
                        if (background_data && (xx <= background_width && yy <= background_height)) {
                            if (get_color(bpp) == bg_color) {
                                color = background_data[(yy * background_width + xx)];
                            } else {
                                color = fg_color;
                            }
                        } else {
                            color = get_color(bpp) ? fg_color : bg_color;
                        }
                        self->i2c_buffer[yy * buffer_width + xx] = color;
                    }
                }

                uint32_t data_size = buffer_width * height * 2;
                uint16_t x2 = x + buffer_width - 1;
                uint16_t y2 = y + height - 1;
                if (x2 < self->width) {
                    set_window(self, x, y, x2, y2);
                    DC_HIGH();
                    CS_LOW();
                    write_spi(self->spi_obj, (uint8_t *)self->i2c_buffer, data_size);
                    CS_HIGH();
                    print_width += width;
                }
                x += width;
                break;
            }
            char_index++;
        }
    }

    if (self->buffer_size == 0) {
        m_free(self->i2c_buffer);
    }

    return mp_obj_new_int(print_width);
}
STATIC MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(st7789_ST7789_write_obj, 5, 9, st7789_ST7789_write);

STATIC mp_obj_t st7789_ST7789_bitmap(size_t n_args, const mp_obj_t *args) {
    st7789_ST7789_obj_t *self = MP_OBJ_TO_PTR(args[0]);

    mp_obj_module_t *bitmap = MP_OBJ_TO_PTR(args[1]);
    mp_int_t x = mp_obj_get_int(args[2]);
    mp_int_t y = mp_obj_get_int(args[3]);

    mp_int_t idx;
    if (n_args > 4) {
        idx = mp_obj_get_int(args[4]);
    } else {
        idx = 0;
    }

    mp_obj_dict_t *dict = MP_OBJ_TO_PTR(bitmap->globals);
    const uint16_t height = mp_obj_get_int(mp_obj_dict_get(dict, MP_OBJ_NEW_QSTR(MP_QSTR_HEIGHT)));
    const uint16_t width = mp_obj_get_int(mp_obj_dict_get(dict, MP_OBJ_NEW_QSTR(MP_QSTR_WIDTH)));
    uint16_t bitmaps = 0;
    const uint8_t bpp = mp_obj_get_int(mp_obj_dict_get(dict, MP_OBJ_NEW_QSTR(MP_QSTR_BPP)));
    mp_obj_t *palette_arg = mp_obj_dict_get(dict, MP_OBJ_NEW_QSTR(MP_QSTR_PALETTE));
    mp_obj_t *palette = NULL;
    size_t palette_len = 0;

    mp_map_elem_t *elem = dict_lookup(bitmap->globals, MP_OBJ_NEW_QSTR(MP_QSTR_BITMAPS));
    if (elem) {
        bitmaps = mp_obj_get_int(elem);
    }

    mp_obj_get_array(palette_arg, &palette_len, &palette);

    mp_obj_t *bitmap_data_buff = mp_obj_dict_get(dict, MP_OBJ_NEW_QSTR(MP_QSTR_BITMAP));
    mp_buffer_info_t bufinfo;

    mp_get_buffer_raise(bitmap_data_buff, &bufinfo, MP_BUFFER_READ);
    bitmap_data = bufinfo.buf;

    size_t buf_size = width * height * 2;
    if (self->buffer_size == 0) {
        self->i2c_buffer = m_malloc(buf_size);
    }

    size_t ofs = 0;
    bs_bit = 0;
    if (bitmaps) {
        if (idx < bitmaps) {
            bs_bit = height * width * bpp * idx;
        } else {
            mp_raise_msg(&mp_type_OSError, MP_ERROR_TEXT("index out of range"));
        }
    }

    for (int yy = 0; yy < height; yy++) {
        for (int xx = 0; xx < width; xx++) {
            self->i2c_buffer[ofs++] = mp_obj_get_int(palette[get_color(bpp)]);
        }
    }

    uint16_t x1 = x + width - 1;
    if (x1 < self->width) {
        set_window(self, x, y, x1, y + height - 1);
        DC_HIGH();
        CS_LOW();
        write_spi(self->spi_obj, (uint8_t *)self->i2c_buffer, buf_size);
        CS_HIGH();
    }

    if (self->buffer_size == 0) {
        m_free(self->i2c_buffer);
    }
    return mp_const_none;
}

STATIC MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(st7789_ST7789_bitmap_obj, 4, 5, st7789_ST7789_bitmap);

STATIC mp_obj_t st7789_ST7789_text(size_t n_args, const mp_obj_t *args) {
    st7789_ST7789_obj_t *self = MP_OBJ_TO_PTR(args[0]);
    uint8_t single_char_s;
    const uint8_t *source = NULL;
    size_t source_len = 0;

    // extract arguments
    mp_obj_module_t *font = MP_OBJ_TO_PTR(args[1]);

    if (mp_obj_is_int(args[2])) {
        mp_int_t c = mp_obj_get_int(args[2]);
        single_char_s = (c & 0xff);
        source = &single_char_s;
        source_len = 1;
    } else if (mp_obj_is_str(args[2])) {
        source = (uint8_t *) mp_obj_str_get_str(args[2]);
        source_len = strlen((char *)source);
    } else if (mp_obj_is_type(args[2], &mp_type_bytes)) {
        mp_obj_t text_data_buff = args[2];
        mp_buffer_info_t text_bufinfo;
        mp_get_buffer_raise(text_data_buff, &text_bufinfo, MP_BUFFER_READ);
        source = text_bufinfo.buf;
        source_len = text_bufinfo.len;
    } else {
        mp_raise_TypeError(MP_ERROR_TEXT("text requires either int, str or bytes."));
        return mp_const_none;
    }

    mp_int_t x0 = mp_obj_get_int(args[3]);
    mp_int_t y0 = mp_obj_get_int(args[4]);

    mp_obj_dict_t *dict = MP_OBJ_TO_PTR(font->globals);
    const uint8_t width = mp_obj_get_int(mp_obj_dict_get(dict, MP_OBJ_NEW_QSTR(MP_QSTR_WIDTH)));
    const uint8_t height = mp_obj_get_int(mp_obj_dict_get(dict, MP_OBJ_NEW_QSTR(MP_QSTR_HEIGHT)));
    const uint8_t first = mp_obj_get_int(mp_obj_dict_get(dict, MP_OBJ_NEW_QSTR(MP_QSTR_FIRST)));
    const uint8_t last = mp_obj_get_int(mp_obj_dict_get(dict, MP_OBJ_NEW_QSTR(MP_QSTR_LAST)));

    mp_obj_t font_data_buff = mp_obj_dict_get(dict, MP_OBJ_NEW_QSTR(MP_QSTR_FONT));
    mp_buffer_info_t bufinfo;
    mp_get_buffer_raise(font_data_buff, &bufinfo, MP_BUFFER_READ);
    const uint8_t *font_data = bufinfo.buf;

    mp_int_t fg_color;
    mp_int_t bg_color;

    if (n_args > 5) {
        fg_color = _swap_bytes(mp_obj_get_int(args[5]));
    } else {
        fg_color = _swap_bytes(WHITE);
    }

    if (n_args > 6) {
        bg_color = _swap_bytes(mp_obj_get_int(args[6]));
    } else {
        bg_color = _swap_bytes(BLACK);
    }

    uint8_t wide = width / 8;
    size_t buf_size = width * height * 2;

    if (self->buffer_size == 0) {
        self->i2c_buffer = m_malloc(buf_size);
    }

    uint8_t chr;
    if (self->i2c_buffer) {
    while (source_len--) {
        chr = *source++;
            if (chr >= first && chr <= last) {
                uint16_t buf_idx = 0;
                uint16_t chr_idx = (chr - first) * (height * wide);
                for (uint8_t line = 0; line < height; line++) {
                    for (uint8_t line_byte = 0; line_byte < wide; line_byte++) {
                        uint8_t chr_data = font_data[chr_idx];
                        for (uint8_t bit = 8; bit; bit--) {
                            if (chr_data >> (bit - 1) & 1) {
                                self->i2c_buffer[buf_idx] = fg_color;
                            } else {
                                self->i2c_buffer[buf_idx] = bg_color;
                            }
                            buf_idx++;
                        }
                        chr_idx++;
                    }
                }
                uint16_t x1 = x0 + width - 1;
                if (x1 < self->width) {
                    set_window(self, x0, y0, x1, y0 + height - 1);
                    DC_HIGH();
                    CS_LOW();
                    write_spi(self->spi_obj, (uint8_t *)self->i2c_buffer, buf_size);
                    CS_HIGH();
                }
                x0 += width;
            }
        }
        if (self->buffer_size == 0) {
            m_free(self->i2c_buffer);
        }
    }
    return mp_const_none;
}

STATIC MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(st7789_ST7789_text_obj, 5, 7, st7789_ST7789_text);

// 0=Portrait, 1=Landscape, 2=Reverse Portrait (180), 3=Reverse Landscape (180)

STATIC void set_rotation(st7789_ST7789_obj_t *self) {
    uint8_t madctl_value = self->color_order;

    if (self->rotation > self->rotations_len) {
        mp_raise_msg_varg(
            &mp_type_RuntimeError,
            MP_ERROR_TEXT("Invalid rotation value %d > %d"), self->rotation, self->rotations_len);
    }

    st7789_rotation_t *rotations = self->rotations;
    if (rotations == NULL) {
        if (self->display_width == 240 && self->display_height == 320) {
            rotations = ORIENTATIONS_240x320;
        } else if (self->display_width == 170 && self->display_height == 320) {
            rotations = ORIENTATIONS_170x320;
        } else if (self->display_width == 240 && self->display_height == 240) {
            rotations = ORIENTATIONS_240x240;
        } else if (self->display_width == 135 && self->display_height == 240) {
            rotations = ORIENTATIONS_135x240;
        } else if (self->display_width == 128 && self->display_height == 160) {
            rotations = ORIENTATIONS_128x160;
        } else if (self->display_width == 80 && self->display_height == 160) {
            rotations = ORIENTATIONS_80x160;
        } else if (self->display_width == 128 && self->display_height == 128) {
            rotations = ORIENTATIONS_128x128;
        }
    }

    if (rotations) {
        st7789_rotation_t *rotation = &rotations[self->rotation];
        madctl_value |= rotation->madctl;
        self->width = rotation->width;
        self->height = rotation->height;
        self->colstart = rotation->colstart;
        self->rowstart = rotation->rowstart;
    }

    self->madctl = madctl_value & 0xff;
    self->min_x = self->width;
    self->min_y = self->height;
    self->max_x = 0;
    self->max_y = 0;

    const uint8_t madctl[] = {madctl_value};
    write_cmd(self, ST7789_MADCTL, madctl, 1);
}

STATIC mp_obj_t st7789_ST7789_rotation(mp_obj_t self_in, mp_obj_t value) {
    st7789_ST7789_obj_t *self = MP_OBJ_TO_PTR(self_in);
    mp_int_t rotation = mp_obj_get_int(value) % 4;
    self->rotation = rotation;
    set_rotation(self);
    return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_2(st7789_ST7789_rotation_obj, st7789_ST7789_rotation);

STATIC mp_obj_t st7789_ST7789_width(mp_obj_t self_in) {
    st7789_ST7789_obj_t *self = MP_OBJ_TO_PTR(self_in);
    return mp_obj_new_int(self->width);
}
STATIC MP_DEFINE_CONST_FUN_OBJ_1(st7789_ST7789_width_obj, st7789_ST7789_width);

STATIC mp_obj_t st7789_ST7789_height(mp_obj_t self_in) {
    st7789_ST7789_obj_t *self = MP_OBJ_TO_PTR(self_in);
    return mp_obj_new_int(self->height);
}
STATIC MP_DEFINE_CONST_FUN_OBJ_1(st7789_ST7789_height_obj, st7789_ST7789_height);

STATIC mp_obj_t st7789_ST7789_vscrdef(size_t n_args, const mp_obj_t *args) {
    st7789_ST7789_obj_t *self = MP_OBJ_TO_PTR(args[0]);
    mp_int_t tfa = mp_obj_get_int(args[1]);
    mp_int_t vsa = mp_obj_get_int(args[2]);
    mp_int_t bfa = mp_obj_get_int(args[3]);

    uint8_t buf[6] = {(tfa) >> 8, (tfa) & 0xFF, (vsa) >> 8, (vsa) & 0xFF, (bfa) >> 8, (bfa) & 0xFF};
    write_cmd(self, ST7789_VSCRDEF, buf, 6);

    return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(st7789_ST7789_vscrdef_obj, 4, 4, st7789_ST7789_vscrdef);

STATIC mp_obj_t st7789_ST7789_vscsad(mp_obj_t self_in, mp_obj_t vssa_in) {
    st7789_ST7789_obj_t *self = MP_OBJ_TO_PTR(self_in);
    mp_int_t vssa = mp_obj_get_int(vssa_in);

    uint8_t buf[2] = {(vssa) >> 8, (vssa) & 0xFF};
    write_cmd(self, ST7789_VSCSAD, buf, 2);

    return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_2(st7789_ST7789_vscsad_obj, st7789_ST7789_vscsad);

STATIC void custom_init(st7789_ST7789_obj_t *self) {
    size_t init_len;
    mp_obj_t *init_list;

    mp_obj_get_array(self->custom_init, &init_len, &init_list);

    for (int idx = 0; idx < init_len; idx++) {
        size_t init_cmd_len;
        mp_obj_t *init_cmd;
        mp_obj_get_array(init_list[idx], &init_cmd_len, &init_cmd);
        mp_buffer_info_t init_cmd_data_info;
        if (mp_get_buffer(init_cmd[0], &init_cmd_data_info, MP_BUFFER_READ)) {
            uint8_t *init_cmd_data = (uint8_t *)init_cmd_data_info.buf;

            if (init_cmd_data_info.len > 1) {
                write_cmd(self, init_cmd_data[0], &init_cmd_data[1], init_cmd_data_info.len - 1);
            } else {
                write_cmd(self, init_cmd_data[0], NULL, 0);
            }
            mp_hal_delay_ms(10);

            // check for delay
            if (init_cmd_len > 1) {
                mp_int_t delay = mp_obj_get_int(init_cmd[1]);
                if (delay > 0) {
                    mp_hal_delay_ms(delay);
                }
            }
        }
    }
}

STATIC mp_obj_t st7789_ST7789_init(mp_obj_t self_in) {
    st7789_ST7789_obj_t *self = MP_OBJ_TO_PTR(self_in);

    st7789_ST7789_hard_reset(self_in);

    if (self->custom_init == MP_OBJ_NULL) {
        st7789_ST7789_soft_reset(self_in);
        write_cmd(self, ST7789_SLPOUT, NULL, 0);

        const uint8_t color_mode[] = {COLOR_MODE_65K | COLOR_MODE_16BIT};
        write_cmd(self, ST7789_COLMOD, color_mode, 1);
        mp_hal_delay_ms(10);

        if (self->inversion) {
            write_cmd(self, ST7789_INVON, NULL, 0);
        } else {
            write_cmd(self, ST7789_INVOFF, NULL, 0);
        }

        write_cmd(self, ST7789_NORON, NULL, 0);
        mp_hal_delay_ms(10);

        write_cmd(self, ST7789_DISPON, NULL, 0);
        mp_hal_delay_ms(150);

    } else {
        custom_init(self);
    }

    set_rotation(self);
    mp_hal_delay_ms(10);

    const mp_obj_t args[] = {
        self_in,
        mp_obj_new_int(0),
        mp_obj_new_int(0),
        mp_obj_new_int(self->width),
        mp_obj_new_int(self->height),
        mp_obj_new_int(BLACK)
    };

    st7789_ST7789_fill_rect(6, args);

    if (self->backlight != GPIO_NUM_NC) {
        mp_hal_pin_write(self->backlight, 1);
    }

    return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_1(st7789_ST7789_init_obj, st7789_ST7789_init);

STATIC mp_obj_t st7789_ST7789_on(mp_obj_t self_in) {
    st7789_ST7789_obj_t *self = MP_OBJ_TO_PTR(self_in);

    if (self->backlight != GPIO_NUM_NC) {
        mp_hal_pin_write(self->backlight, 1);
        mp_hal_delay_ms(10);
    }

    return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_1(st7789_ST7789_on_obj, st7789_ST7789_on);

STATIC mp_obj_t st7789_ST7789_off(mp_obj_t self_in) {
    st7789_ST7789_obj_t *self = MP_OBJ_TO_PTR(self_in);

    if (self->backlight != GPIO_NUM_NC) {
        mp_hal_pin_write(self->backlight, 0);
        mp_hal_delay_ms(10);
    }

    return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_1(st7789_ST7789_off_obj, st7789_ST7789_off);

STATIC mp_obj_t st7789_ST7789_hline(size_t n_args, const mp_obj_t *args) {
    st7789_ST7789_obj_t *self = MP_OBJ_TO_PTR(args[0]);
    mp_int_t x = mp_obj_get_int(args[1]);
    mp_int_t y = mp_obj_get_int(args[2]);
    mp_int_t w = mp_obj_get_int(args[3]);
    mp_int_t color = mp_obj_get_int(args[4]);

    fast_hline(self, x, y, w, color);

    return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(st7789_ST7789_hline_obj, 5, 5, st7789_ST7789_hline);

STATIC mp_obj_t st7789_ST7789_vline(size_t n_args, const mp_obj_t *args) {
    st7789_ST7789_obj_t *self = MP_OBJ_TO_PTR(args[0]);
    mp_int_t x = mp_obj_get_int(args[1]);
    mp_int_t y = mp_obj_get_int(args[2]);
    mp_int_t w = mp_obj_get_int(args[3]);
    mp_int_t color = mp_obj_get_int(args[4]);

    fast_vline(self, x, y, w, color);

    return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(st7789_ST7789_vline_obj, 5, 5, st7789_ST7789_vline);

// Circle/Fill_Circle by https://github.com/c-logic
// https://github.com/russhughes/st7789_mpy/pull/46
// https://github.com/c-logic/st7789_mpy.git patch-1

STATIC mp_obj_t st7789_ST7789_circle(size_t n_args, const mp_obj_t *args) {
    st7789_ST7789_obj_t *self = MP_OBJ_TO_PTR(args[0]);
    mp_int_t xm = mp_obj_get_int(args[1]);
    mp_int_t ym = mp_obj_get_int(args[2]);
    mp_int_t r = mp_obj_get_int(args[3]);
    mp_int_t color = mp_obj_get_int(args[4]);

    mp_int_t f = 1 - r;
    mp_int_t ddF_x = 1;
    mp_int_t ddF_y = -2 * r;
    mp_int_t x = 0;
    mp_int_t y = r;

    draw_pixel(self, xm, ym + r, color);
    draw_pixel(self, xm, ym - r, color);
    draw_pixel(self, xm + r, ym, color);
    draw_pixel(self, xm - r, ym, color);
    while (x < y) {
        if (f >= 0) {
            y -= 1;
            ddF_y += 2;
            f += ddF_y;
        }
        x += 1;
        ddF_x += 2;
        f += ddF_x;
        draw_pixel(self, xm + x, ym + y, color);
        draw_pixel(self, xm - x, ym + y, color);
        draw_pixel(self, xm + x, ym - y, color);
        draw_pixel(self, xm - x, ym - y, color);
        draw_pixel(self, xm + y, ym + x, color);
        draw_pixel(self, xm - y, ym + x, color);
        draw_pixel(self, xm + y, ym - x, color);
        draw_pixel(self, xm - y, ym - x, color);
    }
    return mp_const_none;
}

STATIC MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(st7789_ST7789_circle_obj, 5, 5, st7789_ST7789_circle);

// Circle/Fill_Circle by https://github.com/c-logic
// https://github.com/russhughes/st7789_mpy/pull/46
// https://github.com/c-logic/st7789_mpy.git patch-1

STATIC mp_obj_t st7789_ST7789_fill_circle(size_t n_args, const mp_obj_t *args) {
    st7789_ST7789_obj_t *self = MP_OBJ_TO_PTR(args[0]);
    mp_int_t xm = mp_obj_get_int(args[1]);
    mp_int_t ym = mp_obj_get_int(args[2]);
    mp_int_t r = mp_obj_get_int(args[3]);
    mp_int_t color = mp_obj_get_int(args[4]);

    mp_int_t f = 1 - r;
    mp_int_t ddF_x = 1;
    mp_int_t ddF_y = -2 * r;
    mp_int_t x = 0;
    mp_int_t y = r;

    fast_vline(self, xm, ym - y, 2 * y + 1, color);

    while (x < y) {
        if (f >= 0) {
            y -= 1;
            ddF_y += 2;
            f += ddF_y;
        }
        x += 1;
        ddF_x += 2;
        f += ddF_x;
        fast_vline(self, xm + x, ym - y, 2 * y + 1, color);
        fast_vline(self, xm + y, ym - x, 2 * x + 1, color);
        fast_vline(self, xm - x, ym - y, 2 * y + 1, color);
        fast_vline(self, xm - y, ym - x, 2 * x + 1, color);
    }
    return mp_const_none;
}

STATIC MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(st7789_ST7789_fill_circle_obj, 5, 5, st7789_ST7789_fill_circle);

STATIC mp_obj_t st7789_ST7789_rect(size_t n_args, const mp_obj_t *args) {
    st7789_ST7789_obj_t *self = MP_OBJ_TO_PTR(args[0]);
    mp_int_t x = mp_obj_get_int(args[1]);
    mp_int_t y = mp_obj_get_int(args[2]);
    mp_int_t w = mp_obj_get_int(args[3]);
    mp_int_t h = mp_obj_get_int(args[4]);
    mp_int_t color = mp_obj_get_int(args[5]);

    fast_hline(self, x, y, w, color);
    fast_vline(self, x, y, h, color);
    fast_hline(self, x, y + h - 1, w, color);
    fast_vline(self, x + w - 1, y, h, color);
    return mp_const_none;
}

STATIC MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(st7789_ST7789_rect_obj, 6, 6, st7789_ST7789_rect);

STATIC mp_obj_t st7789_ST7789_madctl(size_t n_args, const mp_obj_t *args) {
    st7789_ST7789_obj_t *self = MP_OBJ_TO_PTR(args[0]);

    if (n_args == 2) {
        mp_int_t madctl_value = mp_obj_get_int(args[1]) & 0xff;
        const uint8_t madctl[] = {madctl_value};
        write_cmd(self, ST7789_MADCTL, madctl, 1);
        self->madctl = madctl_value & 0xff;
    }
    return mp_obj_new_int(self->madctl);
}

STATIC MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(st7789_ST7789_madctl_obj, 1, 2, st7789_ST7789_madctl);

STATIC mp_obj_t st7789_ST7789_offset(size_t n_args, const mp_obj_t *args) {
    st7789_ST7789_obj_t *self = MP_OBJ_TO_PTR(args[0]);
    mp_int_t colstart = mp_obj_get_int(args[1]);
    mp_int_t rowstart = mp_obj_get_int(args[2]);

    self->colstart = colstart;
    self->rowstart = rowstart;

    return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(st7789_ST7789_offset_obj, 3, 3, st7789_ST7789_offset);

STATIC uint16_t color565(uint8_t r, uint8_t g, uint8_t b) {
    return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | ((b & 0xF8) >> 3);
}

STATIC mp_obj_t st7789_color565(mp_obj_t r, mp_obj_t g, mp_obj_t b) {
    return MP_OBJ_NEW_SMALL_INT(color565(
        (uint8_t)mp_obj_get_int(r),
        (uint8_t)mp_obj_get_int(g),
        (uint8_t)mp_obj_get_int(b)));
}
STATIC MP_DEFINE_CONST_FUN_OBJ_3(st7789_color565_obj, st7789_color565);

STATIC void map_bitarray_to_rgb565(uint8_t const *bitarray, uint8_t *buffer, int length, int width,
    uint16_t color, uint16_t bg_color) {
    int row_pos = 0;
    for (int i = 0; i < length; i++) {
        uint8_t byte = bitarray[i];
        for (int bi = 7; bi >= 0; bi--) {
            uint8_t b = byte & (1 << bi);
            uint16_t cur_color = b ? color : bg_color;
            *buffer = (cur_color & 0xff00) >> 8;
            buffer++;
            *buffer = cur_color & 0xff;
            buffer++;

            row_pos++;
            if (row_pos >= width) {
                row_pos = 0;
                break;
            }
        }
    }
}

STATIC mp_obj_t st7789_map_bitarray_to_rgb565(size_t n_args, const mp_obj_t *args) {
    mp_buffer_info_t bitarray_info;
    mp_buffer_info_t buffer_info;

    mp_get_buffer_raise(args[1], &bitarray_info, MP_BUFFER_READ);
    mp_get_buffer_raise(args[2], &buffer_info, MP_BUFFER_WRITE);
    mp_int_t width = mp_obj_get_int(args[3]);
    mp_int_t color = mp_obj_get_int(args[4]);
    mp_int_t bg_color = mp_obj_get_int(args[5]);
    map_bitarray_to_rgb565(bitarray_info.buf, buffer_info.buf, bitarray_info.len, width, color, bg_color);
    return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(st7789_map_bitarray_to_rgb565_obj, 3, 6, st7789_map_bitarray_to_rgb565);

//
// jpg routines
//

#define JPG_MODE_FAST (0)
#define JPG_MODE_SLOW (1)

// User defined device identifier
typedef struct {
    mp_file_t *fp;              // File pointer for input function
    uint8_t *fbuf;              // Pointer to the frame buffer for output function
    unsigned int wfbuf;         // Width of the frame buffer [pix]
    unsigned int left;          // jpg crop left column
    unsigned int top;           // jpg crop top row
    unsigned int right;         // jpg crop right column
    unsigned int bottom;        // jpg crop bottom row

    st7789_ST7789_obj_t *self;  // display object

    // for buffer input function
    uint8_t *data;
    unsigned int dataIdx;
    unsigned int dataLen;

} IODEV;

static unsigned int buffer_in_func(     // Returns number of bytes read (zero on error)
    JDEC *jd,                           // Decompression object
    uint8_t *buff,                      // Pointer to the read buffer (null to remove data)
    unsigned int nbyte) {               // Number of bytes to read/remove
    IODEV *dev = (IODEV *)jd->device;

    if (dev->dataIdx + nbyte > dev->dataLen) {
        nbyte = dev->dataLen - dev->dataIdx;
    }

    if (buff) {
        memcpy(buff, (uint8_t *)(dev->data + dev->dataIdx), nbyte);
    }

    dev->dataIdx += nbyte;
    return nbyte;
}

//
// file input function
//

static unsigned int file_in_func(       // Returns number of bytes read (zero on error)
    JDEC *jd,                           // Decompression object
    uint8_t *buff,                      // Pointer to the read buffer (null to remove data)
    unsigned int nbyte) {               // Number of bytes to read/remove
    IODEV *dev = (IODEV *)jd->device;   // Device identifier for the session (5th argument of jd_prepare function)
    unsigned int nread;

    // Read data from input stream
    if (buff) {
        nread = (unsigned int)mp_readinto(dev->fp, buff, nbyte);
        return nread;
    }

    // Remove data from input stream if buff was NULL
    mp_seek(dev->fp, nbyte, SEEK_CUR);
    return 0;
}

//
// fast output function
//

static int out_fast(                    // 1:Ok, 0:Aborted
    JDEC *jd,                           // Decompression object
    void *bitmap,                       // Bitmap data to be output
    JRECT *rect) {                      // Rectangular region of output image
    IODEV *dev = (IODEV *)jd->device;
    uint8_t *src, *dst;
    uint16_t y, bws, bwd;

    // Copy the decompressed RGB rectangular to the frame buffer (assuming RGB565)
    src = (uint8_t *)bitmap;
    dst = dev->fbuf + 2 * (rect->top * dev->wfbuf + rect->left);    // Left-top of destination rectangular
    bws = 2 * (rect->right - rect->left + 1);                       // Width of source rectangular [byte]
    bwd = 2 * dev->wfbuf;                                           // Width of frame buffer [byte]
    for (y = rect->top; y <= rect->bottom; y++) {
        memcpy(dst, src, bws);                                      // Copy a line
        src += bws;
        dst += bwd;                                                 // Next line
    }

    return 1;     // Continue to decompress
}

//
// Slow output function: draw each
//

static int out_slow(                                    // 1:Ok, 0:Aborted
    JDEC *jd,                                           // Decompression object
    void *bitmap,                                       // Bitmap data to be output
    JRECT *rect) {                                      // Rectangular region of output image
    IODEV *dev = (IODEV *)jd->device;
    st7789_ST7789_obj_t *self = dev->self;

    uint8_t *src, *dst;
    uint16_t y;
    uint16_t wx2 = (rect->right - rect->left + 1) * 2;
    uint16_t h = rect->bottom - rect->top + 1;

    // Copy the decompressed RGB rectangular to the frame buffer (assuming RGB565)
    src = (uint8_t *)bitmap;
    dst = dev->fbuf;                                    // Left-top of destination rectangular
    for (y = rect->top; y <= rect->bottom; y++) {
        memcpy(dst, src, wx2);                          // Copy a line
        src += wx2;
        dst += wx2;                                     // Next line
    }

    // blit buffer to display

    set_window(
        self,
        rect->left + jd->x_offs,
        rect->top + jd->y_offs,
        rect->right + jd->x_offs,
        rect->bottom + jd->y_offs);

    DC_HIGH();
    CS_LOW();
    write_spi(self->spi_obj, (uint8_t *)dev->fbuf, wx2 * h);
    CS_HIGH();

    return 1;     // Continue to decompress
}

//
// Draw jpg from a file at x, y using a fast mode or slow mode
//

STATIC mp_obj_t st7789_ST7789_jpg(size_t n_args, const mp_obj_t *args) {
    st7789_ST7789_obj_t *self = MP_OBJ_TO_PTR(args[0]);
    static unsigned int (*input_func)(JDEC *, uint8_t *, unsigned int) = NULL;
    mp_buffer_info_t bufinfo;
    IODEV devid;

    if (mp_obj_is_type(args[1], &mp_type_bytes)) {
        mp_get_buffer_raise(args[1], &bufinfo, MP_BUFFER_READ);
        devid.dataIdx = 0;
        devid.data = bufinfo.buf;
        devid.dataLen = bufinfo.len;
        input_func = buffer_in_func;
        self->fp = MP_OBJ_NULL;
    } else {
        const char *filename = mp_obj_str_get_str(args[1]);
        self->fp = mp_open(filename, "rb");
        devid.fp = self->fp;
        input_func = file_in_func;
        devid.data = MP_OBJ_NULL;
        devid.dataLen = 0;
    }

    mp_int_t x = mp_obj_get_int(args[2]);
    mp_int_t y = mp_obj_get_int(args[3]);

    mp_int_t mode;

    if (n_args > 4) {
        mode = mp_obj_get_int(args[4]);
    } else {
        mode = JPG_MODE_FAST;
    }

    int (*outfunc)(JDEC *, void *, JRECT *);

    JRESULT res;                                // Result code of TJpgDec API
    JDEC jdec;                                  // Decompression object
    self->work = (void *)m_malloc(3100);        // Pointer to the work area
    size_t bufsize;

    if (input_func && (devid.fp || devid.data)) {
        // Prepare to decompress
        res = jd_prepare(&jdec, input_func, self->work, 3100, &devid);
        if (res == JDR_OK) {
            // Initialize output device
            if (mode == JPG_MODE_FAST) {
                bufsize = 2 * jdec.width * jdec.height;
                outfunc = out_fast;
            } else {
                bufsize = 2 * jdec.msx * 8 * jdec.msy * 8;
                outfunc = out_slow;
                jdec.x_offs = x;
                jdec.y_offs = y;
            }
            if (self->buffer_size && (bufsize > self->buffer_size)) {
                mp_raise_msg_varg(&mp_type_OSError, MP_ERROR_TEXT("buffer too small. %ld bytes required."), (long)bufsize);
            }

            if (self->buffer_size == 0) {
                self->i2c_buffer = m_malloc(bufsize);
            }

            if (!self->i2c_buffer) {
                mp_raise_msg(&mp_type_OSError, MP_ERROR_TEXT("out of memory"));
            }

            devid.fbuf = (uint8_t *)self->i2c_buffer;
            devid.wfbuf = jdec.width;
            devid.self = self;
            res = jd_decomp(&jdec, outfunc, 0);         // Start to decompress with 1/1 scaling
            if (res == JDR_OK) {
                if (mode == JPG_MODE_FAST) {
                    set_window(self, x, y, x + jdec.width - 1, y + jdec.height - 1);
                    DC_HIGH();
                    CS_LOW();
                    write_spi(self->spi_obj, (uint8_t *)self->i2c_buffer, bufsize);
                    CS_HIGH();
                }
            } else {
                mp_raise_msg(&mp_type_RuntimeError, MP_ERROR_TEXT("jpg decompress failed."));
            }
            if (self->buffer_size == 0) {
                m_free(self->i2c_buffer);           // Discard frame buffer
                self->i2c_buffer = MP_OBJ_NULL;
            }
            devid.fbuf = MP_OBJ_NULL;
        } else {
            mp_raise_msg(&mp_type_RuntimeError, MP_ERROR_TEXT("jpg prepare failed."));
        }

        if (self->fp) {
            mp_close(self->fp);
            self->fp = MP_OBJ_NULL;
        }
    }
    m_free(self->work);     // Discard work area
    return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(st7789_ST7789_jpg_obj, 4, 5, st7789_ST7789_jpg);

//
// output function for jpg_decode
//

static int out_crop(                    // 1:Ok, 0:Aborted
    JDEC *jd,                           // Decompression object
    void *bitmap,                       // Bitmap data to be output
    JRECT *rect) {                      // Rectangular region of output image
    IODEV *dev = (IODEV *)jd->device;

    if (
        dev->left <= rect->right &&
        dev->right >= rect->left &&
        dev->top <= rect->bottom &&
        dev->bottom >= rect->top) {
        uint16_t left = MAX(dev->left, rect->left);
        uint16_t top = MAX(dev->top, rect->top);
        uint16_t right = MIN(dev->right, rect->right);
        uint16_t bottom = MIN(dev->bottom, rect->bottom);
        uint16_t dev_width = dev->right - dev->left + 1;
        uint16_t rect_width = rect->right - rect->left + 1;
        uint16_t width = (right - left + 1) * 2;
        uint16_t row;

        for (row = top; row <= bottom; row++) {
            memcpy(
                (uint16_t *)dev->fbuf + ((row - dev->top) * dev_width) + left - dev->left,
                (uint16_t *)bitmap + ((row - rect->top) * rect_width) + left - rect->left,
                width);
        }
    }
    return 1;     // Continue to decompress
}

//
// Decode a jpg file and return it or a portion of it as a tuple containing
// a blittable buffer, the width and height of the buffer.
//

STATIC mp_obj_t st7789_ST7789_jpg_decode(size_t n_args, const mp_obj_t *args) {
    st7789_ST7789_obj_t *self = MP_OBJ_TO_PTR(args[0]);

    static unsigned int (*input_func)(JDEC *, uint8_t *, unsigned int) = NULL;
    mp_buffer_info_t bufinfo;
    IODEV devid;

    if (mp_obj_is_type(args[1], &mp_type_bytes)) {
        mp_get_buffer_raise(args[1], &bufinfo, MP_BUFFER_READ);
        devid.dataIdx = 0;
        devid.data = bufinfo.buf;
        devid.dataLen = bufinfo.len;
        input_func = buffer_in_func;
        self->fp = MP_OBJ_NULL;
    } else {
        const char *filename = mp_obj_str_get_str(args[1]);
        self->fp = mp_open(filename, "rb");
        devid.fp = self->fp;
        input_func = file_in_func;
        devid.data = MP_OBJ_NULL;
        devid.dataLen = 0;
    }
    mp_int_t x = 0, y = 0, width = 0, height = 0;

    if (n_args == 2 || n_args == 6) {
        if (n_args == 6) {
            x = mp_obj_get_int(args[2]);
            y = mp_obj_get_int(args[3]);
            width = mp_obj_get_int(args[4]);
            height = mp_obj_get_int(args[5]);
        }

        self->work = (void *)m_malloc(3100);          // Pointer to the work area

        JRESULT res;          // Result code of TJpgDec API
        JDEC jdec;            // Decompression object
        size_t bufsize = 0;

        if (input_func && (devid.fp || devid.data)) {
            // Prepare to decompress
            res = jd_prepare(&jdec, input_func, self->work, 3100, &devid);
            if (res == JDR_OK) {
                if (n_args < 6) {
                    x = 0;
                    y = 0;
                    width = jdec.width;
                    height = jdec.height;
                }
                // Initialize output device
                devid.left = x;
                devid.top = y;
                devid.right = x + width - 1;
                devid.bottom = y + height - 1;

                bufsize = 2 * width * height;
                self->i2c_buffer = m_malloc(bufsize);
                if (self->i2c_buffer) {
                    memset(self->i2c_buffer, 0xBEEF, bufsize);
                } else {
                    mp_raise_msg(&mp_type_OSError, MP_ERROR_TEXT("out of memory"));
                }

                devid.fbuf = (uint8_t *)self->i2c_buffer;
                devid.wfbuf = jdec.width;
                devid.self = self;
                res = jd_decomp(&jdec, out_crop, 0);    // Start to decompress with 1/1 scaling
                if (res != JDR_OK) {
                    mp_raise_msg(&mp_type_RuntimeError, MP_ERROR_TEXT("jpg decompress failed."));
                }

            } else {
                mp_raise_msg(&mp_type_RuntimeError, MP_ERROR_TEXT("jpg prepare failed."));
            }
            if (self->fp) {
                mp_close(self->fp);
                self->fp = MP_OBJ_NULL;
            }
        }
        m_free(self->work);     // Discard work area

        mp_obj_t result[3] = {
            mp_obj_new_bytearray(bufsize, (mp_obj_t *)self->i2c_buffer),
            mp_obj_new_int(width),
            mp_obj_new_int(height)
        };

        return mp_obj_new_tuple(3, result);
    }

    mp_raise_TypeError(MP_ERROR_TEXT("jpg_decode requires either 2 or 6 arguments"));
    return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(st7789_ST7789_jpg_decode_obj, 2, 6, st7789_ST7789_jpg_decode);

//
// PNG Routines using the pngle library from https://github.com/kikuchan/pngle
// licensed under the MIT License
//

// Define struct for user data to be used in PNG drawing functions
typedef struct _PNG_USER_DATA {
    st7789_ST7789_obj_t *self;     // pointer to ST7789 object
    int ofs_x;                     // x offset of image
    int ofs_y;                     // y offset of image
    uint16_t pixels;               // number of pixels in buffer
    uint16_t row;                  // row in the buffer
    uint16_t first;                // first column in buffer
    uint16_t last;                 // last column in buffer
    bool has_transparency;         // true if image has transparent pixels
    uint16_t *buffer;              // pointer to current pixel in buffer

} PNG_USER_DATA;

void png_flush(st7789_ST7789_obj_t *self, PNG_USER_DATA *user_data) {
        set_window(self, user_data->first, user_data->row, user_data->last, user_data->row);
        DC_HIGH();
        CS_LOW();
        write_spi(self->spi_obj, (uint8_t *)self->i2c_buffer, user_data->pixels * 2);
        CS_HIGH();
        // reset buffer pointer and pixel count
        user_data->buffer = self->i2c_buffer;
        user_data->pixels = 0;
}

void png_new_row(PNG_USER_DATA *user_data, uint16_t row, uint16_t col) {
        user_data->row = row;                                       // save first row
        user_data->first = col;                                     // save first column
        user_data->last = col;                                      // save last column
}

// PNG drawing function for non-transparent images
void pngle_on_draw(pngle_t *pngle, uint32_t x, uint32_t y, uint32_t w, uint32_t h, uint8_t rgba[4]) {
    PNG_USER_DATA *user_data = pngle_get_user_data(pngle);          // pointer to user_data
    st7789_ST7789_obj_t *self = user_data->self;                    // pointer to ST7789 object
    int row = y + user_data->ofs_y;                                 // display row
    int col = x + user_data->ofs_x;                                 // display column

    // skip if this pixel is outside the display
    if (col < 0 || row < 0 || col >= self->width || row > self->height) {
        return;
    }

    pngle_ihdr_t *ihdr = pngle_get_ihdr(pngle);                     // pointer to image header
    size_t min_buffer_size = ihdr->width * 2;                       // minimum buffer size for one line of pixels

    if (user_data->buffer == NULL) {                                // on the first call to this function
        if (self->buffer_size == 0) {                               // If no buffer has been allocated yet
            user_data->buffer = m_malloc(min_buffer_size);          // Allocate buffer for one line of pixels
            if (user_data->buffer == NULL) {                        // If allocation failed raise an exception
                mp_raise_msg(&mp_type_OSError, MP_ERROR_TEXT("out of memory allocating i2c buffer"));
            }
        } else {
            if (self->buffer_size < min_buffer_size) {              // Check if existing buffer is large enough
                mp_raise_msg_varg(&mp_type_OSError, MP_ERROR_TEXT("buffer too small. %zu bytes required."), min_buffer_size);
            }
            user_data->buffer = self->i2c_buffer;                   // Use existing buffer
        }
        self->i2c_buffer = user_data->buffer;                       // Set buffer pointer to start of buffer
        png_new_row(user_data, row, col);                           // Start new row
    }

    // Flush the buffer if pixels are in the buffer and the row changes
    //  or if the pixel is transparent and transparency is enabled
    if (user_data->pixels > 0 && (row != user_data->row || (user_data->has_transparency && rgba[3] == 0))) {
        png_flush(self, user_data);
        png_new_row(user_data, row, col);
    }

    // if transparency is enabled and the pixel is transparent skip it.
    if (user_data->has_transparency && (rgba[3] == 0)) {
        png_new_row(user_data, row, col);
        return;
    }

    // Convert RGBA to 16-bit color, swap bytes, add to buffer
    *user_data->buffer++ = _swap_bytes(color565(rgba[0], rgba[1], rgba[2]));
    user_data->pixels++;
    user_data->last = col;
}

#define PNG_FILE_BUFFER_SIZE 256    // Size of buffer for reading PNG file

STATIC mp_obj_t st7789_ST7789_png(size_t n_args, const mp_obj_t *args) {
    st7789_ST7789_obj_t *self = MP_OBJ_TO_PTR(args[0]);
    const char *filename = mp_obj_str_get_str(args[1]);
    mp_int_t x = mp_obj_get_int(args[2]);
    mp_int_t y = mp_obj_get_int(args[3]);
    bool transparency = (n_args > 4) ? mp_obj_is_true(args[4]) : false;

    char buf[PNG_FILE_BUFFER_SIZE];
    int len, remain = 0;

    PNG_USER_DATA user_data = {
        .self = self,
        .ofs_x = x,
        .ofs_y = y,
        .pixels = 0,
        .row = 0,
        .first = 0,
        .last = 0,
        .has_transparency = transparency,
        .buffer = NULL
    };

    // allocate new pngle_t and store in self to protect memory from gc
    self->work = pngle_new(self);
    pngle_t *pngle = (pngle_t *)self->work;
    pngle_set_user_data(pngle, (void *)&user_data);
    pngle_set_draw_callback(pngle, pngle_on_draw);

    self->fp = mp_open(filename, "rb");
    while ((len = mp_readinto(self->fp, buf + remain, PNG_FILE_BUFFER_SIZE - remain)) > 0) {
        int fed = pngle_feed(pngle, buf, remain + len);
        if (fed < 0) {
            mp_raise_msg_varg(&mp_type_RuntimeError, MP_ERROR_TEXT("png decompress failed: %s"), pngle_error(pngle));
        }
        remain = remain + len - fed;
        if (remain > 0) {
            memmove(buf, buf + fed, remain);
        }
    }

    if (user_data.pixels > 0) {
        png_flush(self, &user_data);
    }

    // free dynamic buffer
    if (self->buffer_size == 0) {
        m_free(self->i2c_buffer);
        self->i2c_buffer = NULL;
    }

    mp_close(self->fp);
    pngle_destroy(pngle);
    self->work = NULL;
    return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(st7789_ST7789_png_obj, 4, 5, st7789_ST7789_png);

//
// Return the center of a polygon as an (x, y) tuple
//

STATIC mp_obj_t st7789_ST7789_polygon_center(size_t n_args, const mp_obj_t *args) {
    size_t poly_len;
    mp_obj_t *polygon;
    mp_obj_get_array(args[1], &poly_len, &polygon);

    mp_float_t sum = 0.0;
    int vsx = 0;
    int vsy = 0;

    if (poly_len > 0) {
        for (int idx = 0; idx < poly_len; idx++) {
            size_t point_from_poly_len;
            mp_obj_t *point_from_poly;
            mp_obj_get_array(polygon[idx], &point_from_poly_len, &point_from_poly);
            if (point_from_poly_len < 2) {
                mp_raise_msg(&mp_type_RuntimeError, MP_ERROR_TEXT("Polygon data error"));
            }

            mp_int_t v1x = mp_obj_get_int(point_from_poly[0]);
            mp_int_t v1y = mp_obj_get_int(point_from_poly[1]);

            mp_obj_get_array(polygon[(idx + 1) % poly_len], &point_from_poly_len, &point_from_poly);
            if (point_from_poly_len < 2) {
                mp_raise_msg(&mp_type_RuntimeError, MP_ERROR_TEXT("Polygon data error"));
            }

            mp_int_t v2x = mp_obj_get_int(point_from_poly[0]);
            mp_int_t v2y = mp_obj_get_int(point_from_poly[1]);

            mp_float_t cross = v1x * v2y - v1y * v2x;
            sum += cross;
            vsx += (int)((v1x + v2x) * cross);
            vsy += (int)((v1y + v2y) * cross);
        }

        mp_float_t z = 1.0 / (3.0 * sum);
        vsx = (int)(vsx * z);
        vsy = (int)(vsy * z);
    } else {
        mp_raise_msg(&mp_type_RuntimeError, MP_ERROR_TEXT("Polygon data error"));
    }

    mp_obj_t center[2] = {mp_obj_new_int(vsx), mp_obj_new_int(vsy)};
    return mp_obj_new_tuple(2, center);
}
STATIC MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(st7789_ST7789_polygon_center_obj, 2, 2, st7789_ST7789_polygon_center);

//
// RotatePolygon: Rotate a polygon around a center point angle radians
//

STATIC void RotatePolygon(Polygon *polygon, Point center, mp_float_t angle) {
    if (polygon->length == 0) {
        return;         /* reject null polygons */

    }
    mp_float_t cosAngle = MICROPY_FLOAT_C_FUN(cos)(angle);
    mp_float_t sinAngle = MICROPY_FLOAT_C_FUN(sin)(angle);

    for (int i = 0; i < polygon->length; i++) {
        mp_float_t dx = (polygon->points[i].x - center.x);
        mp_float_t dy = (polygon->points[i].y - center.y);

        polygon->points[i].x = center.x + (int)0.5 + (dx * cosAngle - dy * sinAngle);
        polygon->points[i].y = center.y + (int)0.5 + (dx * sinAngle + dy * cosAngle);
    }
}

//
// public-domain code by Darel Rex Finley, 2007
// https://alienryderflex.com/polygon_fill/
//

#define MAX_POLY_CORNERS 32
STATIC void PolygonFill(st7789_ST7789_obj_t *self, Polygon *polygon, Point location, uint16_t color) {
    int nodes, nodeX[MAX_POLY_CORNERS], pixelY, i, j, swap;

    int minX = INT_MAX;
    int maxX = INT_MIN;
    int minY = INT_MAX;
    int maxY = INT_MIN;

    for (i = 0; i < polygon->length; i++) {
        if (polygon->points[i].x < minX) {
            minX = (int)polygon->points[i].x;
        }

        if (polygon->points[i].x > maxX) {
            maxX = (int)polygon->points[i].x;
        }

        if (polygon->points[i].y < minY) {
            minY = (int)polygon->points[i].y;
        }

        if (polygon->points[i].y > maxY) {
            maxY = (int)polygon->points[i].y;
        }
    }

    //  Loop through the rows
    for (pixelY = minY; pixelY < maxY; pixelY++) {
        //  Build a list of nodes.
        nodes = 0;
        j = polygon->length - 1;
        for (i = 0; i < polygon->length; i++) {
            if ((polygon->points[i].y < pixelY && polygon->points[j].y >= pixelY) ||
                (polygon->points[j].y < pixelY && polygon->points[i].y >= pixelY)) {
                if (nodes < MAX_POLY_CORNERS) {
                    nodeX[nodes++] = (int)(polygon->points[i].x +
                        (pixelY - polygon->points[i].y) /
                        (polygon->points[j].y - polygon->points[i].y) *
                        (polygon->points[j].x - polygon->points[i].x));
                } else {
                    mp_raise_msg(&mp_type_RuntimeError, MP_ERROR_TEXT("Polygon too complex increase MAX_POLY_CORNERS."));
                }
            }
            j = i;
        }

        //  Sort the nodes, via a simple “Bubble” sort.
        i = 0;
        while (i < nodes - 1) {
            if (nodeX[i] > nodeX[i + 1]) {
                swap = nodeX[i];
                nodeX[i] = nodeX[i + 1];
                nodeX[i + 1] = swap;
                if (i) {
                    i--;
                }
            } else {
                i++;
            }
        }

        //  Fill the pixels between node pairs.
        for (i = 0; i < nodes; i += 2) {
            if (nodeX[i] >= maxX) {
                break;
            }

            if (nodeX[i + 1] > minX) {
                if (nodeX[i] < minX) {
                    nodeX[i] = minX;
                }

                if (nodeX[i + 1] > maxX) {
                    nodeX[i + 1] = maxX;
                }

                fast_hline(self, (int)location.x + nodeX[i], (int)location.y + pixelY, nodeX[i + 1] - nodeX[i] + 1, color);
            }
        }
    }
}

STATIC mp_obj_t st7789_ST7789_polygon(size_t n_args, const mp_obj_t *args) {
    st7789_ST7789_obj_t *self = MP_OBJ_TO_PTR(args[0]);

    size_t poly_len;
    mp_obj_t *polygon;
    mp_obj_get_array(args[1], &poly_len, &polygon);

    self->work = NULL;

    if (poly_len > 0) {
        mp_int_t x = mp_obj_get_int(args[2]);
        mp_int_t y = mp_obj_get_int(args[3]);
        mp_int_t color = mp_obj_get_int(args[4]);

        mp_float_t angle = 0.0f;
        if (n_args > 5 && mp_obj_is_float(args[5])) {
            angle = mp_obj_float_get(args[5]);
        }

        mp_int_t cx = 0;
        mp_int_t cy = 0;

        if (n_args > 6) {
            cx = mp_obj_get_int(args[6]);
            cy = mp_obj_get_int(args[7]);
        }

        self->work = m_malloc(poly_len * sizeof(Point));
        if (self->work) {
            Point *point = (Point *)self->work;

            for (int idx = 0; idx < poly_len; idx++) {
                size_t point_from_poly_len;
                mp_obj_t *point_from_poly;
                mp_obj_get_array(polygon[idx], &point_from_poly_len, &point_from_poly);
                if (point_from_poly_len < 2) {
                    mp_raise_msg(&mp_type_RuntimeError, MP_ERROR_TEXT("Polygon data error"));
                }

                mp_int_t px = mp_obj_get_int(point_from_poly[0]);
                mp_int_t py = mp_obj_get_int(point_from_poly[1]);
                point[idx].x = px;
                point[idx].y = py;
            }

            Point center;
            center.x = cx;
            center.y = cy;

            Polygon polygon;
            polygon.length = poly_len;
            polygon.points = self->work;

            if (angle > 0) {
                RotatePolygon(&polygon, center, angle);
            }

            for (int idx = 1; idx < poly_len; idx++) {
                line(
                    self,
                    (int)point[idx - 1].x + x,
                    (int)point[idx - 1].y + y,
                    (int)point[idx].x + x,
                    (int)point[idx].y + y, color);
            }

            m_free(self->work);
            self->work = NULL;
        } else {
            mp_raise_msg(&mp_type_RuntimeError, MP_ERROR_TEXT("Polygon data error"));
        }
    } else {
        mp_raise_msg(&mp_type_RuntimeError, MP_ERROR_TEXT("Polygon data error"));
    }

    return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(st7789_ST7789_polygon_obj, 4, 8, st7789_ST7789_polygon);

//
//  filled convex polygon
//

STATIC mp_obj_t st7789_ST7789_fill_polygon(size_t n_args, const mp_obj_t *args) {
    st7789_ST7789_obj_t *self = MP_OBJ_TO_PTR(args[0]);

    size_t poly_len;
    mp_obj_t *polygon;
    mp_obj_get_array(args[1], &poly_len, &polygon);

    self->work = NULL;

    if (poly_len > 0) {
        mp_int_t x = mp_obj_get_int(args[2]);
        mp_int_t y = mp_obj_get_int(args[3]);
        mp_int_t color = mp_obj_get_int(args[4]);

        mp_float_t angle = 0.0f;
        if (n_args > 5) {
            angle = mp_obj_float_get(args[5]);
        }

        mp_int_t cx = 0;
        mp_int_t cy = 0;

        if (n_args > 6) {
            cx = mp_obj_get_int(args[6]);
            cy = mp_obj_get_int(args[7]);
        }

        self->work = m_malloc(poly_len * sizeof(Point));
        if (self->work) {
            Point *point = (Point *)self->work;

            for (int idx = 0; idx < poly_len; idx++) {
                size_t point_from_poly_len;
                mp_obj_t *point_from_poly;
                mp_obj_get_array(polygon[idx], &point_from_poly_len, &point_from_poly);
                if (point_from_poly_len < 2) {
                    mp_raise_msg(&mp_type_RuntimeError, MP_ERROR_TEXT("Polygon data error"));
                }

                point[idx].x = mp_obj_get_int(point_from_poly[0]);
                point[idx].y = mp_obj_get_int(point_from_poly[1]);
            }

            Point center = {cx, cy};
            Polygon polygon = {poly_len, self->work};

            if (angle != 0) {
                RotatePolygon(&polygon, center, angle);
            }

            Point location = {x, y};
            PolygonFill(self, &polygon, location, color);

            m_free(self->work);
            self->work = NULL;
        } else {
            mp_raise_msg(&mp_type_RuntimeError, MP_ERROR_TEXT("Polygon data error"));
        }

    } else {
        mp_raise_msg(&mp_type_RuntimeError, MP_ERROR_TEXT("Polygon data error"));
    }

    return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(st7789_ST7789_fill_polygon_obj, 4, 8, st7789_ST7789_fill_polygon);

STATIC mp_obj_t st7789_ST7789_bounding(size_t n_args, const mp_obj_t *args) {
    st7789_ST7789_obj_t *self = MP_OBJ_TO_PTR(args[0]);

    mp_obj_t bounds[4] = {
        mp_obj_new_int(self->min_x),
        mp_obj_new_int(self->min_y),
        (n_args > 2 && mp_obj_is_true(args[2])) ? mp_obj_new_int(self->max_x - self->min_x + 1) : mp_obj_new_int(self->max_x),
        (n_args > 2 && mp_obj_is_true(args[2])) ? mp_obj_new_int(self->max_y - self->min_y + 1) : mp_obj_new_int(self->max_y)
    };

    if (n_args > 1) {
        if (mp_obj_is_true(args[1])) {
            self->bounding = 1;
        } else {
            self->bounding = 0;
        }

        self->min_x = self->width;
        self->min_y = self->height;
        self->max_x = 0;
        self->max_y = 0;
    }
    return mp_obj_new_tuple(4, bounds);
}
STATIC MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(st7789_ST7789_bounding_obj, 1, 3, st7789_ST7789_bounding);

STATIC const mp_rom_map_elem_t st7789_ST7789_locals_dict_table[] = {
    {MP_ROM_QSTR(MP_QSTR_write), MP_ROM_PTR(&st7789_ST7789_write_obj)},
    {MP_ROM_QSTR(MP_QSTR_write_len), MP_ROM_PTR(&st7789_ST7789_write_len_obj)},
    {MP_ROM_QSTR(MP_QSTR_hard_reset), MP_ROM_PTR(&st7789_ST7789_hard_reset_obj)},
    {MP_ROM_QSTR(MP_QSTR_soft_reset), MP_ROM_PTR(&st7789_ST7789_soft_reset_obj)},
    {MP_ROM_QSTR(MP_QSTR_sleep_mode), MP_ROM_PTR(&st7789_ST7789_sleep_mode_obj)},
    {MP_ROM_QSTR(MP_QSTR_inversion_mode), MP_ROM_PTR(&st7789_ST7789_inversion_mode_obj)},
    {MP_ROM_QSTR(MP_QSTR_map_bitarray_to_rgb565), MP_ROM_PTR(&st7789_map_bitarray_to_rgb565_obj)},
    {MP_ROM_QSTR(MP_QSTR_init), MP_ROM_PTR(&st7789_ST7789_init_obj)},
    {MP_ROM_QSTR(MP_QSTR_on), MP_ROM_PTR(&st7789_ST7789_on_obj)},
    {MP_ROM_QSTR(MP_QSTR_off), MP_ROM_PTR(&st7789_ST7789_off_obj)},
    {MP_ROM_QSTR(MP_QSTR_pixel), MP_ROM_PTR(&st7789_ST7789_pixel_obj)},
    {MP_ROM_QSTR(MP_QSTR_line), MP_ROM_PTR(&st7789_ST7789_line_obj)},
    {MP_ROM_QSTR(MP_QSTR_blit_buffer), MP_ROM_PTR(&st7789_ST7789_blit_buffer_obj)},
    {MP_ROM_QSTR(MP_QSTR_draw), MP_ROM_PTR(&st7789_ST7789_draw_obj)},
    {MP_ROM_QSTR(MP_QSTR_draw_len), MP_ROM_PTR(&st7789_ST7789_draw_len_obj)},
    {MP_ROM_QSTR(MP_QSTR_bitmap), MP_ROM_PTR(&st7789_ST7789_bitmap_obj)},
    {MP_ROM_QSTR(MP_QSTR_fill_rect), MP_ROM_PTR(&st7789_ST7789_fill_rect_obj)},
    {MP_ROM_QSTR(MP_QSTR_fill), MP_ROM_PTR(&st7789_ST7789_fill_obj)},
    {MP_ROM_QSTR(MP_QSTR_hline), MP_ROM_PTR(&st7789_ST7789_hline_obj)},
    {MP_ROM_QSTR(MP_QSTR_vline), MP_ROM_PTR(&st7789_ST7789_vline_obj)},
    {MP_ROM_QSTR(MP_QSTR_fill_circle), MP_ROM_PTR(&st7789_ST7789_fill_circle_obj)},
    {MP_ROM_QSTR(MP_QSTR_circle), MP_ROM_PTR(&st7789_ST7789_circle_obj)},
    {MP_ROM_QSTR(MP_QSTR_rect), MP_ROM_PTR(&st7789_ST7789_rect_obj)},
    {MP_ROM_QSTR(MP_QSTR_text), MP_ROM_PTR(&st7789_ST7789_text_obj)},
    {MP_ROM_QSTR(MP_QSTR_rotation), MP_ROM_PTR(&st7789_ST7789_rotation_obj)},
    {MP_ROM_QSTR(MP_QSTR_width), MP_ROM_PTR(&st7789_ST7789_width_obj)},
    {MP_ROM_QSTR(MP_QSTR_height), MP_ROM_PTR(&st7789_ST7789_height_obj)},
    {MP_ROM_QSTR(MP_QSTR_vscrdef), MP_ROM_PTR(&st7789_ST7789_vscrdef_obj)},
    {MP_ROM_QSTR(MP_QSTR_vscsad), MP_ROM_PTR(&st7789_ST7789_vscsad_obj)},
    {MP_ROM_QSTR(MP_QSTR_madctl), MP_ROM_PTR(&st7789_ST7789_madctl_obj)},
    {MP_ROM_QSTR(MP_QSTR_offset), MP_ROM_PTR(&st7789_ST7789_offset_obj)},
    {MP_ROM_QSTR(MP_QSTR_jpg), MP_ROM_PTR(&st7789_ST7789_jpg_obj)},
    {MP_ROM_QSTR(MP_QSTR_jpg_decode), MP_ROM_PTR(&st7789_ST7789_jpg_decode_obj)},
    {MP_ROM_QSTR(MP_QSTR_png), MP_ROM_PTR(&st7789_ST7789_png_obj)},
    {MP_ROM_QSTR(MP_QSTR_polygon_center), MP_ROM_PTR(&st7789_ST7789_polygon_center_obj)},
    {MP_ROM_QSTR(MP_QSTR_polygon), MP_ROM_PTR(&st7789_ST7789_polygon_obj)},
    {MP_ROM_QSTR(MP_QSTR_fill_polygon), MP_ROM_PTR(&st7789_ST7789_fill_polygon_obj)},
    {MP_ROM_QSTR(MP_QSTR_bounding), MP_ROM_PTR(&st7789_ST7789_bounding_obj)},
};
STATIC MP_DEFINE_CONST_DICT(st7789_ST7789_locals_dict, st7789_ST7789_locals_dict_table);
/* methods end */

#ifdef MP_OBJ_TYPE_GET_SLOT

MP_DEFINE_CONST_OBJ_TYPE(
    st7789_ST7789_type,
    MP_QSTR_ST7789,
    MP_TYPE_FLAG_NONE,
    print, st7789_ST7789_print,
    make_new, st7789_ST7789_make_new,
    locals_dict, (mp_obj_dict_t *)&st7789_ST7789_locals_dict);

#else

const mp_obj_type_t st7789_ST7789_type = {
    {&mp_type_type},
    .name = MP_QSTR_ST7789,
    .print = st7789_ST7789_print,
    .make_new = st7789_ST7789_make_new,
    .locals_dict = (mp_obj_dict_t *)&st7789_ST7789_locals_dict,
};

#endif

mp_obj_t st7789_ST7789_make_new(const mp_obj_type_t *type,
    size_t n_args,
    size_t n_kw,
    const mp_obj_t *all_args) {
    enum {
        ARG_spi,
        ARG_width,
        ARG_height,
        ARG_reset,
        ARG_dc,
        ARG_cs,
        ARG_backlight,
        ARG_rotations,
        ARG_rotation,
        ARG_custom_init,
        ARG_color_order,
        ARG_inversion,
        ARG_options,
        ARG_buffer_size
    };
    static const mp_arg_t allowed_args[] = {
        {MP_QSTR_spi, MP_ARG_OBJ | MP_ARG_REQUIRED, {.u_obj = MP_OBJ_NULL}},
        {MP_QSTR_width, MP_ARG_INT | MP_ARG_REQUIRED, {.u_int = 0}},
        {MP_QSTR_height, MP_ARG_INT | MP_ARG_REQUIRED, {.u_int = 0}},
        {MP_QSTR_reset, MP_ARG_KW_ONLY | MP_ARG_OBJ, {.u_obj = MP_OBJ_NULL}},
        {MP_QSTR_dc, MP_ARG_KW_ONLY | MP_ARG_OBJ, {.u_obj = MP_OBJ_NULL}},
        {MP_QSTR_cs, MP_ARG_KW_ONLY | MP_ARG_OBJ, {.u_obj = MP_OBJ_NULL}},
        {MP_QSTR_backlight, MP_ARG_KW_ONLY | MP_ARG_OBJ, {.u_obj = MP_OBJ_NULL}},
        {MP_QSTR_rotations, MP_ARG_KW_ONLY | MP_ARG_OBJ, {.u_obj = MP_OBJ_NULL}},
        {MP_QSTR_rotation, MP_ARG_KW_ONLY | MP_ARG_INT, {.u_int = 0}},
        {MP_QSTR_custom_init, MP_ARG_KW_ONLY | MP_ARG_OBJ, {.u_obj = MP_OBJ_NULL}},
        {MP_QSTR_color_order, MP_ARG_KW_ONLY | MP_ARG_INT, {.u_int = ST7789_MADCTL_RGB}},
        {MP_QSTR_inversion, MP_ARG_KW_ONLY | MP_ARG_BOOL, {.u_bool = true}},
        {MP_QSTR_options, MP_ARG_KW_ONLY | MP_ARG_INT, {.u_int = 0}},
        {MP_QSTR_buffer_size, MP_ARG_KW_ONLY | MP_ARG_INT, {.u_int = 0}},
    };
    mp_arg_val_t args[MP_ARRAY_SIZE(allowed_args)];
    mp_arg_parse_all_kw_array(n_args, n_kw, all_args, MP_ARRAY_SIZE(allowed_args), allowed_args, args);

    // create new object
    st7789_ST7789_obj_t *self = m_new_obj(st7789_ST7789_obj_t);
    self->base.type = &st7789_ST7789_type;

    // set parameters
    mp_obj_base_t *spi_obj = (mp_obj_base_t *)MP_OBJ_TO_PTR(args[ARG_spi].u_obj);
    self->spi_obj = spi_obj;
    self->display_width = args[ARG_width].u_int;
    self->width = args[ARG_width].u_int;
    self->display_height = args[ARG_height].u_int;
    self->height = args[ARG_height].u_int;

    self->rotations = NULL;
    self->rotations_len = 4;

    if (args[ARG_rotations].u_obj != MP_OBJ_NULL) {
        size_t len;
        mp_obj_t *rotations_array = MP_OBJ_NULL;
        mp_obj_get_array(args[ARG_rotations].u_obj, &len, &rotations_array);
        self->rotations_len = len;
        self->rotations = m_new(st7789_rotation_t, self->rotations_len);
        for (int i = 0; i < self->rotations_len; i++) {
            mp_obj_t *rotation_tuple = NULL;
            size_t rotation_tuple_len = 0;

            mp_obj_tuple_get(rotations_array[i], &rotation_tuple_len, &rotation_tuple);
            if (rotation_tuple_len != 5) {
                mp_raise_ValueError(MP_ERROR_TEXT("rotations tuple must have 5 elements"));
            }

            self->rotations[i].madctl = mp_obj_get_int(rotation_tuple[0]);
            self->rotations[i].width = mp_obj_get_int(rotation_tuple[1]);
            self->rotations[i].height = mp_obj_get_int(rotation_tuple[2]);
            self->rotations[i].colstart = mp_obj_get_int(rotation_tuple[3]);
            self->rotations[i].rowstart = mp_obj_get_int(rotation_tuple[4]);
        }
    }

    self->rotation = args[ARG_rotation].u_int % self->rotations_len;
    self->custom_init = args[ARG_custom_init].u_obj;
    self->color_order = args[ARG_color_order].u_int;
    self->inversion = args[ARG_inversion].u_bool;
    self->options = args[ARG_options].u_int & 0xff;
    self->buffer_size = args[ARG_buffer_size].u_int;

    if (self->buffer_size) {
        self->i2c_buffer = m_malloc(self->buffer_size);
    } else {
        self->i2c_buffer = NULL;
    }

    if (args[ARG_dc].u_obj == MP_OBJ_NULL) {
        mp_raise_ValueError(MP_ERROR_TEXT("must specify dc pin"));
    }

    if (args[ARG_reset].u_obj != MP_OBJ_NULL) {
        self->reset = mp_hal_get_pin_obj(args[ARG_reset].u_obj);
    } else {
        self->reset = GPIO_NUM_NC;
    }

    self->dc = mp_hal_get_pin_obj(args[ARG_dc].u_obj);

    if (args[ARG_cs].u_obj != MP_OBJ_NULL) {
        self->cs = mp_hal_get_pin_obj(args[ARG_cs].u_obj);
    } else {
        self->cs = GPIO_NUM_NC;
    }

    if (args[ARG_backlight].u_obj != MP_OBJ_NULL) {
        self->backlight = mp_hal_get_pin_obj(args[ARG_backlight].u_obj);
    } else {
        self->backlight = GPIO_NUM_NC;
    }

    self->bounding = 0;
    self->min_x = self->display_width;
    self->min_y = self->display_height;
    self->max_x = 0;
    self->max_y = 0;

    return MP_OBJ_FROM_PTR(self);
}

STATIC const mp_map_elem_t st7789_module_globals_table[] = {
    {MP_ROM_QSTR(MP_QSTR___name__), MP_OBJ_NEW_QSTR(MP_QSTR_st7789)},
    {MP_ROM_QSTR(MP_QSTR_color565), (mp_obj_t)&st7789_color565_obj},
    {MP_ROM_QSTR(MP_QSTR_map_bitarray_to_rgb565), (mp_obj_t)&st7789_map_bitarray_to_rgb565_obj},
    {MP_ROM_QSTR(MP_QSTR_ST7789), (mp_obj_t)&st7789_ST7789_type},
    {MP_ROM_QSTR(MP_QSTR_BLACK), MP_ROM_INT(BLACK)},
    {MP_ROM_QSTR(MP_QSTR_BLUE), MP_ROM_INT(BLUE)},
    {MP_ROM_QSTR(MP_QSTR_RED), MP_ROM_INT(RED)},
    {MP_ROM_QSTR(MP_QSTR_GREEN), MP_ROM_INT(GREEN)},
    {MP_ROM_QSTR(MP_QSTR_CYAN), MP_ROM_INT(CYAN)},
    {MP_ROM_QSTR(MP_QSTR_MAGENTA), MP_ROM_INT(MAGENTA)},
    {MP_ROM_QSTR(MP_QSTR_YELLOW), MP_ROM_INT(YELLOW)},
    {MP_ROM_QSTR(MP_QSTR_WHITE), MP_ROM_INT(WHITE)},
    {MP_ROM_QSTR(MP_QSTR_FAST), MP_ROM_INT(JPG_MODE_FAST)},
    {MP_ROM_QSTR(MP_QSTR_SLOW), MP_ROM_INT(JPG_MODE_SLOW)},
    {MP_ROM_QSTR(MP_QSTR_MADCTL_MY), MP_ROM_INT(ST7789_MADCTL_MY)},
    {MP_ROM_QSTR(MP_QSTR_MADCTL_MX), MP_ROM_INT(ST7789_MADCTL_MX)},
    {MP_ROM_QSTR(MP_QSTR_MADCTL_MV), MP_ROM_INT(ST7789_MADCTL_MV)},
    {MP_ROM_QSTR(MP_QSTR_MADCTL_ML), MP_ROM_INT(ST7789_MADCTL_ML)},
    {MP_ROM_QSTR(MP_QSTR_MADCTL_MH), MP_ROM_INT(ST7789_MADCTL_MH)},
    {MP_ROM_QSTR(MP_QSTR_RGB), MP_ROM_INT(ST7789_MADCTL_RGB)},
    {MP_ROM_QSTR(MP_QSTR_BGR), MP_ROM_INT(ST7789_MADCTL_BGR)},
    {MP_ROM_QSTR(MP_QSTR_WRAP), MP_ROM_INT(OPTIONS_WRAP)},
    {MP_ROM_QSTR(MP_QSTR_WRAP_H), MP_ROM_INT(OPTIONS_WRAP_H)},
    {MP_ROM_QSTR(MP_QSTR_WRAP_V), MP_ROM_INT(OPTIONS_WRAP_V)}
};

STATIC MP_DEFINE_CONST_DICT(mp_module_st7789_globals, st7789_module_globals_table);

const mp_obj_module_t mp_module_st7789 = {
    .base = {&mp_type_module},
    .globals = (mp_obj_dict_t *)&mp_module_st7789_globals,
};

#if !defined(MICROPY_VERSION) || MICROPY_VERSION <= 70144
MP_REGISTER_MODULE(MP_QSTR_st7789, mp_module_st7789, MODULE_ST7789_ENABLE);
#else
MP_REGISTER_MODULE(MP_QSTR_st7789, mp_module_st7789);
#endif
