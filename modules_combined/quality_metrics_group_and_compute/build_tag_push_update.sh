# Run from root repository (NEON-IS-data-processing)
#!/usr/bin/env bash
image_name=neon-is-qaqc-qm-grp
tag=$(git rev-parse --short HEAD)
docker build -t $image_name:latest -f ./modules_combined/quality_metrics_group_and_compute/Dockerfile .
docker tag $image_name quay.io/battelleecology/$image_name:$tag
docker push quay.io/battelleecology/$image_name:$tag

Rscript ./utilities/flow.img.updt.R "./pipe" ".yaml" "quay.io/battelleecology/$image_name" "$tag"
