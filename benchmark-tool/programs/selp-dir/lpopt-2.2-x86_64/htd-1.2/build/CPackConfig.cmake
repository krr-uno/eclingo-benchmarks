# This file will be configured to contain variables for CPack. These variables
# should be set in the CMake list file of the project before CPack module is
# included. The list of available CPACK_xxx variables and their associated
# documentation may be obtained using
#  cpack --help-variable-list
#
# Some variables are common to all generators (e.g. CPACK_PACKAGE_NAME)
# and some are specific to a generator
# (e.g. CPACK_NSIS_EXTRA_INSTALL_COMMANDS). The generator specific variables
# usually begin with CPACK_<GENNAME>_xxxx.


set(CPACK_BUILD_SOURCE_DIRS "/gpfs1/home/e/l/elillopo/eclingo-benchmark/selp/lpopt-2.2-x86_64/htd-1.2;/gpfs1/home/e/l/elillopo/eclingo-benchmark/selp/lpopt-2.2-x86_64/htd-1.2/build")
set(CPACK_CMAKE_GENERATOR "Unix Makefiles")
set(CPACK_COMPONENTS_ALL "")
set(CPACK_COMPONENT_UNSPECIFIED_HIDDEN "TRUE")
set(CPACK_COMPONENT_UNSPECIFIED_REQUIRED "TRUE")
set(CPACK_DEFAULT_PACKAGE_DESCRIPTION_FILE "/gpfs1/sw/x86_64/rh7/pkgs/cmake/3.28.3/share/cmake-3.28/Templates/CPack.GenericDescription.txt")
set(CPACK_DEFAULT_PACKAGE_DESCRIPTION_SUMMARY "htd built using CMake")
set(CPACK_DMG_SLA_USE_RESOURCE_FILE_LICENSE "ON")
set(CPACK_GENERATOR "STGZ;TGZ;TZ;ZIP")
set(CPACK_INNOSETUP_ARCHITECTURE "x64")
set(CPACK_INSTALL_CMAKE_PROJECTS "/gpfs1/home/e/l/elillopo/eclingo-benchmark/selp/lpopt-2.2-x86_64/htd-1.2/build;htd;ALL;/")
set(CPACK_INSTALL_PREFIX "/usr/local")
set(CPACK_MODULE_PATH "")
set(CPACK_NSIS_DISPLAY_NAME "htd 1.2.0")
set(CPACK_NSIS_INSTALLER_ICON_CODE "")
set(CPACK_NSIS_INSTALLER_MUI_ICON_CODE "")
set(CPACK_NSIS_INSTALL_ROOT "$PROGRAMFILES")
set(CPACK_NSIS_PACKAGE_NAME "htd 1.2.0")
set(CPACK_NSIS_UNINSTALL_NAME "Uninstall")
set(CPACK_OBJCOPY_EXECUTABLE "/usr/bin/objcopy")
set(CPACK_OBJDUMP_EXECUTABLE "/usr/bin/objdump")
set(CPACK_OUTPUT_CONFIG_FILE "/gpfs1/home/e/l/elillopo/eclingo-benchmark/selp/lpopt-2.2-x86_64/htd-1.2/build/CPackConfig.cmake")
set(CPACK_PACKAGE_DEFAULT_LOCATION "/")
set(CPACK_PACKAGE_DESCRIPTION_FILE "/gpfs1/home/e/l/elillopo/eclingo-benchmark/selp/lpopt-2.2-x86_64/htd-1.2/README.md")
set(CPACK_PACKAGE_DESCRIPTION_SUMMARY "A small but efficient C++ library for computing (customized) tree and hypertree decompositions.")
set(CPACK_PACKAGE_FILE_NAME "htd-1.2.0-Linux")
set(CPACK_PACKAGE_INSTALL_DIRECTORY "htd 1.2.0")
set(CPACK_PACKAGE_INSTALL_REGISTRY_KEY "htd 1.2.0")
set(CPACK_PACKAGE_NAME "htd")
set(CPACK_PACKAGE_RELOCATABLE "true")
set(CPACK_PACKAGE_VENDOR "Michael Abseher (abseher@dbai.tuwien.ac.at)")
set(CPACK_PACKAGE_VERSION "1.2.0")
set(CPACK_PACKAGE_VERSION_MAJOR "1")
set(CPACK_PACKAGE_VERSION_MINOR "2")
set(CPACK_PACKAGE_VERSION_PATCH "0")
set(CPACK_READELF_EXECUTABLE "/usr/bin/readelf")
set(CPACK_RESOURCE_FILE_LICENSE "/gpfs1/home/e/l/elillopo/eclingo-benchmark/selp/lpopt-2.2-x86_64/htd-1.2/LICENSE.txt")
set(CPACK_RESOURCE_FILE_README "/gpfs1/sw/x86_64/rh7/pkgs/cmake/3.28.3/share/cmake-3.28/Templates/CPack.GenericDescription.txt")
set(CPACK_RESOURCE_FILE_WELCOME "/gpfs1/sw/x86_64/rh7/pkgs/cmake/3.28.3/share/cmake-3.28/Templates/CPack.GenericWelcome.txt")
set(CPACK_SET_DESTDIR "OFF")
set(CPACK_SOURCE_GENERATOR "STGZ;TGZ;TZ;ZIP")
set(CPACK_SOURCE_OUTPUT_CONFIG_FILE "/gpfs1/home/e/l/elillopo/eclingo-benchmark/selp/lpopt-2.2-x86_64/htd-1.2/build/CPackSourceConfig.cmake")
set(CPACK_SYSTEM_NAME "Linux")
set(CPACK_THREADS "1")
set(CPACK_TOPLEVEL_TAG "Linux")
set(CPACK_WIX_SIZEOF_VOID_P "8")

if(NOT CPACK_PROPERTIES_FILE)
  set(CPACK_PROPERTIES_FILE "/gpfs1/home/e/l/elillopo/eclingo-benchmark/selp/lpopt-2.2-x86_64/htd-1.2/build/CPackProperties.cmake")
endif()

if(EXISTS ${CPACK_PROPERTIES_FILE})
  include(${CPACK_PROPERTIES_FILE})
endif()