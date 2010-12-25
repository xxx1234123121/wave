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

pip_package "h5py" do
  # pyH5 has a tiny bug that prevents it from compiling against Python 2.7.  The
  # following archive has been fixed, but should be removed once the official
  # version goes higher than 1.3.0.
  version "1.3.0"
  file "http://dl.dropbox.com/u/72178/dist/h5py-1.3.0.tar.gz"
end

pip_package "psycopg2"
pip_package "sqlalchemy"
pip_package "geoalchemy"
pip_package "pyproj"


#===============================================================================
#  NCAR, which does not play nice with the other kids.
#===============================================================================
include_recipe "NCAR"


#===============================================================================
#  Wave Model Setup
#===============================================================================

#  User creation
#-------------------------------------------------------------------------------

log "Isolating modeling environment with a new user."

case node[:platform]
when "debian", "ubuntu"
  # To allow Chef to set user passwords
  package "libshadow-ruby1.8"
end

user node[:user] do
  password node[:user_password]
  home node[:user_home]
  shell "/bin/bash"
  supports :manage_home => true
end

#  Code Checkout
#-------------------------------------------------------------------------------

log "Downloading project code."

git "SERC Software" do
  repository "git://github.com/serc/wave.git"
  user node[:user]
  destination File.join(node[:user_home], 'wave')
  action :sync
end

#  Database Creation
#-------------------------------------------------------------------------------

log "Setting up databases."

script "Create postgres user" do
  interpreter "ruby"
  user node[:postgres_config][:admin_user]
  code <<-RUBY
    user_check = `psql -t -c "SELECT usename FROM pg_user WHERE usename = '#{node[:user]}';"`
    `psql -c "CREATE USER #{node[:user]} WITH PASSWORD '#{node[:postgrespass]}';"` unless user_check.chomp.size > 0
  RUBY
end

case node[:platform]
when "debian", "ubuntu"
  pg_contrib = File.join("/usr/share/postgresql", node[:postgresql][:version], "contrib")
end

pg_uuid = File.join(pg_contrib, "uuid-ossp.sql")
# Naughty assumptions about PostGIS version number
pg_postgis = File.join(pg_contrib, "postgis-1.5", "postgis.sql" )
pg_spatial = File.join(pg_contrib, "postgis-1.5", "spatial_ref_sys.sql" )

wave_model_schema = File.join(node[:user_home], "wave", "db", "design", "wave.psql")

pg_db = node[:postgres_config][:productionDB]
script "Create production database" do
  interpreter "ruby"
  user node[:postgres_config][:admin_user]
  code <<-RUBY
    db_check = `psql -t -c "SELECT datname FROM pg_database WHERE datname = '#{pg_db}';"`
    unless db_check.chomp.size > 0

      `createdb #{pg_db}`
      `createlang plpgsql #{pg_db}`

      `psql -d #{pg_db} -f#{pg_uuid}`
      `psql -d #{pg_db} -f#{pg_postgis}`
      `psql -d #{pg_db} -f#{pg_spatial}`
      `psql -d #{pg_db} -f#{wave_model_schema}`

      table_grants = `psql -t -d #{pg_db} -c "select
        'grant all on '||schemaname||'.'||tablename||' to #{node[:user]};' 
        from pg_tables where schemaname in ('public') order by schemaname, tablename;"`.split "\n"
      
      table_grants.each do |grant|
        `psql -d #{pg_db} -c "\#{grant}"`
      end

    end
  RUBY
end

pg_db = node[:postgres_config][:testDB]
script "Create test database" do
  interpreter "ruby"
  user node[:postgres_config][:admin_user]
  code <<-RUBY
    db_check = `psql -t -c "SELECT datname FROM pg_database WHERE datname = '#{pg_db}';"`
    unless db_check.chomp.size > 0

      `createdb #{pg_db}`
      `createlang plpgsql #{pg_db}`

      `psql -d #{pg_db} -f#{pg_uuid}`
      `psql -d #{pg_db} -f#{pg_postgis}`
      `psql -d #{pg_db} -f#{pg_spatial}`
      `psql -d #{pg_db} -f#{wave_model_schema}`

      table_grants = `psql -t -d #{pg_db} -c "select
        'grant all on '||schemaname||'.'||tablename||' to #{node[:user]};' 
        from pg_tables where schemaname in ('public') order by schemaname, tablename;"`.split "\n"
      
      table_grants.each do |grant|
        `psql -d #{pg_db} -c "\#{grant}"`
      end

    end
  RUBY
end

