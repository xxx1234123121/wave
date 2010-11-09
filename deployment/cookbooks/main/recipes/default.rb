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
pip_package "h5py" do
  # pyH5 has a tiny bug that prevents it from compiling agains Python 2.7.  The
  # following archive has been fixed, but should be removed once the official
  # version goes higsmallher than 1.3.0.
  version "1.3.0"
  file "http://dl.dropbox.com/u/72178/dist/h5py-1.3.0.tar.gz"
end

