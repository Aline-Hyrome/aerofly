def test(test, nom_test="Test"):
    try:
        assert test
        print("%s passed" %nom_test)
    except AssertionError as e:
        print("%s not passed: %s" %(nom_test, e))
