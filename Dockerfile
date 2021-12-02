FROM registry.access.redhat.com/ubi8/ubi@sha256:8ee9d7bbcfc19d383f9044316a5c5fbcbe2df6be3c97f6c7a5422527b29bdede

RUN dnf install -y jq python39 git wget unzip

RUN mkdir -p /opt/app-root/src/.local/bin
RUN wget "https://github.com/vmware/govmomi/releases/download/v0.27.2/govc_Linux_x86_64.tar.gz"
RUN tar xf govc_Linux_x86_64.tar.gz
RUN mv govc /usr/local/bin

RUN wget "https://mirror.openshift.com/pub/openshift-v4/clients/ocp/stable-4.9/openshift-client-linux.tar.gz"
RUN tar xf openshift-client-linux.tar.gz
RUN mv oc /usr/local/bin
RUN mv kubectl /usr/local/bin

RUN wget "https://mirror.openshift.com/pub/openshift-v4/clients/ocp/latest-4.9/openshift-install-linux.tar.gz"
RUN tar xf openshift-install-linux.tar.gz
RUN mv openshift-install /usr/local/bin

RUN python3 -m ensurepip --upgrade
RUN pip3 install pyyaml

RUN mkdir /opt/app-root/src/release
RUN git clone https://github.com/openshift/release.git /opt/app-root/src/release

RUN mkdir /var/lib/openshift-installer
RUN git clone https://github.com/openshift/installer/ /var/lib/openshift-install

RUN wget "https://releases.hashicorp.com/terraform/0.13.4/terraform_0.13.4_linux_amd64.zip"
RUN unzip terraform_0.13.4_linux_amd64.zip
RUN mv terraform /opt/app-root/src/.local/bin
COPY openshift-tests /usr/local/bin
COPY run.py /opt/app-root/src
WORKDIR /opt/app-root/src
