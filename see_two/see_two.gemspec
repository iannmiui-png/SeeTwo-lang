require_relative "lib/see_two/version"
Gem::Specification.new do |s|
  s.name        = "see_two"
  s.version     = "0.1.0"
  s.summary     = "See Two? esoteric language interpreter"
  s.description = "Compact interpreter for the See Two? esolang (C2xC2xC2 + Dodecahedron)."
  s.authors     = ["You"]
  s.email       = ["you@example.com"]
  s.files       = Dir["lib/**/*.rb"] + ["exe/see_two"]
  s.executables = ["see_two"]
  s.require_paths = ["lib"]
  s.homepage    = ""
  s.license     = "MIT"
  s.add_development_dependency "rspec"
end
