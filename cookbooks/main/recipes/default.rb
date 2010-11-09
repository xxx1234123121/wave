puts "Bootstrapping Development Environment."

include_recipe "git"
include_recipe "gfortran"
include_recipe "datalibs"

include_recipe "python"
include_recipe "pip"

pipRoot = File.expand_path(File.join(File.dirname(__FILE__), "..", "..", "pip"))
require pipRoot + "/providers/pip"
require pipRoot + "/resources/pip_package"

pip_package "sphinx"
pip_package "flask"
pip_package "numpy"

