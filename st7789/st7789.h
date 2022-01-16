#ifndef __ST7789_H__
#define __ST7789_H__

#ifdef __cplusplus
extern "C" {
#endif

// color modes
#define COLOR_MODE_65K      0x50
#define COLOR_MODE_262K     0x60
#define COLOR_MODE_12BIT    0x03
#define COLOR_MODE_16BIT    0x05
#define COLOR_MODE_18BIT    0x06
#define COLOR_MODE_16M      0x07

// commands
#define ST7789_NOP     0x00
#define ST7789_SWRESET 0x01
#define ST7789_RDDID   0x04
#define ST7789_RDDST   0x09

#define ST7789_SLPIN   0x10
#define ST7789_SLPOUT  0x11
#define ST7789_PTLON   0x12
#define ST7789_NORON   0x13

#define ST7789_INVOFF  0x20
#define ST7789_INVON   0x21
#define ST7789_DISPOFF 0x28
#define ST7789_DISPON  0x29
#define ST7789_CASET   0x2A
#define ST7789_RASET   0x2B
#define ST7789_RAMWR   0x2C
#define ST7789_RAMRD   0x2E

#define ST7789_PTLAR   0x30
#define ST7789_VSCRDEF 0x33
#define ST7789_COLMOD  0x3A
#define ST7789_MADCTL  0x36
#define ST7789_VSCSAD  0x37

#define ST7789_MADCTL_MY  0x80  // Page Address Order
#define ST7789_MADCTL_MX  0x40  // Column Address Order
#define ST7789_MADCTL_MV  0x20  // Page/Column Order
#define ST7789_MADCTL_ML  0x10  // Line Address Order
#define ST7789_MADCTL_MH  0x04  // Display Data Latch Order
#define ST7789_MADCTL_RGB 0x00
#define ST7789_MADCTL_BGR 0x08

#define ST7789_RDID1   0xDA
#define ST7789_RDID2   0xDB
#define ST7789_RDID3   0xDC
#define ST7789_RDID4   0xDD

// Color definitions
#define	BLACK   0x0000
#define	BLUE    0x001F
#define	RED     0xF800
#define	GREEN   0x07E0
#define CYAN    0x07FF
#define MAGENTA 0xF81F
#define YELLOW  0xFFE0
#define WHITE   0xFFFF

#define OPTIONS_WRAP_V 0x01
#define OPTIONS_WRAP_H 0x02
#define OPTIONS_WRAP   0x03

typedef struct _Point {
   mp_float_t x;
   mp_float_t y;
} Point;

typedef struct _Polygon {
    int     length;
    Point   *points;
} Polygon;

typedef struct _st7789_rotation_t {
    uint8_t madctl;
    uint16_t width;
    uint16_t height;
    uint16_t colstart;
    uint16_t rowstart;
} st7789_rotation_t;

// this is the actual C-structure for our new object
typedef struct _st7789_ST7789_obj_t {
    mp_obj_base_t base;

    mp_obj_base_t *spi_obj;
	mp_file_t *fp;				// file object
	uint16_t *i2c_buffer;		// resident buffer if buffer_size given
    void *work;                 // work buffer for jpg decoding
	size_t buffer_size;         // resident buffer size, 0=dynamic
    uint16_t display_width;     // physical width
    uint16_t width;             // logical width (after rotation)
    uint16_t display_height;    // physical width
    uint16_t height;            // logical height (after rotation)
    uint8_t colstart;
    uint8_t rowstart;
    uint8_t rotation;
    st7789_rotation_t *rotations;   // list of rotation tuples [(madctl, colstart, rowstart)]
    uint8_t rotations_len;          // number of rotations
    uint8_t color_order;
    bool inversion;
    uint8_t madctl;
    uint8_t options;            // options bit array
    mp_hal_pin_obj_t reset;
    mp_hal_pin_obj_t dc;
    mp_hal_pin_obj_t cs;
    mp_hal_pin_obj_t backlight;

    uint8_t bounding;
    uint16_t min_x;
    uint16_t min_y;
    uint16_t max_x;
    uint16_t max_y;

} st7789_ST7789_obj_t;

mp_obj_t st7789_ST7789_make_new(const mp_obj_type_t *type, size_t n_args, size_t n_kw, const mp_obj_t *args);

extern void draw_pixel(st7789_ST7789_obj_t *self, int16_t x, int16_t y, uint16_t color);
extern void fast_hline(st7789_ST7789_obj_t *self, int16_t x, int16_t y, int16_t w, uint16_t color);

#ifdef  __cplusplus
}
#endif /*  __cplusplus */

#endif  /*  __ST7789_H__ */
