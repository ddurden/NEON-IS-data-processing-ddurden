# Run from root repository (NEON-IS-data-processing)
#!/usr/bin/env bash
image_name=replace_macaddress_with_assetuid
tag=$(git rev-parse HEAD)
cd ./modules
docker build -t $image_name:latest -f ./replace_macaddress_with_assetuid/Dockerfile .
docker tag $image_name quay.io/battelleecology/$image_name:$tag
docker push quay.io/battelleecology/$image_name:$tag
cd ..
Rscript ./utilities/flow.img.updt.R "./pipe" ".yaml" "quay.io/battelleecology/$image_name" "$tag"