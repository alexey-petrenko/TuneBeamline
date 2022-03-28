#!/usr/bin/env python3

import json, os, sys
import numpy as np

resp_file='responses.json'
if len(sys.argv) > 1:
    resp_file = sys.argv[1]

if os.path.exists(resp_file):
    with open(resp_file, "r") as f:
        cfg = json.load(f)
        var_dict = {}
        for name, itm in cfg["response data"].items():
            observed, varied = name.split(" / ")
            if varied in var_dict:
                var_dict[varied].append(observed)
            else:
                var_dict[varied] = [observed]

        for name, itm in var_dict.items():
            print(f"{name}: {itm}")
else:
    print(f"No {resp_file} file to plot!")

#input("Press Enter.")