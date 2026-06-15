require "see_two/version"
require "see_two/tokenizer"
require "see_two/interpreter"

module SeeTwo
  # Public API: run source string or file
  def self.run_source(src)
    tokens = Tokenizer.tokenize(src)
    rt = Interpreter.new(tokens)
    rt.run
  end

  def self.run_file(path)
    src = File.read(path, encoding: "utf-8")
    run_source(src)
  end
end
