# Create an INTERFACE library for our C module.
add_library(usermod_st7789 INTERFACE)

# Add our source files to the lib
target_sources(usermod_st7789 INTERFACE
    ${CMAKE_CURRENT_LIST_DIR}/st7789.c
    ${CMAKE_CURRENT_LIST_DIR}/mpfile.c
    ${CMAKE_CURRENT_LIST_DIR}/tjpgd565.c
)

# Add the current directory as an include directory.
target_include_directories(usermod_st7789 INTERFACE
    ${CMAKE_CURRENT_LIST_DIR}

)
target_compile_definitions(usermod_st7789 INTERFACE
    MODULE_ST7789_ENABLED=1
    MICROPY_PY_FILE_LIKE=1
    EXPOSE_EXTRA_METHODS=1
)

# Link our INTERFACE library to the usermod target.
target_link_libraries(usermod INTERFACE usermod_st7789)
