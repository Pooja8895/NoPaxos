# Arguments in order: protocol, #replicas, #threads per client, #client machines
# EX: python ./bench/runBench.py unreplicated 5 1 1
# To run with batching, use protocol "batch"
import sys, string
import subprocess
import os
import threading
import time
import tempfile

project = "nopaxos"
zone="us-east1-b"

def generateCmdStr(machine, remoteCmd):
    return ("gcloud compute --project \"%s\" ssh --zone \"%s\" \"%s\" --command \"%s\"") % (project, zone, machine, remoteCmd)

def timeout(p):
    print("timeout")
    if p.poll() is None:
        print("killing for processes" , p)
        p.terminate()

def runTest(protocol, numReplicas, numThreadsPerClient, numClientMachines):
    configMap = {3: "config-3"} # TODO: add others
    replicas = ["test1instance", "test2instance", "test3instance"]
    clients = ["test5instance"]
    config = configMap[numReplicas]
    sequencer = "test4instance"
    processes = []
    devNull = open(os.devnull, 'w')

    # Start sequencer for nopaxos
    tempFile = tempfile.TemporaryFile()
    if protocol == "nopaxos":
        sequencerCmd = ("sudo kill \$(ps aux | grep 'sequencer' | grep -v grep | awk '{print \$2}') > /dev/null &> /dev/null; cd /home/anjalimishra/NOPaxos; sudo ./sequencer/sequencer -C %s -c sequencer_config") % config
        process = subprocess.Popen(generateCmdStr(sequencer, sequencerCmd),
            stderr=tempFile, stdout=devNull, shell=True) 
        processes.append(process)
	print("starting sequencer processes", process)
        time.sleep(0.5)

    # Start replicas
    for i in range(0, numReplicas):
        protocolStr = protocol
        if protocol == "batch":
            protocolStr = "vr -b 64"
        replicaCmd = ("sudo lsof -t -i udp:8000 | sudo xargs kill > /dev/null &> /dev/null; cd /home/anjalimishra/NOPaxos; ./bench/replica -c %s -i %d -m %s") % (config, i, protocolStr)
        process = subprocess.Popen(generateCmdStr(replicas[i], replicaCmd),
            shell=True, stdout=devNull, stderr=devNull)
        processes.append(process)
	print("starting replica processes", process)
        time.sleep(0.5)

    # Start clients
    protocolStr = protocol
    if protocol == "batch":
        protocolStr = "vr"
    clientCmd = ("cd /home/anjalimishra/NOPaxos; rm output.txt; ./bench/client -t %d -c %s -m %s -n 1000 &> output.txt; python ./bench/combineThreadOutputs.py") % (numThreadsPerClient, config, protocolStr)
    clientProcesses = []
    timers = []
    totThroughput = 0.0
    totLatency = 0.0
    for i in reversed(list(range(0, numClientMachines))):
        process = subprocess.Popen(generateCmdStr(clients[i], clientCmd),
            shell=True, stdout=subprocess.PIPE, stderr=devNull)
        t = threading.Timer(60, timeout, [process])
        print("starting client processes", t)
	t.start()
        timers.append(t)
        clientProcesses.append(process)

    try:
        for i in reversed(list(range(0, numClientMachines))):
            output = clientProcesses[i].stdout.read()
            outputLines = output.splitlines()
            elems = outputLines[0].split(":")
            totThroughput += float(elems[1])
            elems = outputLines[1].split(":")
            totLatency += float(elems[1])
        avgLatency = totLatency / numClientMachines
    except Exception:
        totThroughput = -1
        avgLatency = -1

    # Kill replicas and sequencer.
    for process in processes :
        process.terminate()

    for t in timers:
        t.cancel()

    seqThroughput = 0
    if protocol == "nopaxos":
        tempFile.seek(0)
	print("tempFile",tempFile)
	lines = tempFile.readlines()
	print("lines", lines)
        start = float(lines[0])
	print("start time", start)
        end = float(lines[len(lines) - 1])
	print("end time", end)
        elapsed = end - start
	if elapsed != 0:
        	seqThroughput = numClientMachines * numThreadsPerClient * 1000.0 / elapsed


    print("")
    print("******************************************************************")
    print((("Finished running %s with %d replicas with %d client machines each running %d threads") % (protocol, numReplicas, numClientMachines, numThreadsPerClient)))
    print((("Total throughput (requests/sec): %d") % (totThroughput)))
    print((("Average latency (us): %d") % (avgLatency)))
    if protocol == "nopaxos":
        print(("Sequencer Throughput is %f" % seqThroughput))
    return totThroughput, avgLatency, seqThroughput
