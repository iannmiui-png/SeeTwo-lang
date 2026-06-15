# frozen_string_literal: true
module SeeTwo
  module Tokenizer
    PALOCHKA = "\u04C0" # Ӏ

    PCX_TO_PGM = {
      "zCeq.pcx" => "≓",
      "zCdo.pcx" => "☻",
      "zCha.pcx" => "♦",
      "zCit.pcx" => "♥"
    }.freeze

    PRIMITIVE_TO_OPS = {
      "=" => "c",
      "♥" => "D",
      "♦" => "e"
    }.freeze

    PHRASE_TO_PALOCHKA = {
      "Dodecahedron" => PALOCHKA * 2,
      "Dodecahedron dodecahedra"  => PALOCHKA * 4 *
    }.freeze

    module_function

    def normalize(src)
      src.to_s.gsub("\r\n", "\n").gsub("\r", "\n")
    end

    def expand_pcx(src)
      s = src.dup
      PHRASE_TO_PALOCHKA.each { |k, v| s.gsub!(/\b#{Regexp.escape(k)}\b/i, v) }
      PCX_TO_PGM.each { |k, v| s.gsub!(k, v) }
      s
    end

    def tokenize(src)
      s = normalize(src)
      s = expand_pcx(s)
      tokens = []
      i = 0
      while i < s.length
        ch = s[i]
        if ch == PALOCHKA
          j = i
          j += 1 while j < s.length && s[j] == PALOCHKA
          tokens << s[i...j]
          i = j
          next
        end

        if ch =~ /\s/
          i += 1
          next
        end

        tokens << ch
        i += 1
      end

      # expand single-character primitives into op sequences
      expanded = []
      tokens.each do |t|
        if PRIMITIVE_TO_OPS.key?(t)
          PRIMITIVE_TO_OPS[t].each_char { |c| expanded << c }
        else
          expanded << t
        end
      end

      expanded
    end
  end
end
