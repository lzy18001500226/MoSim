#!/usr/bin/ruby

# Copyright (C) 2022 Open Source Robotics Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

require 'erb'
require 'open-uri'
require 'yaml'
require 'ostruct'

class Add_files

  def cmake_lists(resources_dir,open_struct_opt,options,req_file_and_path)
    cmakelists_render = ERB.new(File.read(resources_dir+req_file_and_path[1]),trim_mode: ">")
    cmakelists_file = File.new(options['name']+"/CMakeLists.txt", "w")
    cmakelists_file.puts(cmakelists_render.result(open_struct_opt))
    cmakelists_file.close
  end

  def package_xml(resources_dir,open_struct_opt,options,req_file_and_path)
    package_xml_render = ERB.new(File.read(resources_dir+req_file_and_path[1]),trim_mode: ">")
    package_xml_file = File.new(options['name']+"/package.xml", "w")
    package_xml_file.puts(package_xml_render.result(OpenStruct.new(options).instance_eval { binding }))
    package_xml_file.close
  end

  def worlds(resources_dir,open_struct_opt,options,req_file_and_path)
    Dir.mkdir(options['name']+"/worlds")
    world_txt=File.read(resources_dir+req_file_and_path[1])
    world_file = File.new(options['name']+"/worlds/empty_platform_with_elevator.sdf", "w")
    world_file.puts(world_txt)
    world_file.close
  end

  def models(resources_dir,open_struct_opt,options,req_file_and_path)
    Dir.mkdir(options['name']+"/models")
    Dir.mkdir(options['name']+"/models/elevator")
    model_config_txt=File.read(resources_dir+req_file_and_path[1])
    model_config_file = File.new(options['name']+"/models/elevator/model.config", "w")
    model_config_file.puts(model_config_txt)
    model_config_file.close

    model_sdf_txt=File.read(resources_dir+req_file_and_path[2])
    model_sdf_file = File.new(options['name']+"/models/elevator/model.sdf", "w")
    model_sdf_file.puts(model_sdf_txt)
    model_sdf_file.close
  end

  def plugins(resources_dir,open_struct_opt,options,req_file_and_path)
    Dir.mkdir(options['name']+"/plugins")
    plugin_txt=File.read(resources_dir+req_file_and_path[1])
    plugin_file = File.new(options['name']+"/plugins/HelloWorld.cc", "w")
    plugin_file.puts(plugin_txt)
    plugin_file.close

    plugin_header_txt=File.read(resources_dir+req_file_and_path[2])
    plugin_header_file = File.new(options['name']+"/plugins/HelloWorld.hh", "w")
    plugin_header_file.puts(plugin_header_txt)
    plugin_header_file.close
  end

  def executable(resources_dir,open_struct_opt,options,req_file_and_path)
    Dir.mkdir(options['name']+"/src")
    executable_txt=File.read(resources_dir+req_file_and_path[1])
    executable_file = File.new(options['name']+"/src/random_points.cc", "w")
    executable_file.puts(executable_txt)
    executable_file.close
  end

end

def add_required_files(command,config_yaml,open_struct_opt,options,resources_dir)
  add_file_obj=Add_files.new
  for req_file_and_path in config_yaml.fetch(command)
    add_file_obj.send(req_file_and_path[0],resources_dir,open_struct_opt,options,req_file_and_path)
  end

end
