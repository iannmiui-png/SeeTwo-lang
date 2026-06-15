require_relative 'lib/see_two'
src = File.read('examples/Dodecahedron.st2', encoding: 'utf-8')
tokens = SeeTwo::Tokenizer.tokenize(src)
p tokens
rt = SeeTwo::Interpreter.new(tokens)
out = rt.run
puts "#{out.inspect}"
puts "G#{rt.group},D2#{rt.dodec}"
