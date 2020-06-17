from nose.tools import assert_equal, assert_not_equal, assert_false

from locmoss.struct import KGrams, Fingerprint
from locmoss.parser import Token
from locmoss.software import SourceFile


def get_kgrams():
    kg1 = KGrams(Token("a", 0, 0), Token("b", 1, 1), Token("c", 2, 2))
    kg1_p = KGrams(Token("a", 1, 1), Token("b", 2, 3), Token("c", 9, 11))
    kg2 = KGrams(Token("a", 0, 0), Token("b", 1, 1), Token("g", 2, 2))
    kg3 = KGrams(Token("a", 0, 0), Token("b", 1, 1))

    return kg1, kg1_p, kg2, kg3

def test_kgram_len():
    kg1, kg1_p, kg2, kg3 = get_kgrams()

    assert_equal(len(kg1), 3)
    assert_equal(len(kg1_p), 3)
    assert_equal(len(kg2), 3)
    assert_equal(len(kg3), 2)

def test_kgram_hash_eq():
    kg1, kg1_p, kg2, kg3 = get_kgrams()

    assert_equal(hash(kg1), hash(kg1_p))
    assert_equal(kg1, kg1_p)
    assert_false(kg1 is kg1_p)

    assert_not_equal(hash(kg1), hash(kg2))
    assert_not_equal(hash(kg1), hash(kg3))
    assert_not_equal(hash(kg2), hash(kg3))

    assert_not_equal(kg1, kg2)
    assert_not_equal(kg1, kg3)
    assert_not_equal(kg2, kg3)
