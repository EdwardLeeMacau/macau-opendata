"""
  FileName      [ utils.py ]
  PacakageName  [ cmdManager ]
  Synopsis      [ utility functions ]
  Author        [ EdwardLeeMacau ]
  Reference     [  ]
"""

def myNStrCmp(str1, str2, n) -> bool:
    """
    Check whether str1 is the substring of str2, with at least n exact match.

    Parameters
    ----------
    str1, str2 : string
        String to compare

    n : int
        Number of length to compare

    Return
    ------
    bool : bool
        True if str1 is the substring of str2
    """
    str1, str2 = str1.lower(), str2.lower()

    if str1[:n] == str2[:n]:
        return True

    return False

    