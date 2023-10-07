import sys
sys.path.append('/mnt/wch/registry_ecos')

print(f'Type of sys.path: {type(sys.path)}')
if isinstance(sys.path, (list, tuple)):
    sys.path = sys.path[::-1]

from src.analysis.callable import Bandit4MalCallable, CALLABLE_ANALYSERS, CallableAnalyser

if __name__ == "__main__":
    d = "/mnt/wch/oss_security_repos/pypi_malregistry/yptt"
    # d = "/mnt/wch/oss_security_repos/pypi_malregistry"
    # d = "/mnt/wch/oss_malicious_repos/py_mal_pkgs_by_BKC"
    
    # bmc = Bandit4MalCallable()
    # analysis_result = bmc(d, flat_subproj=True)

    ca = CallableAnalyser(CALLABLE_ANALYSERS.Bandit4MalCallable, verbose=True)
    analysis_result = ca.analyse(d)
    
    import json
    with open('bandit_analysis_result.json', 'w') as f:
        json.dump(analysis_result, f, indent=4)