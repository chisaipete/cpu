# cpu
Adventures in CPU Simulation
## setup
- Have Python 3.3.* as default version on OS (`python`)
- At base of repository run: 
    + `python -m venv venv`
    + Activate your venv: `. ./venv/bin/activate` OR `.\venv\Scripts\activate.bat`
    + `pip install --upgrade pip`
    + `pip install -r requirements.txt`
- Use the following shebang: `#!/usr/bin/env python`
- Before running any script, activate your venv: `./venv/bin/activate`
- Before releasing, use `pip freeze > requirements.txt`
    + remove `pkg-resources` line from requirements.txt
- To run tests: `python -m unittest discover`
- To run tests with coverage: `coverage run -m unittest discover`
- To generate coverage report: `coverage html --omit="*/venv*"`
- View report by opening: `./htmlcov/index.html`
- Also, in a Windows terminal, you may encounter issues when echoing unicode characters for debug purposes, so execute the following: `chcp 65001`

## ISA Targets
- [RiSC-16](https://ece.umd.edu/~blj/RiSC)
- [LC-3]()
- [LC-896]()
- [MIPS-\*]()

## References
- [BitVector](https://engineering.purdue.edu/kak/dist/BitVector-3.4.8.html)
