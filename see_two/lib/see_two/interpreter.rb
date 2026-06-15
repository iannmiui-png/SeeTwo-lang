# frozen_string_literal: true
# old
require "see_two/tokenizer"

# new (use require_relative so running from project root works)
require_relative "tokenizer"

module SeeTwo
  class Interpreter
    PALOCHKA = Tokenizer::PALOCHKA

    attr_reader :group, :dodec, :output

    def initialize(tokens)
      @code = tokens.dup
      @ip = 0
      @group = 0      # 3 bits (0..7)
      @dodec = 0      # 4 bits (0..15)
      @acc_primary_mode = :group
      @acc_secondary_mode = :dodec
      @call_stack = []
      @running = true
      @output = []
    end

    def get_acc(which = :primary)
      mode = which == :primary ? @acc_primary_mode : @acc_secondary_mode
      mode == :group ? @group : @dodec
    end

    def set_acc(value, which = :primary)
      value &= 0xF
      if which == :primary
        if @acc_primary_mode == :group
          @group = value & 0x7
        else
          @dodec = value & 0xF
        end
      else
        if @acc_secondary_mode == :group
          @group = value & 0x7
        else
          @dodec = value & 0xF
        end
      end
    end

    def toggle_group_axis(axis)
      mask = 1 << axis
      @group ^= mask
      @group &= 0x7
    end

    def rotate_dodec_left(steps = 1)
      steps %= 4
      @dodec = ((@dodec << steps) | (@dodec >> (4 - steps))) & 0xF
    end

    def step
      return unless @running
      if @ip < 0 || @ip >= @code.length
        @running = false
        return
      end
      op = @code[@ip]
      @ip += 1

      case op
      when 'c'
        toggle_group_axis(0)
      when 'd'
        toggle_group_axis(1)
      when 'D'
        toggle_group_axis(2)
      when 'e'
        rotate_dodec_left(1)
      when 'a'
        @acc_primary_mode, @acc_secondary_mode = @acc_secondary_mode, @acc_primary_mode
      when 'o'
        val = get_acc(:primary)
        ch = (val <= 0x10 ? val.chr(Encoding::UTF_8) : '?')
        @output << ch
        print ch
      when 'n'
        val = get_acc(:primary)
        s = val.to_s
        @output << s
        print s
      when 'h'
        @running = false
      when 'r'
        if @call_stack.any?
          @ip = @call_stack.pop
        else
          addr = get_acc(:secondary)
          @ip = [[0, addr].max, @code.length].min
        end
      when /\A#{Regexp.escape(PALOCHKA)}+\z/
        @dodec = op.length & 0xF
      when '#'
        # comment / no-op
      else
        # unknown token: ignore
      end
    end

    def run(max_steps = 100_000)
      steps = 0
      while @running && steps < max_steps
        step
        steps += 1
      end
      @output.join
    end
  end
end
