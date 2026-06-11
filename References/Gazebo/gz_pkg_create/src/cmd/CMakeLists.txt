
#===============================================================================
# Used for the installed model command version.
# Generate the ruby script that gets installed.
# Note that the major version of the library is included in the name.
# set(library_location "../../../${CMAKE_INSTALL_LIBDIR}/$<TARGET_FILE_NAME:${ign_lib_target}>")

set(cmd_model_script_generated "${CMAKE_CURRENT_BINARY_DIR}/cmdpkg_create${PROJECT_VERSION_MAJOR}.rb")
set(cmd_model_script_configured "${cmd_model_script_generated}.configured")

configure_file(
  "cmdpkg_create.rb.in"
  "${cmd_model_script_configured}"
  @ONLY)
file(GENERATE
  OUTPUT "${cmd_model_script_generated}"
  INPUT  "${cmd_model_script_configured}")

install(FILES ${cmd_model_script_generated} DESTINATION lib/ruby/ignition)
install(DIRECTORY resources
  DESTINATION lib/ruby/ignition)

install(DIRECTORY config
  DESTINATION lib/ruby/ignition)

# Used for the installed version.
set(ign_model_ruby_path "${CMAKE_INSTALL_PREFIX}/lib/ruby/ignition/cmdpkg_create${PROJECT_VERSION_MAJOR}")
set(model_configured "${CMAKE_CURRENT_BINARY_DIR}/pkg_create{PROJECT_VERSION_MAJOR}.yaml")

configure_file(
  "pkg_create.yaml.in"
  ${model_configured})

install(FILES ${model_configured} DESTINATION ${CMAKE_INSTALL_PREFIX}/${CMAKE_INSTALL_DATAROOTDIR}/ignition/)
#===============================================================================