#===============================================================================
#  Programs and libraries
#===============================================================================
case node[:platform]
when "debian", "ubuntu"
  log "Refreshing package database."
  execute "apt-get update -y"
  execute "apt-get upgrade -y"
end


#===============================================================================
#  Programs and libraries
#===============================================================================

log "Installing required software."

include_recipe "buildtools"
include_recipe "git"
include_recipe "python"
include_recipe "pip"

include_recipe "libraries"

include_recipe "postgresql::server"


unless `which cms`.chomp.size > 0
  remote_file "/tmp/cms.deb" do
    source "http://dl.dropbox.com/u/72178/dist/CMS-4.0.0-Linux.deb"
  end

  package "cms" do
    version "4.0.0"
    source "/tmp/cms.deb"
    provider Chef::Provider::Package::Dpkg # Needed because apt only looks at repos
  end
end


#===============================================================================
#  Python modules
#===============================================================================
log "Installing Python packages."

pipRoot = File.expand_path(File.join(File.dirname(__FILE__), "..", "..", "pip"))
require File.join(pipRoot, "providers", "pip")
require File.join(pipRoot, "resources", "pip_package")

pip_package "sphinx"
pip_package "flask"
pip_package "pyparsing"

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

pip_package "griddata" do
  version "0.1.2"
  file "http://griddata-python.googlecode.com/files/griddata-0.1.2.tar.gz"
end

pip_package "h5py" do
  # pyH5 has a tiny bug that prevents it from compiling against Python 2.7.  The
  # following archive has been fixed, but should be removed once the official
  # version goes higher than 1.3.0.
  version "1.3.0"
  file "http://dl.dropbox.com/u/72178/dist/h5py-1.3.0.tar.gz"
end
pip_package "netCDF4"

pip_package "pydap"

pip_package "psycopg2"
pip_package "sqlalchemy"
pip_package "geoalchemy"
pip_package "pyproj"

pip_package "ipython"


#===============================================================================
#  NCAR, which does not play nice with the other kids.
#===============================================================================
include_recipe "NCAR"

#===============================================================================
#  Wave Model Setup
#===============================================================================
include_recipe "wave_forecasting"

