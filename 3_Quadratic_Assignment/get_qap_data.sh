mkdir -p data/qap/problem
cd data/qap/problem
curl -O https://qaplib.mgi.polymtl.ca/data.d/qapdata.tar.gz
gunzip qapdata.tar.gz
tar -xvf qapdata.tar

mkdir -p ../solutions
cd ../solutions
curl -O https://qaplib.mgi.polymtl.ca/soln.d/qapsoln.tar.gz
gunzip qapsoln.tar.gz
tar -xvf qapsoln.tar
