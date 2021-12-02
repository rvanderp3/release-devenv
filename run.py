import os
import yaml
import subprocess

workflow=os.environ['JOB_NAME_SAFE']
path="/opt/app-root/src/release"
skipJobs=["ipi-install-rbac", "openshift-cluster-bot-rbac"]

def scan_dir_for(type, path, name, pathParts=""):        
    if os.path.isfile(path):
        filename = os.path.basename(path)
        if filename == name + "-" + type + ".yaml":
            return path
        else:
            return 

    for filename in os.listdir(path):        
        if os.path.isfile(filename):
            pass
        if pathParts != "":
            thisPath = filename
        else:
            thisPath = "-" + filename
        foundPath = scan_dir_for(type, path + "/" + filename, name, thisPath)
        if foundPath != None:
            return foundPath

def processRef(ref):
    global path
    refPath = scan_dir_for("ref", path, ref)
    if refPath == None:
        print("ref[" + ref + "] not found")
        return 1
    with open(refPath, "r") as stream:
        try:
            ref = yaml.safe_load(stream)            
            ref = ref["ref"]
            shPath = os.path.dirname(refPath) + "/" + ref["commands"]
            print("ref:["+ref["as"]+"]----> " + shPath)
            for job in skipJobs:
                if job in ref["as"]:
                    print("skipping ref")
                    return 0
            return subprocess.run(["bash" , shPath])
        except yaml.YAMLError as exc:
            print(exc)
    return 1

def processChain(chain):
    global path
    chainPath = scan_dir_for("chain", path, chain)
    if chainPath == None:
        print("chain[" + chain + "] not found")
        return 1
    with open(chainPath, "r") as stream:
        try:
            chain = yaml.safe_load(stream)            
            if "chain" not in chain:
                print("yaml is not a chain")
                return
            chain = chain["chain"]
            steps = chain["steps"]
            for step in steps:
                if "ref" in step:                    
                    return processRef(step["ref"])                   
                if "chain" in step:
                    print("chain:["+chain["as"]+"]-->")
                    return processChain(step["chain"])
                    
        except yaml.YAMLError as exc:
            print(exc)
    return 1            

def processWorkflow(workflow):
    global path
    workflowPath = scan_dir_for("workflow", path, workflow)
    if workflowPath == None:
        print("workflow[" + workflow + "] not found")
        return
    with open(workflowPath, "r") as stream:
        try:
            workflow = yaml.safe_load(stream)            
            if "workflow" not in workflow:
                print("yaml is not a workflow")
                return
            workflow = workflow["workflow"]
            steps = workflow["steps"]
            stepTypes = ["pre", "test", "post"]
            for stepType in stepTypes:                
                if stepType in steps:
                    print("workflow["+workflow["as"]+"] phase["+stepType+"]")
                    preSteps = steps[stepType]
                    for step in preSteps:    
                        if "ref" in step:
                            if processRef(step["ref"]) != 0 and stepType == "pre":
                                print("step failed. exiting 'pre' chain")
                                break
                        elif "chain" in step:                            
                            if processChain(step["chain"]) !=0 and stepType == "pre":
                                print("chain failed. exiting 'pre' chain")
                                break
                        else:
                            print("unrecognized step class - " + step)
                    
        except yaml.YAMLError as exc:
            print(exc)

processWorkflow(workflow)
