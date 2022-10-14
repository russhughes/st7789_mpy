ST7789_MOD_DIR := $(USERMOD_DIR)

CFLAGS_USERMOD += -I$(ST7789_MOD_DIR)

SRC_USERMOD += $(addprefix $(ST7789_MOD_DIR)/, st7789.c)
SRC_USERMOD += $(addprefix $(ST7789_MOD_DIR)/, mpfile.c)
SRC_USERMOD += $(addprefix $(ST7789_MOD_DIR)/jpg/, tjpgd565.c)
SRC_USERMOD += $(addprefix $(ST7789_MOD_DIR)/png/, pngle.c)
SRC_USERMOD += $(addprefix $(ST7789_MOD_DIR)/png/, miniz.c)
