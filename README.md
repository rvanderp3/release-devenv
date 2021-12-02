# Overview

Verifying the functionality of PRs in the `release` repo is timely and expensive(from both a developer and cloud cost) perspective. The intent of this project is to provide a development environment where changes to the `release` repo can be verified locally while still working with real cloud backends.  This environment is not intended to replace verifying a PR via `pj-rehearse`.  It is solely intended to allow faster iteration of changes and
allow mocking of configurations that are not readily possible with `pj-rehearse` today.  For example, I need to run job `x` against version `y`.  This environment is presently skewed towards development of periodics.

This project is not a 'turn-key' solution. You must be knowledgable, to an extent, on how the `release` repo runs workflows. 

## Requirements

- Kubernetes cluster which will host secrets and act as the executor the CI workflow
- Container registry which will host image with required tools, installer, and openshift-tests
- Necessary credentials to install in your cloud of choice



## Building a Kubernetes Cluster

This workflow was tested with a [kind](https://kind.sigs.k8s.io/) cluster.  All secrets and pods were created in the `default` namespace.

## Building a Workflow Runner Image

The example below builds an image with the following attributes:
- Required tooling needed by CI workflows. This will vary based on the workflows you're running.
- Based on ubi8
- Packages installer and oc clients
- Packages openshift-tests

See `Dockerfile` for an example.

Note: Credentials are __not__ provisioned in the image. They are mounted at runtime.  

## Starting the Image

Below is an example pod spec that deploys a container where workflows are executed. Check each of the environment variables below to determine if they are applicable to the workflow you're running. Not all(most) are relevant to the actual execution of a workflow.


See `pod.yaml` for an example.

## Executing the Workflow

The `JOB_NAME_SAFE` environment variable determines which workflow is executed by run.py.  To run a workflow, create and rsh to the `e2e-workflow-runner` pod.

~~~ bash
$ oc create -f pod.yaml
$ oc rsh e2e-workflow-runner
(app-root) sh-4.4$ python run.py
workflow[openshift-e2e-vsphere-upi-serial] phase[pre]
ref:[ipi-install-rbac]----> /opt/app-root/src/release/ci-operator/step-registry/ipi/install/rbac/ipi-install-rbac-commands.sh
skipping ref
ref:[openshift-cluster-bot-rbac]----> /opt/app-root/src/release/ci-operator/step-registry/openshift/cluster-bot/rbac/openshift-cluster-bot-rbac-commands.sh
skipping ref
chain:[upi-vsphere-pre]-->
ref:[ipi-conf]----> /opt/app-root/src/release/ci-operator/step-registry/ipi/conf/ipi-conf-commands.sh
Installing from release registry.ci.openshift.org/ocp/release:4.10.0-0.nightly-2021-12-01-210213
error encountered in[/opt/app-root/src/release/ci-operator/step-registry/ipi/conf/ipi-conf-ref.yaml]
ref:[ipi-conf-vsphere-check]----> /opt/app-root/src/release/ci-operator/step-registry/ipi/conf/vsphere/check/ipi-conf-vsphere-check-commands.sh
Scheduling job on IBM Cloud instance
2021-12-02 18:11:58+00:00 - Creating govc.sh file...
2021-12-02 18:11:58+00:00 - Creating vsphere_context.sh file...
2021-12-02 18:11:58+00:00 - Find virtual machines attached to ci-segment-98 and destroy
~~~

## Secrets

Perhaps the most challenging aspects of setting up this environment is the management of secrets necessary to interact with the cloud in question.  This step might not be critical if the scripts you are testing don't need to actually communicated with a cloud(i.e. you're troubleshooting some syntax issue in a bash script).  

~~~ yaml
apiVersion: v1
kind: Secret
metadata:
  name: ibm-cloud-vmware-creds
data:
  secrets.sh: "...Cg=="
  secret.auto.tfvars: "...Igo="

~~~

~~~ yaml
apiVersion: v1
kind: Secret
metadata:
  name: cluster-profile
data:
  ssh-publickey: "c3N...nYK"
  ssh-privatekey: "c3N...nYK"
  pull-secret: "ey...19Cg=="
~~~


