puts "Bootstrapping Development Environment."

include_recipe "buildtools"
include_recipe "git"
include_recipe "libraries"

include_recipe "python"
include_recipe "pip"

puts "Adding Python Modules."

pipRoot = File.expand_path(File.join(File.dirname(__FILE__), "..", "..", "pip"))
require pipRoot + "/providers/pip"
require pipRoot + "/resources/pip_package"

pip_package "sphinx"
pip_package "flask"
pip_package "numpy"

pip_package "scipy" do
  # SciPy has a problem compiling agianst Python 2.7 due to a missing C++ header
  # file.  The issue is documented at:
  #
  #     http://projects.scipy.org/scipy/ticket/1180
  #
  # The package used here is the official 0.8.0 release patched with SVN
  # changeset 6646:
  #
  #     http://projects.scipy.org/scipy/changeset/6646 
  #
  # Once 0.9.0 comes out, this issue should be resolved.
  version "0.8.0"
  file "http://dl.dropbox.com/u/72178/dist/scipy-0.8.0.tar.gz"
end

pip_package "h5py" do
  # pyH5 has a tiny bug that prevents it from compiling agains Python 2.7.  The
  # following archive has been fixed, but should be removed once the official
  # version goes higher than 1.3.0.
  version "1.3.0"
  file "http://dl.dropbox.com/u/72178/dist/h5py-1.3.0.tar.gz"
end

