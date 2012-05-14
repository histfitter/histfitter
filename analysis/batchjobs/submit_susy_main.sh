#!/bin/bash

for ds in `cat susy_points3.txt `; do sh ./submit_susy.sh $ds; done
