FROM ubuntu:22.04

# Set environment variable for soft directory
ENV SOFT=/soft

# Create the soft directory
RUN mkdir -p $SOFT

# Install essential general packages for building software
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libncurses5-dev \
    zlib1g-dev \
    libncursesw5-dev \
    libbz2-dev \
    liblzma-dev \
    autoconf \
    automake \
    libtool \
    pkg-config \
    cmake \
    perl \
    git \
    wget \
    python3 \
    python3-pip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Check if tar is installed, and install it if not
RUN if ! dpkg -l | grep -q tar; then \
        apt-get update && \
        apt-get install -y tar && \
        apt-get clean && \
        rm -rf /var/lib/apt/lists/*; \
    fi

# Install samtools
RUN cd $SOFT && \
    # Command Works to get the latest version
    LATEST_VERSION=$(wget -qO- https://api.github.com/repos/samtools/samtools/releases/latest | grep -oP '"tag_name": "\K(.*)(?=")') && \
    wget https://github.com/samtools/samtools/releases/download/$LATEST_VERSION/samtools-$LATEST_VERSION.tar.bz2 && \
    tar -xjf samtools-$LATEST_VERSION.tar.bz2 && \
    cd samtools-$LATEST_VERSION && \
    ./configure --prefix=$SOFT/samtools-$LATEST_VERSION && \
    make -j$(nproc) && \
    make install && \
    cd .. && \
    echo "LATEST_VERSION=${LATEST_VERSION}" > $SOFT/samtools_version.env && \ 
    echo "export SAMTOOLS=$SOFT/samtools-$LATEST_VERSION/bin/samtools" >> ~/.bashrc && \
    rm -rf samtools-$LATEST_VERSION.tar.bz2


# Install htslib
RUN cd $SOFT && \
    # Command Works to get the latest version
    LATEST_VERSION=$(wget -qO- https://api.github.com/repos/samtools/htslib/releases/latest | grep -oP '"tag_name": "\K(.*)(?=")') && \
    wget https://github.com/samtools/htslib/releases/download/$LATEST_VERSION/htslib-$LATEST_VERSION.tar.bz2 && \
    tar -xjf htslib-$LATEST_VERSION.tar.bz2 && \
    cd htslib-$LATEST_VERSION && \
    ./configure --prefix=$SOFT/htslib-$LATEST_VERSION && \
    make -j$(nproc) && \
    make install && \
    cd .. && \
    echo "LATEST_VERSION=${LATEST_VERSION}" > $SOFT/htslib_version.env && \
    echo "export HTSLIB=$SOFT/htslib-$LATEST_VERSION/bin/htsfile" >> ~/.bashrc && \
    echo "export HTSLIB_ANNOT_TSV=$SOFT/htslib-$LATEST_VERSION/bin/annot-tsv" >> ~/.bashrc && \
    echo "export HTSLIB_BGZIP=$SOFT/htslib-$LATEST_VERSION/bin/bgzip" >> ~/.bashrc && \
    echo "export HTSLIB_TABIX=$SOFT/htslib-$LATEST_VERSION/bin/tabix" >> ~/.bashrc && \
    rm -rf htslib-$LATEST_VERSION.tar.bz2

# Install libdeflate
RUN cd $SOFT && \
    # Command Works to get the latest version
    LATEST_VERSION=$(wget -qO- https://api.github.com/repos/ebiggers/libdeflate/releases/latest | grep -oP '"tag_name": "\K(.*)(?=")' | sed 's/^v//') && \
    wget https://github.com/ebiggers/libdeflate/archive/refs/tags/v$LATEST_VERSION.tar.gz && \
    tar -xzf v$LATEST_VERSION.tar.gz && \
    cd libdeflate-$LATEST_VERSION && \
    mkdir build && cd build && \
    cmake .. && \
    make -j$(nproc) && \
    make install DESTDIR=$SOFT/libdeflate-$LATEST_VERSION && \
    cd .. && \
    # # Cleaning build, cmake and tar.archive
    rm -rf build && \
    rm -rf /soft/v$LATEST_VERSION.tar.gz && \
    apt-get purge -y cmake && \
    rm -rf /var/lib/apt/lists/* && \
    # #
    echo "LATEST_VERSION=${LATEST_VERSION}" > $SOFT/libdeflate_version.env && \
    echo "export LIBDEFLATEGUNZIP=$SOFT/libdeflate-$LATEST_VERSION/usr/local/bin/libdeflate-gunzip" >> ~/.bashrc && \
    echo "export LIBDEFLATEGZIP=$SOFT/libdeflate-$LATEST_VERSION/usr/local/bin/libdeflate-gzip" >> ~/.bashrc

# Install bcftools
RUN cd $SOFT && \
    LATEST_VERSION=$(wget -qO- https://api.github.com/repos/samtools/bcftools/releases/latest | grep -oP '"tag_name": "\K(.*)(?=")') && \
    wget https://github.com/samtools/bcftools/releases/download/$LATEST_VERSION/bcftools-$LATEST_VERSION.tar.bz2 && \
    tar -xjf bcftools-$LATEST_VERSION.tar.bz2 && \
    cd bcftools-$LATEST_VERSION && \
    ./configure --prefix=$SOFT/bcftools-$LATEST_VERSION && \
    make -j$(nproc) && \
    make install && \
    cd .. && \
    echo "LATEST_VERSION=${LATEST_VERSION}" > $SOFT/bcftools_version.env && \
    echo "export BCFTOOLS=$SOFT/bcftools-$LATEST_VERSION/bin/bcftools" >> ~/.bashrc && \
    rm -rf bcftools-$LATEST_VERSION.tar.bz2

# Install vcftools
RUN cd $SOFT && \
    LATEST_VERSION=$(wget -qO- https://api.github.com/repos/vcftools/vcftools/releases/latest | grep -oP '"tag_name": "\K(.*)(?=")' | sed 's/^v//') && \
    wget https://github.com/vcftools/vcftools/releases/download/v$LATEST_VERSION/vcftools-$LATEST_VERSION.tar.gz && \
    tar -xzf vcftools-$LATEST_VERSION.tar.gz && \
    cd vcftools-$LATEST_VERSION/ && \
    ./autogen.sh && \
    ./configure --prefix=$SOFT/vcftools-$LATEST_VERSION && \
    make -j$(nproc) && \
    make install && \
    cd .. && \
    echo "LATEST_VERSION=${LATEST_VERSION}" > $SOFT/vcftools_version.env && \
    echo "export VCFTOOLS=$SOFT/vcftools-$LATEST_VERSION/bin/vcftools" >> ~/.bashrc && \
    rm -rf vcftools-$LATEST_VERSION.tar.gz

# Install Python dependencies
RUN pip3 install -U Cython pandas pysam

# Copy the Python script into the container
COPY FP_SNPs_processing_2.py /app/FP_SNPs_processing_2.py
COPY VCFtools_wrapper.sh $SOFT/vcftools-0.1.16/

RUN cd $SOFT && \
    LATEST_VERSION=$(wget -qO- https://api.github.com/repos/vcftools/vcftools/releases/latest | grep -oP '"tag_name": "\K(.*)(?=")' | sed 's/^v//') && \
    echo "LATEST_VERSION=${LATEST_VERSION}" > $SOFT/vcftools_version.env && \
    echo "export VCFTOOLS=$SOFT/vcftools-$LATEST_VERSION/VCFtools_wrapper.sh" >> ~/.bashrc

# Set environment variables
ENV SAMTOOLS="$SOFT/samtools-1.20/bin/" \
    HTSLIB="$SOFT/htslib-1.20/bin/" \
    LIBDEFLATE="$SOFT/libdeflate-1.21/usr/local/bin/" \
    BCFTOOLS="$SOFT/bcftools-1.20/bin/" \
    VCFTOOLS="$SOFT/vcftools-0.1.16/VCFtools_wrapper.sh"

# Set the working directory
WORKDIR /app

# Command to run the Python script (modify as needed)
CMD ["python3", "FP_SNPs_processing_2.py"]