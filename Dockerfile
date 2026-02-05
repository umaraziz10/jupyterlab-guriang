FROM jupyter/datascience-notebook:latest

USER root

# 1. Install Dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    octave \
    gnuplot \
    ghostscript \
    less \
    bzip2 \
    build-essential \
    munge \
    libmunge-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# 2. Copy File Slurm Lokal ke dalam Image
COPY slurm-20.11.8.tar.bz2 /tmp/slurm-20.11.8.tar.bz2

# 3. Compile & Install Slurm 20.11.8
RUN cd /tmp && \
    tar -xvf slurm-20.11.8.tar.bz2 && \
    cd slurm-20.11.8 && \
    ./configure --prefix=/usr --sysconfdir=/etc/slurm --disable-debug && \
    make -j$(nproc) && \
    make install && \
    cd /tmp && \
    rm -rf slurm-20.11.8 slurm-20.11.8.tar.bz2

# 4. Setup Folder Dasar Munge & Slurm
RUN mkdir -p /var/log/slurm && \
    mkdir -p /var/run/munge && \
    chown -R munge:munge /var/run/munge /etc/munge && \
    chmod 777 /var/run/munge && \
    mkdir -p /etc/slurm

# 5. Install Python Kernels
RUN pip install --no-cache-dir octave_kernel gnuplot_kernel

# 6. Register Kernels
RUN python -m octave_kernel install --sys-prefix && \
    python -m gnuplot_kernel install --sys-prefix

# 7. Julia Setup
RUN julia -e 'using Pkg; Pkg.build("IJulia")'

# 8. Custom Package
COPY guriang /tmp/guriang
RUN SITE_PACKAGES=$(python -c "import site; print(site.getsitepackages()[0])") && \
    mv /tmp/guriang "$SITE_PACKAGES/guriang" && \
    chmod +x "$SITE_PACKAGES/guriang/sync"

COPY start-with-slurm.sh /usr/local/bin/start-with-slurm.sh
RUN chmod +x /usr/local/bin/start-with-slurm.sh

# 9. Start with specific logged in users
USER ${NB_UID}
