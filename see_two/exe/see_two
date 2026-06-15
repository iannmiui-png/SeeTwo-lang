#!/usr/bin/env ruby
require "see_two"

if ARGV.empty?
  puts "Usage: see_two <file.st2>"
  exit 1
end

path = ARGV[0]
begin
  SeeTwo.run_file(path)
rescue Errno::ENOENT
  STDERR.puts "File not found: #{path}"
  exit 2
end
