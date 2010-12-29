#!/usr/bin/ruby
#
# This script sets up and runs the deployment proceedure for the wave
# forecasting software.
#
# Inspired by, and forked from, the installation script for the Homebrew package
# manager:
#
#    https://gist.github.com/323731
require 'rubygems'
require 'tmpdir'
require 'pathname'

module Tty extend self
  def blue; bold 34; end
  def white; bold 39; end
  def green; bold 32; end
  def red; underline 31; end
  def reset; escape 0; end
  def bold n; escape "1;#{n}" end
  def underline n; escape "4;#{n}" end
  def escape n; "\033[#{n}m" if STDOUT.tty? end
end

class Array
  def shell_s
    cp = dup
    first = cp.shift
    cp.map{ |arg| arg.gsub " ", "\\ " }.unshift(first) * " "
  end
end

def ohai *args
  puts "#{Tty.blue}==>#{Tty.white} #{args.shell_s}#{Tty.reset}"
end

def warn warning
  puts "#{Tty.red}Warning#{Tty.reset}: #{warning.chomp}"
end
 
def system *args
  abort "Failed during: #{args.shell_s}" unless Kernel.system *args
end

def sudo *args
  args = if args.length > 1
    args.unshift "/usr/bin/sudo"
  else
    "/usr/bin/sudo #{args}"
  end
  ohai *args
  system *args
end

def get_password
  password = ask("Please enter a password for the user: ") do |question|
    question.echo = '*'
    question.validate = lambda { |ans| ans.length > 0 }
    question.responses[:not_valid] = "Please enter a password of non-zero length!"
    question.responses[:ask_on_error] = :question # Re-ask if validation fails
  end

  check = ask("Please re-enter the password: ") do |question|
    question.echo = '*'
  end 

  if password == check
    puts "Password accepted. It will also be used for Postgres database access."
    return password
  else
    warn "Passwords do not match! Try again."
    return get_password
  end
end

def get_config_opts
  ohai "Gathering setup information:"
  puts "Press enter to use |default| values."

  opts = {}

  opts[:user] = ask("What user should own the forecasting system? ") do |question|
    question.default = 'wave'
  end

  opts[:user_home] = ask("Where should #{opts[:user]}'s home directory be located? ") do |question|
    question.default = "/home/#{opts[:user]}"
  end

  pg_config = {}
  pg_config[:admin_user] = ask("Which user administrates the Postgres database? (Defaults are good here) ") do |question|
    question.default = "postgres"
  end

  pg_config[:production_db] = ask("What should the name of the production database be? ") do |question|
    question.default = "wave"
  end

  pg_config[:test_db] = ask("What should the name of the test database be? ") do |question|
    question.default = "wave_test"
  end

  opts[:postgres_config] = pg_config

  
  puts "The following configuration has been chosen:"
  puts opts.to_yaml
  
  # Handy highline function, agree() accepts "yes" or "no" or shortened versions
  # and returns true/false.
  ok_to_go = agree("Is this setup ok [yes/no]? ") do |question|
    question.default = 'yes'
  end

  if ok_to_go
    opts[:user_password] = get_password
    return opts
  else
    # Call the function again to get new values
    return get_config_opts
  end
end


####################################################################### script
ohai "Checking installer requirements:"
print "Checking for Chef... "
if Kernel.system "/usr/bin/which -s chef-solo"
  puts "\t#{Tty.green}Found#{Tty.reset}"
else
  puts "\t#{Tty.red}Not Found#{Tty.reset}"
  abort <<-EOS
The Chef configuration manager is used to deploy the wave forecasting suite and
its dependencies. Chef can be installed on Ubuntu using the following commands:

    sudo apt-get install ruby-dev rubygems
    sudo gem install chef
  
For more information about Chef, see:

    http://www.opscode.com/chef/

  EOS
end

print "Checking for JSON... "
begin
  require 'json'
  puts "\t#{Tty.green}Found#{Tty.reset}"
rescue LoadError
  puts "\t#{Tty.red}Not Found#{Tty.reset}"
  abort <<-EOS
This installer requires the Ruby JSON gem in order to write some configuration
files. JSON can be installed on Ubuntu using the following commands:

    sudo apt-get install ruby-dev rubygems
    sudo gem install json
  
  EOS
end

print "Checking for highline... "
begin
  require 'highline/import'
  puts "\t#{Tty.green}Found#{Tty.reset}"
rescue LoadError
  puts "\t#{Tty.red}Not Found#{Tty.reset}"
  abort <<-EOS
This installer requires the Ruby highline gem in order to secure password input.
highline can be installed on Ubuntu using the following commands:

    sudo apt-get install ruby-dev rubygems
    sudo gem install highline
  
  EOS
end

ohai "This script will install:"
puts "- Compilers and tools required to build and mantain forecasting software."
puts "- Libraries and programs required to use forecasting software."
puts "- Python modules required to use forecasting software."
puts "- Forecasting software and database, owned by a new user."

config = get_config_opts
config[:run_list] = ['main']

work_dir = (Pathname Dir.pwd) + 'work'
work_dir.mkdir

Dir.chdir work_dir do
  ohai "Downloading deployment resources..."
  system "/bin/bash -o pipefail -c '/usr/bin/curl -sSfL https://github.com/serc/wave/tarball/deploy | /usr/bin/tar xz -m --strip 1'"

  ohai "Writing configuration info..."
  config_file = File.open('deploy-config.json', 'w')
  config_file.write JSON.dump(config)
  config_file.close

  ohai "Running Chef..."
  sudo "chef-solo", "-c deploy.rb", "-j deploy-config.json"
end

ohai "Installation successful!"
warn "In order to use MATLAB matlab components, you will need to install MATLAB." unless Kernel.system "/usr/bin/which -s matlab"

