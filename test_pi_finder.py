from pi_finder import (bw_rows, compute_pi_digits, digits_to_letters,
                       find_all, find_shape)

PI_100K = compute_pi_digits(100_000)  # computed once and shared by the tests


# ---------- compute_pi_digits ----------

def test_first_50_digits():
    assert compute_pi_digits(50) == "14159265358979323846264338327950288419716939937510"


def test_returns_requested_length():
    assert len(compute_pi_digits(1234)) == 1234


def test_more_digits_do_not_change_earlier_ones():
    assert compute_pi_digits(100) == PI_100K[:100]


# ---------- find_all ----------

def test_find_all_counts_overlapping_matches():
    assert find_all("abababa", "aba") == [0, 2, 4]


def test_find_all_returns_empty_list_when_missing():
    assert find_all("12345", "9") == []


def test_feynman_point():
    assert find_all(PI_100K, "999999") == [761]  # digit 762, counting from 1


# ---------- digits_to_letters ----------

def test_digit_pairs_become_letters():
    # 00 -> A, 01 -> B, 25 -> Z, 26 -> A again (pair % 26)
    assert digits_to_letters("00012526") == "ABZA"


def test_odd_trailing_digit_is_ignored():
    assert digits_to_letters("000") == "A"


def test_words_in_pi_letters():
    letters = digits_to_letters(PI_100K)
    assert find_all(letters, "PIE")[0] == 10961
    assert find_all(letters, "CAT")[0] == 22730
    assert find_all(letters, "DOG")[0] == 44144


def test_shifted_letters_use_the_other_alignment():
    shifted = digits_to_letters(PI_100K[1:])
    assert find_all(shifted, "PIE")[:2] == [4425, 4430]


# ---------- bw_rows and find_shape ----------

def test_bw_rows_maps_0_to_4_black_and_5_to_9_white():
    assert bw_rows("0123456789", 5) == ["00000", "11111"]


def test_bw_rows_drops_a_partial_last_row():
    assert bw_rows("012345", 4) == ["0000"]


def test_find_shape_single_match():
    rows = ["0000", "0110", "0110", "0000"]
    assert find_shape(rows, ["11", "11"]) == [(1, 1)]


def test_find_shape_counts_overlapping_matches():
    rows = ["000", "000", "000"]
    assert find_shape(rows, ["00", "00"]) == [(0, 0), (0, 1), (1, 0), (1, 1)]


def test_find_shape_no_match():
    assert find_shape(["01", "10"], ["11", "11"]) == []


def test_black_squares_in_pi():
    rows = bw_rows(PI_100K, 100)
    three = find_shape(rows, ["000"] * 3)
    assert len(three) == 167 and three[0] == (9, 8)
    assert find_shape(rows, ["0000"] * 4) == [(502, 71)]