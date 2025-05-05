from concord232 import concord_tokens

def test_decode_text_tokens_basic():
    # 'HELLO' (0x76 0x15 0x1D 0x1D 0x1F)
    tokens = [0x76, 0x15, 0x1D, 0x1D, 0x1F]
    result = concord_tokens.decode_text_tokens(tokens)
    assert 'HELLO' in result

def test_decode_text_tokens_special():
    # 'A', backspace, 'B' should yield 'B'
    tokens = [0x11, 0xFD, 0x12]
    result = concord_tokens.decode_text_tokens(tokens)
    assert result == 'B'

def test_decode_text_tokens_word_tokens():
    # 'GARAGE DOOR' (0x70, 0x2B, 0x57)
    tokens = [0x70, 0x2B, 0x57]
    result = concord_tokens.decode_text_tokens(tokens)
    assert 'GARAGE' in result and 'DOOR' in result 