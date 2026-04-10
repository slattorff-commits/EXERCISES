cmake_minimum_required(VERSION 3.8)
project(turtle_rgb)

find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "srv/SetRGB.srv"
)

ament_export_dependencies(rosidl_default_runtime)

ament_package()