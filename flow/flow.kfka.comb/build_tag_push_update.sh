# Run from root repository (NEON-IS-data-processing)
#!/usr/bin/env bash
image_name=neon-is-kfka-comb-r
tag=$(git rev-parse HEAD)
cd ./flow/flow.kfka.comb
docker build -t $image_name:latest .
docker tag $image_name quay.io/battelleecology/$image_name:$tag
docker push quay.io/battelleecology/$image_name:$tag
cd ../..

Rscript ./utilities/flow.img.updt.R "./pipe" ".yaml" "quay.io/battelleecology/$image_name" "$tag"