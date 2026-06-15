require "spec_helper"

RSpec.describe SeeTwo do
  it "toggles group axes" do
    tokens = SeeTwo::Tokenizer.tokenize("c d D h")
    rt = SeeTwo::Interpreter.new(tokens)
    rt.run
    expect(rt.group).to eq(0b111)
  end

  it "rotates dodec left" do
    tokens = SeeTwo::Tokenizer.tokenize("\u04C0 e h")
    rt = SeeTwo::Interpreter.new(tokens)
    rt.run
    expect(rt.dodec).to eq(0b0010)
  end

  it "outputs numeric values" do
    tokens = SeeTwo::Tokenizer.tokenize("n c n h")
    rt = SeeTwo::Interpreter.new(tokens)
    out = rt.run
    expect(out).to include("0")
    expect(out).to include("1")
  end

  it "expands pcx tokens" do
    tokens = SeeTwo::Tokenizer.tokenize("zCeq.pcx zCdo.pcx h")
    expect(tokens).to include('c')
    expect(tokens).to include('D')
  end
end
