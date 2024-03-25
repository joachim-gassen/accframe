FROM rocker/r-ver:4.2

RUN apt clean && apt update 
RUN apt-get -y install cmake git pandoc libxml2-dev libcurl4-openssl-dev && apt-get clean
RUN apt-get -y install libssl-dev libgit2-dev wget libfontconfig1-dev && apt-get clean
RUN apt-get -y install libharfbuzz-dev libfribidi-dev librsvg2-dev && apt-get clean
RUN apt-get -y install libfreetype6-dev libpng-dev libtiff5-dev 
RUN apt-get -y install libpq-dev libjpeg-dev && apt-get clean
RUN apt-get -y install texlive && apt-get clean
RUN apt-get -y install texlive-latex-extra && apt-get clean
RUN apt-get -y install texlive-xetex && apt-get clean
RUN apt-get -y install texlive-science && apt-get clean
RUN apt-get -y install texlive-fonts-extra && apt-get clean
RUN apt-get -y install ghostscript && apt-get clean
RUN apt-get -y install python3 && apt-get clean
RUN apt-get -y install apt install python3-venv && apt-get clean
RUN apt-get -y install apt install python3-wheel && apt-get clean

RUN install2.r --error --skipinstalled tidyverse 
RUN install2.r --error --skipinstalled lubridate 
RUN install2.r --error --skipinstalled knitr
RUN install2.r --error --skipinstalled kableExtra
RUN install2.r --error --skipinstalled rmarkdown 
RUN install2.r --error --skipinstalled modelsummary 
RUN install2.r --error --skipinstalled ggbeeswarm 
RUN install2.r --error --skipinstalled devtools
RUN install2.r --error --skipinstalled xml2
RUN install2.r --error --skipinstalled countrycode
RUN install2.r --error --skipinstalled gt
RUN install2.r --error --skipinstalled showtext
RUN install2.r --error --skipinstalled quarto
RUN install2.r --error --skipinstalled languageserver
RUN install2.r --error --skipinstalled rsconnect
RUN install2.r --error --skipinstalled ggwordcloud
RUN install2.r --error --skipinstalled tidytext

RUN rm -rf /tmp/downloaded_packages

ARG TARGETARCH
RUN QUARTO_VERSION=1.4.550 \
    && if [ $TARGETARCH = "arm64" ]; then \
        QUARTO_ARCH=linux-arm64; \
        else QUARTO_ARCH=linux-amd64; \
    fi \
    && wget -O quarto.deb https://github.com/quarto-dev/quarto-cli/releases/download/v${QUARTO_VERSION}/quarto-${QUARTO_VERSION}-${QUARTO_ARCH}.deb \
    && dpkg -i quarto.deb \
    && rm quarto.deb

CMD /bin/sh

