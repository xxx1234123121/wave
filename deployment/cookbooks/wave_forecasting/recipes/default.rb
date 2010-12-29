#  User creation
#-------------------------------------------------------------------------------

log "Isolating modeling environment with a new user."

case node[:platform]
when "debian", "ubuntu"
  # To allow Chef to set user passwords
  package "libshadow-ruby1.8"
  # To generate shadow hashes from plaintext passwords
  package "makepasswd"
end

ruby_block 'make_wave_user' do
  block do
    # Has to be done this way because all Ruby code is executed *before* Chef
    # resources are evaluated.  This means the shell command that generated the
    # shadow hash was evaluated before the `package "makepassword"` resource
    # installed `makepasswd`.  Unfortunately, Chef resources cannot easily be
    # nested inside blocks, so the ugliness below is the result of low-level
    # Chef commands.
    run_context = Chef::RunContext.new(node, {})
    user = Chef::Resource::User.new(node[:user], run_context)

    shadow_hash = `echo '#{node[:user_password]}' | makepasswd --clearfrom=- --crypt-md5 |awk '{ print $2 }'`.chomp

    user.password  shadow_hash
    user.home      node[:user_home]
    user.shell     "/bin/bash"
    user.supports  :manage_home => true

    user.run_action :create
  end
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
    `psql -c "CREATE USER #{node[:user]} WITH PASSWORD '#{node[:user_password]}';"` unless user_check.chomp.size > 0
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

pg_db = node[:postgres_config][:production_db]
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

pg_db = node[:postgres_config][:test_db]
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
