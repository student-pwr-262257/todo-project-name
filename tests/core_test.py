from todo_project_name.core import mod_exp

def test_mod_exp()->None:
    for i in range(2,561):
        assert mod_exp(i,560,561)==1 #First Carmicheal number
    for i in range(2,1729):
        assert mod_exp(i,1728,1729)==1 #Second Carmichael number
    for i in range(2,7):
        assert mod_exp(i,6,7)==1 #True by Fermat's little theorem
    test_cases = [
            (287,479,373,55),
            (73,666,100,89),
            (44,666,66,22),
            (1905,53,44,41),
            (2022,44,666,342)]
    for b, e, m, result in test_cases:
        assert mod_exp(b,e,m) == result

if __name__ == "__main__":
    test_mod_exp()
    print("Test passed")