"""Tests for git-bus-factor core logic."""
import sys
sys.path.insert(0, '/tmp/git-bus-factor')
from bus_factor import compute_bus_factor, compute_concentration_score

def test_bus_factor_single_author():
    authors = {"Alice": 100}
    assert compute_bus_factor(authors) == 1, "Single author should have bus factor 1"

def test_bus_factor_two_equal_authors():
    authors = {"Alice": 50, "Bob": 50}
    # Together they own 100%, each owns 50%. Threshold 0.5: first author hits it.
    assert compute_bus_factor(authors) == 1

def test_bus_factor_many_even_authors():
    authors = {f"dev{i}": 10 for i in range(10)}
    # Each owns 10%; need 5 to reach 50%
    assert compute_bus_factor(authors) == 5

def test_bus_factor_empty():
    assert compute_bus_factor({}) == 0

def test_concentration_single_author():
    assert compute_concentration_score({"Alice": 100}) == 1.0

def test_concentration_equal_authors():
    authors = {"Alice": 50, "Bob": 50}
    score = compute_concentration_score(authors)
    assert score == 0.0, f"Equal split should have 0 concentration, got {score}"

def test_concentration_dominant_author():
    authors = {"Alice": 90, "Bob": 10}
    score = compute_concentration_score(authors)
    assert score > 0.5, f"Dominant author should have high concentration, got {score}"

def test_concentration_range():
    for distribution in [{"A": 100}, {"A": 70, "B": 30}, {"A": 50, "B": 25, "C": 25}]:
        score = compute_concentration_score(distribution)
        assert 0.0 <= score <= 1.0, f"Score out of range: {score} for {distribution}"

if __name__ == "__main__":
    tests = [
        test_bus_factor_single_author,
        test_bus_factor_two_equal_authors,
        test_bus_factor_many_even_authors,
        test_bus_factor_empty,
        test_concentration_single_author,
        test_concentration_equal_authors,
        test_concentration_dominant_author,
        test_concentration_range,
    ]
    passed = 0
    for t in tests:
        try:
            t()
            print(f"  PASS  {t.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"  FAIL  {t.__name__}: {e}")
    print(f"\n{passed}/{len(tests)} tests passed")
    sys.exit(0 if passed == len(tests) else 1)
