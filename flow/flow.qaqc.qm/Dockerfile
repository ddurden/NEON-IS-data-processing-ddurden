# Dockerfile for NEON IS Data Processing - Quality metrics and final quality flag module

# Start with the base image. 
FROM quay.io/battelleecology/neon-is-pack-qaqc-r:v1.1.4

# maintainer handle
MAINTAINER "Cove Sturtevant" csturtevant@battelleecology.org

# Copy the lockfile and restore known working versions of R dependency packages
COPY ./renv.lock /renv.lock
RUN R -e 'renv::restore(lockfile="/renv.lock")'

# Create app user
RUN groupadd app && \
    useradd app -g app
WORKDIR /home/app

# Copy in application code
COPY ./flow.qaqc.qm.R .
COPY ./wrap.qaqc.qm.R .

# Run as app user
RUN chown app:app -R /home/app
USER app
